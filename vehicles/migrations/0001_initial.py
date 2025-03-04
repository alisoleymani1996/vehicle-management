# Generated by Django 4.2 on 2025-02-18 06:54

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('national_code', models.CharField(max_length=10, unique=True)),
                ('age', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(18)])),
            ],
        ),
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('width', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0)])),
                ('geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=43226)),
            ],
        ),
        migrations.CreateModel(
            name='TollStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('fixed_toll', models.IntegerField(default=5000)),
            ],
        ),
        migrations.CreateModel(
            name='LightVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(choices=[('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('black', 'Black'), ('white', 'White')], max_length=10)),
                ('length', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0)])),
                ('model_name', models.CharField(max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='light_vehicles', to='vehicles.person')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HeavyVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(choices=[('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('black', 'Black'), ('white', 'White')], max_length=10)),
                ('length', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0)])),
                ('max_load_weight', models.FloatField(validators=[django.core.validators.MinValueValidator(1.0)])),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heavy_vehicle', to='vehicles.person')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
