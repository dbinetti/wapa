import datetime
import json
import logging

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_fsm import TransitionNotAllowed

from .forms import AccountForm
from .forms import AttendeeForm
from .forms import CommentForm
from .forms import DeleteForm
from .forms import StoryForm
from .forms import StudentFormSet
from .models import Attendee
from .models import Comment
from .models import Event
from .models import Issue
from .tasks import send_verification_email

log = logging.getLogger(__name__)


# Root
def index(request):
    issue = Issue.objects.get(state=Issue.STATE.active)
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
        if not getattr(user, 'is_verified', None):
            return redirect('verify')
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
    issue = Issue.objects.get(
        state=Issue.STATE.active,
    )
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
            account = form.save(commit=False)
            account.address_raw = str(form.cleaned_data['address'])
            account.save()
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
                    mark_safe("Next, please send a comment to the Superintendent!"),
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
        },
    )

@login_required
def delete(request):
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()
            messages.error(
                request,
                "Account Deleted!",
            )
            return redirect('index')
    else:
        form = DeleteForm()
    return render(
        request,
        'pages/delete.html',
        {'form': form,},
    )

@login_required
def story(request):
    account = request.user.account
    if request.POST:
        form = StoryForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                mark_safe("Saved!"),
            )
            return redirect('story')
    else:
        form = StoryForm(instance=account)

    return render(
        request,
        'pages/story.html',
        context={
            'form': form,
        },
    )

@login_required
def comments(request):
    account = request.user.account
    issue = Issue.objects.get(state=Issue.STATE.active)
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
            comment.save()
            if comment.state == Comment.STATE.approved:
                messages.success(
                    request,
                    'Comment Sent to Superintendent Bub!',
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
        form = DeleteForm(request.POST)
        if form.is_valid():
            comment.delete()
            messages.error(
                request,
                "Comment Deleted!",
            )
            return redirect('comments')
    else:
        form = DeleteForm()
    return render(
        request,
        'pages/comment_delete.html',
        context = {
            'form': form,
            'comment': comment,
        },
    )

@login_required
def story_delete(request):
    account = request.user.account
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            account.story = ''
            account.save()
            messages.error(
                request,
                "Story Deleted!",
            )
            return redirect('story')
    else:
        form = DeleteForm()
    return render(
        request,
        'pages/story_delete.html',
        context = {
            'form': form,
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

@login_required
def events(request):
    events = Event.objects.filter(
    ).order_by(
        'date',
    )
    if events.count() == 1:
        event = events.first()
        return redirect(
            'event',
            event.id,
        )
    return render(
        request,
        'pages/events.html',
        context = {
            'events': events,
        }
    )

@login_required
def event(request, event_id):
    event = get_object_or_404(
        Event,
        pk=event_id,
    )
    attendees = event.attendees.filter(
        is_confirmed=True,
        account__is_public=True,
    ).order_by(
        '-created',
    )
    try:
        attendee = event.attendees.get(account=request.user.account)
    except Attendee.DoesNotExist:
        attendee = None
    if request.method == 'POST':
        form = AttendeeForm(request.POST, instance=attendee)
        if form.is_valid():
            attendee = form.save(commit=False)
            attendee.account = request.user.account
            attendee.event = event
            attendee.save()
            messages.success(
                request,
                'Saved!',
            )
            return redirect('event', event_id)
    form = AttendeeForm(instance=attendee)
    return render(
        request,
        'pages/event.html',
        context = {
            'event': event,
            'attendees': attendees,
            'form': form,
        }
    )
