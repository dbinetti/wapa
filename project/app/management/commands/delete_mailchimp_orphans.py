from app.tasks import delete_mailchimp_from_email
from app.tasks import get_mailchimp_client
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

User = apps.get_model("app", "User")


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = get_mailchimp_client()
        members = client.lists.members.all(
            settings.MAILCHIMP_AUDIENCE_ID,
            get_all=True,
        )['members']
        for member in members:
            email = member['email_address']
            users = User.objects.filter(email=email)
            if not users:
                delete_mailchimp_from_email.delay(email)
