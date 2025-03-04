from django.contrib import admin
from .models import Person, Vehicle, Road, TollStation

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'national_code', 'age')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'color', 'length', 'load_volume', 'owner')

@admin.register(Road)
class RoadAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'is_heavy_vehicle_allowed')

@admin.register(TollStation)
class TollStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'fixed_toll')
