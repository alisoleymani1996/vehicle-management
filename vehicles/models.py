from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator

class Person(models.Model):
    
    name = models.CharField(max_length=100)
    national_code = models.CharField(max_length=10, unique=True)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18)])


    def __str__(self):
        return self.name


class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('small', 'Light Vehicle'),
        ('big', 'Heavy Vehicle'),
    ]
    
    owner = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='vehicles')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    color = models.CharField(max_length=10, choices=[
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('black', 'Black'),
        ('white', 'White'),
    ])
    length = models.FloatField(validators=[MinValueValidator(1.0)])
    load_volume = models.FloatField(null=True, blank=True)  # Only for heavy vehicles

    def calculate_toll(self):
        """Calculate toll dynamically based on vehicle type."""
        if self.type == 'big' and self.load_volume:
            return self.load_volume * 300
        return 0  # No toll for light vehicles

    def __str__(self):
        return f"{self.owner.name}'s {self.get_type_display()} ({self.color})"

class Road(models.Model):
    
    name = models.CharField(max_length=100, null=True, blank=True)
    width = models.FloatField(validators=[MinValueValidator(1.0)])  
    geom = gis_models.MultiLineStringField(srid=4326)

    def is_heavy_vehicle_allowed(self):
        
        return self.width > 20

    def __str__(self):
        return f"{self.name} (Width: {self.width} m)"


class TollStation(models.Model):
    
    name = models.CharField(max_length=100, null=True, blank=True)
    location = gis_models.PointField()
    fixed_toll = models.IntegerField(default=5000) 

    def __str__(self):
        return self.name if self.name else "Unnamed Toll Station"
