from django.apps import apps
from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

Voter = apps.get_model("voterapi", "Voter")


class Command(BaseCommand):
    def handle(self, *args, **options):
        Voter.objects.update(
            search_vector=SearchVector(
                'name',
                'address',
            )
        )
        self.stdout.write("Voter model indexed.")
        return
