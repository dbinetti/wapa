# Generated by Django 3.2.7 on 2021-09-16 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0060_auto_20210916_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='geocode',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
