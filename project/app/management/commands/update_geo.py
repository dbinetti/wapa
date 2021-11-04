# from app.tasks import update_point_from_account
from app.tasks import geocode_account
from app.tasks import update_address_from_account
from app.tasks import update_zone_from_account
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Q

Account = apps.get_model("app", "Account")


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Set address raw for logging
        cs = Account.objects.filter(
            Q(address_raw='') | Q(address_raw='None'),
        ).exclude(
            address_too='',
        )
        csc = cs.count()
        for c in cs:
            update_address_from_account(c)
        self.stdout.write(f"Updated addresses: {csc}")


        # Geocode Account
        ts = Account.objects.exclude(
            address_too='',
        )
        tsc = ts.count()
        for t in ts:
            account = geocode_account(t)
            account.save()
        self.stdout.write(f"Geocoded Accounts: {tsc}")


        zs = Account.objects.filter(
            zone__isnull=False,
        ).exclude(
            address_too='',
        )
        zsc = zs.count()
        zs.update(zone=None)
        self.stdout.write(f"Zones scrubbed: {zsc}")


        ps = Account.objects.filter(
            point__isnull=False,
        ).exclude(
            address_too='',
        )
        psc = ps.count()
        ps.update(point=None)
        self.stdout.write(f"Points scrubbed: {psc}")

        self.stdout.write("Complete.")
        return
