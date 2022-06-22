import json

from app.exporters import export_school
from app.exporters import export_schools
from django.apps import apps
from django.core.cache import cache
from django.core.management.base import BaseCommand

School = apps.get_model("app", "School")


class Command(BaseCommand):
    def handle(self, *args, **options):
        kinds = [
            'elementary',
            'middle',
            'high',
        ]
        for kind in kinds:
            schools = School.objects.filter(
                is_traditional=True,
                kind=getattr(School.KIND, kind),
            )
            json_object = export_schools(schools)
            with open(f'{kind}.geojson', 'w') as file:
                json_string = json.dumps(json_object)
                file.write(json_string)
        return
