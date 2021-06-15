# Standard Libary
import json
import logging

import posthog
# First-Party
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_rq import job
from mailchimp3 import MailChimp
from mailchimp3.helpers import get_subscriber_hash
from mailchimp3.mailchimpclient import MailChimpError

from .models import Account

log = logging.getLogger(__name__)

# Auth0
def get_auth0_token():
    get_token = GetToken(settings.AUTH0_TENANT)
    token = get_token.client_credentials(
        settings.AUTH0_CLIENT_ID,
        settings.AUTH0_CLIENT_SECRET,
        f'https://{settings.AUTH0_TENANT}/api/v2/',
    )
    return token

def get_auth0_client():
    token = get_auth0_token()
    client = Auth0(
        settings.AUTH0_TENANT,
        token['access_token'],
    )
    return client

def get_auth0_user(user_id):
    client = get_auth0_client()
    data = client.users.get(user_id)
    return data

@job
def delete_auth0_from_user(user):
    client = get_auth0_client()
    response = client.users.delete(user.username)
    return response


@job
def update_auth0_from_user(user):
    if not user.username.startswith('auth0|'):
        return
    client = get_auth0_client()
    payload = {
        'name': user.name,
        'email': user.email,
    }
    response = client.users.update(user.username, payload)
    return response


# Account Creation Utility
def create_account_from_user(user):
    account = Account.objects.create(
        user=user,
        name=user.name,
    )
    return account


# Mailchimp
def get_mailchimp_client():
    enabled = not settings.DEBUG
    return MailChimp(
        mc_api=settings.MAILCHIMP_API_KEY,
        enabled=enabled,
    )

@job
def create_or_update_mailchimp_from_user(user):
    client = get_mailchimp_client()
    list_id = settings.MAILCHIMP_AUDIENCE_ID
    email = user.email
    subscriber_hash = get_subscriber_hash(email)
    data = {
        'status_if_new': 'subscribed',
        'email_address': email,
    }
    try:
        client.lists.members.create_or_update(
            list_id=list_id,
            subscriber_hash=subscriber_hash,
            data=data,
        )
    except MailChimpError as err:
        # error = json.loads(str(e).replace("\'", "\""))
        # if error['title'] == 'Invalid Resource':
        #     user = User.objects.get(
        #         email=email,
        #     )
        #     user.is_active = False
        #     user.save()
        #     result = 'Invalid Resource'
        # else:
        #     raise e
        raise err
    return

@job
def delete_mailchimp_from_user(user):
    client = get_mailchimp_client()
    subscriber_hash = get_subscriber_hash(user.email)
    client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
    try:
        client.lists.members.delete(
            list_id=settings.MAILCHIMP_AUDIENCE_ID,
            subscriber_hash=subscriber_hash,
        )
    except MailChimpError as err:
        # Skip if does not exist
        error = json.loads(str(err).replace("\'", "\""))
        if not error['title'] == 'Method Not Allowed':
            # Otherwise, raise original error
            raise err
    return


# Utility
def build_email(template, subject, from_email, context=None, to=[], cc=[], bcc=[], attachments=[], html_content=None):
    body = render_to_string(template, context)
    if html_content:
        html_rendered = render_to_string(html_content, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
    )
    if html_content:
        email.attach_alternative(html_rendered, "text/html")
    for attachment in attachments:
        with attachment[1].open() as f:
            email.attach(attachment[0], f.read(), attachment[2])
    return email

@job
def send_email(email):
    return email.send()



@job
def create_or_update_posthog_from_user(user):
    payload = {
        'name': user.name,
        'email': user.email,
    }
    posthog.set(
        str(user.id),
        payload,
    )
    return


@job
def identify_posthog_from_user(user):
    posthog.identify(
        str(user.id)
    )
    return

@job
def alias_posthog_from_user(user, distinct_id):
    posthog.alias(
        distinct_id,
        str(user.id),
    )
    return
