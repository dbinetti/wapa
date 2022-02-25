import datetime
import json
import logging

import geocoder
import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_fsm import TransitionNotAllowed

from .forms import AccountForm
from .forms import CommentForm
from .forms import ConfirmForm
from .forms import SearchForm
from .forms import StudentFormSet
from .forms import ZoneForm
from .models import Comment
from .models import Issue
from .models import Zone
from .tasks import get_mailchimp_client
from .tasks import get_precision
from .tasks import link_account
from .tasks import send_verification_email
from .tasks import unlink_account

log = logging.getLogger(__name__)


# Root
def index(request):
    try:
        issue = Issue.objects.get(
            state=Issue.STATE.active,
        )
    except Issue.DoesNotExist:
        issue = None
    comments = Comment.objects.filter(
        account__is_public=True,
        state=Comment.STATE.approved,
        account__user__is_active=True,
        issue=issue,
    ).select_related(
        'account',
        'account__user',
    ).prefetch_related(
        'account__students',
        'account__students__school',
    ).order_by(
        '-created',
    )
    return render(
        request,
        'pages/index.html',
        context = {
            'comments': comments,
            'issue': issue,
        },
    )

# Authentication
def login(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    next_url = request.GET.get('next', '/account')
    state = f"{get_random_string()}|{next_url}"
    request.session['state'] = state
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'redirect_uri': redirect_uri,
        'screen_hint': 'signup',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)

def verify(request):
    email = request.user.email
    is_verified = request.user.is_verified
    if is_verified:
        return redirect('verified')
    return render(
        request,
        'pages/verify.html',
        context={
            'email': email,
        },
    )

def verified(request):
    messages.success(
        request,
        "Thank you -- your account has been verified!",
    )
    messages.warning(
        request,
        "Next, review the below and click 'Save'.  Then you can send comments."
    )
    return redirect('account')

def reverify(request):
    send_verification_email.delay(request.user)
    messages.success(
        request,
        "Verification email sent!",
    )
    return redirect('verify')

def callback(request):
    # Reject if state doesn't match
    browser_state = request.session.get('state')
    server_state = request.GET.get('state')
    if browser_state != server_state:
        del request.session['state']
        log.error('state mismatch')
        messages.error(
            request,
            "Sorry, there was a problem.  Please try again or contact support."
        )
        return redirect('index')
    next_url = server_state.partition('|')[2]
    # Get Auth0 Code
    code = request.GET.get('code', None)
    if not code:
        log.error('no code')
        return HttpResponse(status=400)
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    token = requests.post(
        token_url,
        json=token_payload,
    ).json()
    payload = jwt.decode(
        token['id_token'],
        options={
            'verify_signature': False,
        }
    )
    payload['username'] = payload.pop('sub')
    if not 'email' in payload:
        log.error("no email")
        messages.error(
            request,
            "Email address is required.  Please try again.",
        )
        return redirect('index')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        # if not getattr(user, 'is_verified', None):
        #     return redirect('verify')
        # Always redirect first-time users to account page
        if (user.last_login - user.created) < datetime.timedelta(minutes=1):
            messages.success(
                request,
                "Welcome and thanks for your support!"
            )
            messages.warning(
                request,
                "Next, review the below and click 'Save'.  Then you can send comments."
            )
            return redirect('account')
        # Otherwise, redirect to next_url, defaults to 'account'
        return redirect(next_url)
    log.error('callback fallout')
    return HttpResponse(status=403)

def logout(request):
    log_out(request)
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'return_to': request.build_absolute_uri(reverse('index')),
    }
    logout_url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/v2/logout',
        params=params,
    ).prepare().url
    messages.success(
        request,
        "You Have Been Logged Out!",
    )
    return redirect(logout_url)

# Dashboard
@login_required
def dashboard(request):
    account = request.user.account
    comments = account.comments.order_by(
        '-created',
    )
    try:
        issue = Issue.objects.get(
            state=Issue.STATE.active,
        )
    except Issue.DoesNotExist:
        issue = None
    is_current = comments.filter(
        issue=issue,
    )
    return render(
        request,
        'pages/dashboard.html',
        context={
            'account': account,
            'comments': comments,
            'issue': issue,
            'is_current': is_current,
        },
    )

# Account
@login_required
def account(request):
    try:
        issue = Issue.objects.get(
            state=Issue.STATE.active,
        )
    except Issue.DoesNotExist:
        issue = None
    account = request.user.account
    students = account.students.order_by(
        'grade',
        'name',
    )
    comments = account.comments.filter(
        issue__state=10,
    ).count()
    if request.POST:
        form = AccountForm(request.POST, instance=account)
        formset = StudentFormSet(request.POST, request.FILES, instance=account)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            for student_form in formset:
                if student_form.is_valid() and student_form.has_changed():
                    student_form.save()
            for obj in formset.deleted_objects:
                obj.delete()
            if account.is_public:
                messages.success(
                    request,
                    mark_safe("Saved!"),
                )
                if comments:
                    return redirect('account')
                messages.warning(
                    request,
                    mark_safe("Next, please send a comment."),
                )
                return redirect('comments')
            messages.success(
                request,
                mark_safe("Saved!"),
            )
            messages.warning(
                request,
                mark_safe("Please consider making your name Public so you can <a href='/comments'>make comments</a>."),
            )
            return redirect('account')
    else:
        form = AccountForm(instance=account)
        formset = StudentFormSet(instance=account)


    return render(
        request,
        'pages/account.html',
        context={
            'account': account,
            'form': form,
            'formset': formset,
            'students': students,
            'issue': issue,
        },
    )

@login_required
def delete(request):
    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()
            messages.error(
                request,
                "Account Deleted!",
            )
            return redirect('index')
    else:
        form = ConfirmForm()
    return render(
        request,
        'pages/delete.html',
        {'form': form,},
    )

@login_required
def comments(request):
    account = request.user.account
    try:
        issue = Issue.objects.get(
            state=Issue.STATE.active,
        )
    except Issue.DoesNotExist:
        issue = None
    comment = account.comments.filter(issue=issue).first()
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.account = account
            comment.issue = issue
            if account.user.is_verified:
                try:
                    comment.approve()
                except TransitionNotAllowed:
                    pass
            if comment.state == Comment.STATE.denied:
                comment.state = Comment.STATE.pending
            comment.save()
            if comment.state == Comment.STATE.approved:
                recipient_name = comment.issue.recipient_name if comment.issue.recipient_name else "Your Trustee"
                messages.success(
                    request,
                    f'Comment Sent to {recipient_name}!',
                )
            else:
                messages.success(
                    request,
                    'Saved!',
                )
            return redirect('comments')
    else:
        form = CommentForm(instance=comment)
    comments = Comment.objects.filter(
        account__is_public=True,
        state=Comment.STATE.approved,
        account__user__is_active=True,
        issue=issue,
    ).select_related(
        'account',
        'account__user',
    ).prefetch_related(
        'account__students',
        'account__students__school',
    ).order_by(
        # '-is_featured',
        '-created',
    )
    return render(
        request,
        'pages/comments.html',
        context={
            'comment': comment,
            'comments': comments,
            'account': account,
            'form': form,
            'issue': issue,
        },
    )

@login_required
def comment_delete(request, comment_id):
    try:
        comment = Comment.objects.get(
            id=comment_id,
            account=request.user.account,
        )
    except Comment.DoesNotExist:
        return PermissionDenied("You can not delete others' comments")
    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if form.is_valid():
            comment.delete()
            messages.error(
                request,
                "Comment Deleted!",
            )
            return redirect('comments')
    else:
        form = ConfirmForm()
    return render(
        request,
        'pages/comment_delete.html',
        context = {
            'form': form,
            'comment': comment,
        },
    )

@csrf_exempt
@require_POST
@login_required
def upload_picture(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        account = request.user.account
        account.picture.name = payload['public_id']
        account.save()
        messages.success(
            request,
            "Picture Saved!"
        )
    return HttpResponse()

@login_required
def delete_picture(request):
    account = request.user.account
    account.picture = "none"
    account.save()
    return redirect('account')


def updates(request):
    client = get_mailchimp_client()
    campaigns = client.campaigns.all(
        list_id=settings.MAILCHIMP_AUDIENCE_ID,
        sort_field='send_time',
        count=100,
    )['campaigns']
    updates = [x for x in campaigns if x['status'] == 'sent' and 'Re-sent' not in x['settings']['title']]
    updates.reverse()
    for u in updates:
        u['date'] = datetime.datetime.strptime(u['send_time'], '%Y-%m-%dT%H:%M:%S%z')
    return render(
        request,
        'pages/resources/updates/index.html',
        context = {
            'updates': updates,
        },
    )


@login_required
def search(request):
    form = SearchForm(request.POST or None)
    if form.is_valid():
        query = form.cleaned_data['query']
        url = f'{settings.VOTER_API_HOST}/search?q={query}'
        headers={
            'Authorization': f'Token {settings.VOTER_API_KEY}'
        }
        response = requests.get(
            url,
            headers=headers,
        ).json()
    else:
        response = None
    return render(
        request,
        'pages/search.html',
        context = {
            'form': form,
            'response': response,
        }
    )



@login_required
def confirm(request, voter_pk):
    account = request.user.account
    url = f'{settings.VOTER_API_HOST}/voter/{voter_pk}'
    headers={
        'Authorization': f'Token {settings.VOTER_API_KEY}'
    }
    response = requests.get(
        url,
        headers=headers,
    )
    voter_json = response.json()
    form = ConfirmForm(request.POST or None)
    if form.is_valid():
        messages.success(
            request,
            "Your voter registration status has been confirmed!",
        )
        account = link_account(account, voter_json)
        return redirect('account')
    return render(
        request,
        'pages/confirm.html',
        context = {
            'form': form,
            'voter': voter_json,
        },
    )

@login_required
def unlink(request):
    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if form.is_valid():
            account = request.user.account
            account = unlink_account(account)
            messages.error(
                request,
                "Voter Record Unlinked!",
            )
            return redirect('account')
    else:
        form = ConfirmForm()
    return render(
        request,
        'pages/unlink.html',
        {'form': form,},
    )
