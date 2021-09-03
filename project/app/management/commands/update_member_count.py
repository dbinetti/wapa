from django.apps import apps
from django.core.cache import cache
from django.core.management.base import BaseCommand

Account = apps.get_model("app", "Account")


class Command(BaseCommand):
    def handle(self, *args, **options):
        count = sum([
            Account.objects.all().count(),
            Account.objects.filter(is_spouse=True).count(),
        ])
        cache.set('member_count', count)
        return
