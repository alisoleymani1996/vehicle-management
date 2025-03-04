from rest_framework import serializers
from .models import Person, Vehicle, TollStation, Road
from django.contrib.gis.geos import Point


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['name', 'national_code', 'age']


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.name')

    class Meta:
        model = Vehicle
        fields = ['id', 'type', 'color', 'length', 'load_volume', 'owner']


class TollStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TollStation
        fields = ['name', 'location', 'fixed_toll']


class RoadSerializer(serializers.ModelSerializer):
    geom = serializers.SerializerMethodField()

    class Meta:
        model = Road
        fields = ['name', 'width', 'geom']

    def get_geom(self, obj):
        return obj.geom.wkt or "Unnamed Road" # Convert geometry to WKT format
    
class VehicleLocationSerializer(serializers.Serializer):
    car = serializers.IntegerField()
    location = serializers.CharField()
    date = serializers.DateTimeField()

def validate_location(self, value):
    """
    Validates WKT format and converts it into a Point object.
    """
    try:
        srid, point_str = value.split(";")
        if srid.strip() != "SRID=4326":
            raise serializers.ValidationError("SRID must be 4326.")

        lon, lat = map(float, point_str.replace("POINT", "").strip(" ()").split())
        return Point(lon, lat, srid=4326) 
    except Exception:
        raise serializers.ValidationError("Invalid location format. Expected 'SRID=4326;POINT (lon lat)'")
 
