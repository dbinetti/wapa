# Standard Libary
import csv
import json
import logging

import cloudinary
import geocoder
import posthog
import pydf
# First-Party
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
# Django
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_rq import job
from mailchimp3 import MailChimp
from mailchimp3.helpers import get_subscriber_hash
from mailchimp3.mailchimpclient import MailChimpError
from scourgify import normalize_address_record
from scourgify.exceptions import UnParseableAddressError

from .models import Account
from .models import School
from .models import Zone

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

def get_auth0_data(user_id):
    client = get_auth0_client()
    data = client.users.get(user_id)
    return data

@job
def delete_auth0_from_user(user):
    client = get_auth0_client()
    response = client.users.delete(user.username)
    return response


@job
def update_user_from_auth0(user):
    data = get_auth0_data(user.username)
    user.name = data.get('name')
    user.email = data.get('email')
    user.is_verified = data.get('email_verified')
    user.data = data
    user = user.save()
    return user


@job
def send_verification_email(user):
    client = get_auth0_client()
    response = client.jobs.send_verification_email({
        'user_id': user.username,
    })
    return response


# Account Creation Utility
def create_account_from_user(user):
    account = Account.objects.create(
        user=user,
        name=user.name,
    )
    try:
        file = user.data.get('picture', None)
    except AttributeError:
        file = None
    if file:
        try:
            picture = cloudinary.uploader.unsigned_upload(
                file,
                'picture',
                folder=f'{settings.CLOUDINARY_PREFIX}/pictures/',
                public_id=str(user.account.id),
                resource_type='image',
            )
        except Exception as e:
            log.error(e)
            return account
        account.picture.name = picture['public_id']
        account.save()
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
    subscriber_hash = get_subscriber_hash(user.email)
    data = {
        'status_if_new': 'subscribed',
        'email_address': user.email,
        'merge_fields': {
            'NAME': user.account.name,
        }
    }
    try:
        result = client.lists.members.create_or_update(
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
    return result

@job
def delete_mailchimp_from_email(email):
    client = get_mailchimp_client()
    subscriber_hash = get_subscriber_hash(email)
    client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
    try:
        client.lists.members.delete(
            list_id=settings.MAILCHIMP_AUDIENCE_ID,
            subscriber_hash=subscriber_hash,
        )
    except MailChimpError as err:
        # Skip if already deleted
        error = json.loads(str(err).replace("\'", "\""))
        if error['title'] == 'Resource Not Found':
            log.error(err)
            return
        if error['title'] == 'Method Not Allowed':
            raise err
        # else raise err
        raise err


# Utility
def build_email(template, subject, from_email='David Binetti (WAPA) <dbinetti@westadaparents.com>', context=None, to=[], cc=[], bcc=[], attachments=[], html_content=None):
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
        str(user.username), {
            'name': user.name,
            'email': user.email,
        }
    )
    return

@job
def alias_posthog_from_user(user, distinct_id):
    posthog.alias(
        distinct_id,
        str(user.username),
    )
    return

@job
def send_denial_email(account):
    # comments = account.comments
    email = build_email(
        template='emails/denied.txt',
        subject='Comment Denied',
        # context={'comments': comments},
        to=[account.user.email],
    )
    return email.send()

@job
def send_approval_email(account):
    # comments = account.comments
    email = build_email(
        template='emails/approved.txt',
        subject='Comment Approved!',
        # context={'comments': comments},
        to=[account.user.email],
    )
    return email.send()


@job
def send_super_email(comment):
    account = comment.account
    from_email = f"{account.name} (WAPA) <{account.id}@westadaparents.com>"
    email = build_email(
        template='emails/comment.txt',
        subject=f'{comment.issue.name}',
        context={
            'comment': comment,
            'account': account,
        },
        from_email=from_email,
        to=comment.issue.recipient_emails,
        cc=[account.user.email],
    )
    return email.send()

def denorm_students(account):
    schools = School.objects.filter(
        students__account=account
    ).order_by(
        'kind',
    ).distinct()
    output = []
    mapping = {
        -1: 'PK',
        0: 'K',
        1: '1st',
        2: '2nd',
        3: '3rd',
        4: '4th',
        5: '5th',
        6: '6th',
        7: '7th',
        8: '8th',
        9: '9th',
        10: '10th',
        11: '11th',
        12: '12th',
    }
    for school in schools:
        grades = school.students.filter(
            account=account,
        ).values_list('grade', flat=True)
        try:
            listed = ", ".join([mapping[x] for x in grades])
        except KeyError:
            continue
        flat = f'{school.name} {listed}'
        output.append(flat)
    account.output = output


@job
def send_review_from_account(account):
    from_email = "David Binetti (WAPA) <dbinetti@westadaparents.com>"
    need_student = bool(account.students.count())
    need_address = bool(account.address)
    students_raw = account.students.order_by(
        'school__kind',
        'school__name',
        'grade',
    )
    students_comp = [f"{x.school.name} {x.get_grade_display()}" for x in students_raw]
    students = "; ".join(list(students_comp))
    email = build_email(
        template='emails/review.txt',
        subject='Administrative Request: Account Review',
        context={
            'account': account,
            'need_student': need_student,
            'need_address': need_address,
            'students': students,
        },
        from_email=from_email,
        to=[f'{account.name} <{account.user.email}>'],
    )
    return email.send()



def get_letter_from_comment(comment):
    context={
        'comment': comment,
    }
    rendered = render_to_string('app/pdfs/letter.html', context)
    pdf = pydf.generate_pdf(
        rendered,
        enable_smart_shrinking=False,
        orientation='Portrait',
        margin_top='10mm',
        margin_bottom='10mm',
    )
    return pdf

def merge_letter_from_comments(comments):
    output = ''
    for comment in comments:
        context={
            'comment': comment,
        }
        rendered = render_to_string('app/pdfs/letter.html', context)
        output += rendered
    pdf = pydf.generate_pdf(
        output,
        enable_smart_shrinking=False,
        orientation='Portrait',
        margin_top='10mm',
        margin_bottom='10mm',
        margin_right='20mm',
        margin_left='20mm',
    )
    return pdf

@job
def normalize_address(account):
    try:
        address = normalize_address_record(str(account.address))
    except UnParseableAddressError as e:
        log.error(e)
        return
    address_json = json.dumps(address)
    account.address_json = address_json
    account.save()
    return

@job
def update_address_from_account(account):
    if not account.address:
        return
    account.address_raw = str(account.address)
    account.save()
    return

@job
def update_point_from_account(account):
    if not account.address:
        return
    try:
        account.address.longitude
        account.address.latitude
    except KeyError:
        log.error(f'{account.id} lon/lat')
        return
    point = Point(
        account.address.longitude,
        account.address.latitude,
    )
    account.point = point
    account.save()
    return

@job
def update_zone_from_account(account):
    if not account.point:
        return
    try:
        zone = Zone.objects.get(
            poly__contains=account.point,
        )
    except Zone.DoesNotExist:
        zone = Zone.objects.get(
            name='Not in District',
        )
    account.zone = zone
    account.save()
    return


@job
def geocode_account(account):
    result = geocoder.google(str(account.address))
    account.geocode = result.json
    account.save()
    return
