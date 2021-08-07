# Generated by Django 3.2.6 on 2021-08-07 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_school_full'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='grade',
            field=models.IntegerField(choices=[(-1, 'Pre-K'), (0, 'Kindergarten'), (1, 'First Grade'), (2, 'Second Grade'), (3, 'Third Grade'), (4, 'Fourth Grade'), (5, 'Fifth Grade'), (6, 'Sixth Grade'), (7, 'Seventh Grade'), (8, 'Eighth Grade'), (9, 'Ninth Grade'), (10, 'Tenth Grade'), (11, 'Eleventh Grade'), (12, 'Twelfth Grade')], default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
