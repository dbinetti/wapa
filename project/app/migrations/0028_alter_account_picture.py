# Generated by Django 3.2.6 on 2021-08-08 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_alter_school_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='picture',
            field=models.ImageField(default='wapa/avatar', upload_to=''),
        ),
    ]
