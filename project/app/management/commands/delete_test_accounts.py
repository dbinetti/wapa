from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Q

User = apps.get_model("app", "User")


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(
            Q(email__endswith='westadaparents.com') |
            Q(email__endswith='tfbnw.net')
        )
        count = users.count()
        for user in users:
            user.delete()
        self.stdout.write(f"{count} Test Accounts Deleted.")
        return
