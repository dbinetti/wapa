# Generated by Django 3.2.7 on 2021-09-06 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_auto_20210906_0435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zone',
            name='poli',
        ),
    ]
