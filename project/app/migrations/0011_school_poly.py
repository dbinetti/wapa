# Generated by Django 4.0.5 on 2022-06-04 04:35

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_school_capacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='poly',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
    ]
