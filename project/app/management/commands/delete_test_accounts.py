from app.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(
            Q(email__endswith='tfbnw.net')
        )
        for user in users:
            user.delete()
        self.stdout.write("Complete.")
        return
