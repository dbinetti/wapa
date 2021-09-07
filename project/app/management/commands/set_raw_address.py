from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import F

Account = apps.get_model("app", "Account")
Zone = apps.get_model("app", "Zone")
Student = apps.get_model("app", "Student")

class Command(BaseCommand):
    def handle(self, *args, **options):
        cs = Account.objects.filter(
            address__isnull=False,
            address_raw='',
        )
        for c in cs:
            c.address_raw = str(c.address)
            c.save()
        return
