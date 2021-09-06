from django.apps import apps
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

Account = apps.get_model("app", "Account")
Zone = apps.get_model("app", "Zone")
Student = apps.get_model("app", "Student")

class Command(BaseCommand):
    def handle(self, *args, **options):
        cs = Account.objects.filter(
            point__isnull=True,
            address__latitude__isnull=False,
            address__longitude__isnull=False,
        )
        for c in cs:
            point = Point(
                c.address.longitude,
                c.address.latitude,
            )
            c.point = point
            c.save()
        return
