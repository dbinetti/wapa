from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import User
from .tasks import create_account_from_user
from .tasks import create_or_update_mailchimp_from_user
from .tasks import delete_auth0_user
from .tasks import delete_mailchimp_from_user
from .tasks import update_auth0_from_user


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        create_account_from_user(instance)
    else:
        update_auth0_from_user.delay(instance)
    create_or_update_mailchimp_from_user.delay(instance)
    return

@receiver(pre_delete, sender=User)
def user_pre_delete(sender, instance, **kwargs):
    delete_auth0_user(instance.username)
    delete_mailchimp_from_account(instance)
    return
