# Generated by Django 3.2.6 on 2021-08-02 12:39

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_comment_issue'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='state',
            field=django_fsm.FSMIntegerField(choices=[(-5, 'Archived'), (0, 'Pending'), (10, 'Active')], default=0),
        ),
    ]
