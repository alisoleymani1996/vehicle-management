from django.shortcuts import render
from django.http import JsonResponse
from .models import Road, TollStation, Person, Vehicle
from .serializers import PersonSerializer, VehicleSerializer, VehicleLocationSerializer
import json
from django.contrib.gis.geos import MultiLineString, LineString
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models


class RedBlueVehiclesView(APIView):
    def get(self, request):
        red_blue_colors = ['red', 'blue']
        light_vehicles = Vehicle.objects.filter(type='small', color__in=red_blue_colors)
        heavy_vehicles = Vehicle.objects.filter(type='big', color__in=red_blue_colors)

        light_serializer = VehicleSerializer(light_vehicles, many=True)
        heavy_serializer = VehicleSerializer(heavy_vehicles, many=True)

        return Response({
            'light_vehicles': light_serializer.data,
            'heavy_vehicles': heavy_serializer.data
        })


class RegisterUserAndVehicleView(APIView):
    def post(self, request):
        person_data = request.data.get('person')
        vehicle_data = request.data.get('vehicle')

        # Create Person
        person_serializer = PersonSerializer(data=person_data)
        if person_serializer.is_valid():
            person = person_serializer.save()
        else:
            return Response(person_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create Vehicle
        vehicle_data['owner'] = person.id
        vehicle_serializer = VehicleSerializer(data=vehicle_data)

        if vehicle_serializer.is_valid():
            vehicle_serializer.save()
            return Response({'message': 'User and vehicle registered successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(vehicle_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OldOwnersVehiclesView(APIView):
    def get(self, request):
        old_people = Person.objects.filter(age__gt=70)
        vehicles = Vehicle.objects.filter(owner__in=old_people)

        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


class HeavyVehiclesOnNarrowRoadsView(APIView):
    def post(self, request):
        serializer = VehicleLocationSerializer(data=request.data, many=True)  # Validate multiple records
        
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        heavy_vehicle_ids = set(
            Vehicle.objects.filter(type='big').values_list('id', flat=True)
        )
        violating_vehicles = []

        for record in serializer.validated_data:
            vehicle_id = record["car"]
            vehicle_point = record["location"]  
            record_date = record["date"]

            # Skip non-heavy vehicles
            if vehicle_id not in heavy_vehicle_ids:
                continue

            # Check for narrow roads
            nearby_roads = Road.objects.filter(geom__intersects=vehicle_point, width__lt=20)
            
            if nearby_roads.exists():
                violating_vehicles.append({
                    "vehicle_id": vehicle_id,
                    "location": vehicle_point,
                    "date": record_date,
                    "violated_roads": [
                        {"road_name": road.name, "width": road.width} for road in nearby_roads
                    ]
                })

        return Response({"violating_vehicles": violating_vehicles}, status=status.HTTP_200_OK)
    
class TollCalculationView(APIView):
    def get(self, request, vehicle_id, start_date, end_date):
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            crossings = Crossing.objects.filter(
                vehicle_id=vehicle_id, 
                date__range=[start_date, end_date]
            )
            
            toll_per_cross = 300 * vehicle.load_volume if vehicle.type == 'big' else 0
            total_toll = toll_per_cross * crossings.count()

            return Response({
                'vehicle_id': vehicle_id,
                'owner': vehicle.owner.name,  # Assuming Vehicle has an owner field
                'total_toll': total_toll,
                'crossings_count': crossings.count(),
                'period': {'start_date': start_date, 'end_date': end_date}
            })
        
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)


class NearbySmallVehiclesView(APIView):
    def post(self, request):
        # Validate input data with the serializer
        serializer = VehicleLocationSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Find "عوارضی 1" toll station
        try:
            toll_station = TollStation.objects.get(name="عوارضی 1")
        except TollStation.DoesNotExist:
            return Response({"error": "Toll station not found"}, status=status.HTTP_404_NOT_FOUND)

        toll_location = toll_station.location

        small_vehicle_ids = set(Vehicle.objects.filter(type="small").values_list("id", flat=True))

        nearby_vehicles = []

        for record in serializer.validated_data:
            vehicle_id = record["car"]
            vehicle_point = record["location"]  # Already parsed as Point
            record_date = record["date"]

            # Skip if vehicle is not small
            if vehicle_id not in small_vehicle_ids:
                continue

            # Calculate distance
            #distance = toll_location.distance(vehicle_point)
            distance = toll_location.transform(4326, clone=True).distance(vehicle_point)

            nearby_vehicles.append({
                "vehicle_id": vehicle_id,
                "location": f"POINT ({vehicle_point.x} {vehicle_point.y})",
                "date": record_date,
                "distance_meters": round(distance, 2)
            })

        return Response({"nearby_small_vehicles": nearby_vehicles}, status=status.HTTP_200_OK)


class ViolationOwnersView(APIView):
    def get(self, request):
        owners = Person.objects.annotate(total_violations=models.Sum('vehicles__toll_paid')).order_by('-total_violations')
        serializer = PersonSerializer(owners, many=True)
        return Response(serializer.data)


def import_roads(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        
        try:
            data = json.load(json_file)  # Load JSON data
            
            roads_to_create = []
            for item in data:
                name = item.get('name', None)  # Handle null names
                width = item.get('width', 1.0)  # Default width if missing

                if not item.get('geom'):
                    continue  # Skip records without geometry

                # Extract WKT geometry
                wkt_geom = item['geom'].split(';')[1]
                wkt_geom = wkt_geom.replace('MULTILINESTRING ', '').strip('()')

                # Parse coordinates correctly
                line_strings = []
                for line in wkt_geom.split('),('):  
                    coordinates = [tuple(map(float, pair.split())) for pair in line.strip().split(',')]
                    line_strings.append(LineString(coordinates))

                # Convert to MultiLineString
                geom = MultiLineString(line_strings)

                # Create Road object (but don't save yet)
                roads_to_create.append(Road(name=name, width=width, geom=geom))

            # Bulk create all roads at once (faster)
            Road.objects.bulk_create(roads_to_create)

            return JsonResponse({'message': 'Roads imported successfully!'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'roads/upload_form.html')


def import_toll_stations(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        
        try:
            data = json.load(json_file)  # Load JSON file
            
            tolls_to_create = []
            for item in data:
                name = item.get('name', None)  # Handle null names
                fixed_toll = item.get('toll_per_cross', 5000)  # Default value if missing

                # Extract and parse WKT location
                if not item.get('location'):
                    continue  # Skip records without location

                wkt_location = item['location'].split(';')[1].strip('POINT').replace('(', '').replace(')', '')
                coordinates =  wkt_location.split()
                lon, lat = map(float, coordinates)

                # Create TollStation object (without saving yet)
                tolls_to_create.append(TollStation(name=name, fixed_toll=fixed_toll, location=Point(lon, lat)))

            # Bulk create for better performance
            TollStation.objects.bulk_create(tolls_to_create)

            return JsonResponse({'message': 'Toll stations imported successfully!'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'toll/upload_toll_form.html')  # Render the upload form


def import_owners(request):
    if request.method == "POST" and request.FILES.get("json_file"):
        json_file = request.FILES["json_file"]
        try:
            data = json.load(json_file)

            for person_data in data:
                national_code_str = str(person_data["national_code"])
                person, _ = Person.objects.get_or_create(
                    national_code=national_code_str,
                    defaults={"name": person_data["name"], "age": person_data["age"]}
                )

                for car_data in person_data.get("ownerCar", []):
                    if car_data["type"] == "small":
                        Vehicle.objects.create(
                            owner=person,
                            type="small",  # You can change this as needed
                            color=car_data["color"],
                            length=car_data["length"],
                            # Add any other fields specific to light vehicles
                        )
                    elif car_data["type"] == "big":
                        Vehicle.objects.create(
                            owner=person,
                            type="big",  # You can change this as needed
                            color=car_data["color"],
                            length=car_data["length"],
                            load_volume=car_data.get("load_volume", 0)  # For heavy vehicles
                        )

            return JsonResponse({"message": "Owners and vehicles imported successfully."}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'owners/upload_owners_form.html')
