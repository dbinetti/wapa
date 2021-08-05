import json
import logging
import urllib

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import User
from .tasks import alias_posthog_from_user
from .tasks import create_account_from_user
from .tasks import create_or_update_mailchimp_from_user
from .tasks import create_or_update_posthog_from_user
from .tasks import delete_auth0_from_user
from .tasks import delete_mailchimp_from_user
from .tasks import identify_posthog_from_user
from .tasks import update_user_from_auth0

log = logging.getLogger(__name__)



@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        create_account_from_user(instance)
    create_or_update_mailchimp_from_user.delay(instance)
    # create_or_update_posthog_from_user.delay(instance)
    return

@receiver(pre_delete, sender=User)
def user_pre_delete(sender, instance, **kwargs):
    delete_auth0_from_user.delay(instance)
    delete_mailchimp_from_user.delay(instance)
    return


# @receiver(user_logged_in)
# def user_logged_in(sender, request, user, **kwargs):
#     update_user_from_auth0.delay(user)
#     identify_posthog_from_user.delay(user)
#     encoded = request.COOKIES.get(f'ph_{settings.POSTHOG_API_KEY}_posthog', None)
#     if encoded:
#         distinct_id = json.loads(urllib.parse.unquote(encoded))['distinct_id']
#         alias_posthog_from_user.delay(user, distinct_id)
#     else:
#         log.error(f'Posthog: {user}')
#     return
