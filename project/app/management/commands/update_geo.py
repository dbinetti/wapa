from app.tasks import update_address_from_account
from app.tasks import update_point_from_account
from app.tasks import update_zone_from_account
from django.apps import apps
from django.core.management.base import BaseCommand

Account = apps.get_model("app", "Account")


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Set address raw for logging
        cs = Account.objects.filter(
            address__isnull=False,
            address_raw='',
        )
        csc = cs.count()
        for c in cs:
            update_address_from_account(c)
        self.stdout.write(f"Updated addresses: {csc}")


        # Set point when there are addresses
        ts = Account.objects.filter(
            point__isnull=True,
            address__latitude__isnull=False,
            address__longitude__isnull=False,
        )
        tsc = ts.count()
        for t in ts:
            update_point_from_account(t)
        self.stdout.write(f"Updated points: {tsc}")


        # Set zone when missing
        fs = Account.objects.filter(
            zone__isnull=True,
            point__isnull=False,
        )
        fsc = fs.count()
        for f in fs:
            update_zone_from_account(f)
        self.stdout.write(f"Updated zones: {fsc}")


        zs = Account.objects.filter(
            address__isnull=True,
            zone__isnull=False,
        )
        zsc = zs.count()
        zs.update(zone=None)
        self.stdout.write(f"Zones scrubbed: {zsc}")


        ps = Account.objects.filter(
            address__isnull=True,
            point__isnull=False,
        )
        psc = ps.count()
        ps.update(point=None)
        self.stdout.write(f"Points scrubbed: {psc}")

        self.stdout.write("Complete.")
        return
