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

from .forms import AccountForm
from .forms import AttendeeForm
from .forms import CommentForm
from .forms import DeleteForm
from .forms import StudentFormSet
from .models import Account
from .models import Attendee
from .models import Comment
from .models import Event
from .models import Issue
from .models import Student

log = logging.getLogger(__name__)


# Root
def index(request):
    issue = Issue.objects.latest('date')
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
    count = sum([
        Account.objects.all().count(),
        Account.objects.filter(is_spouse=True).count(),
    ])
    return render(
        request,
        'app/pages/index.html',
        context = {
            'comments': comments,
            'count': count,
        },
    )

# Authentication
def join(request):
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
        'initScreen': 'signUp',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)

def login(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    next_url = request.GET.get('next', '/comments')
    state = f"{get_random_string()}|{next_url}"
    request.session['state'] = state
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'redirect_uri': redirect_uri,
        'initScreen': 'login',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)

def verify(request):
    return render(
        request,
        'app/pages/verify.html',
        context={
        },
    )

def verified(request):
    messages.success(
        request,
        "Thank you -- your account has been verified!",
    )
    return redirect('account')


def callback(request):
    # Reject if state doesn't match
    browser_state = request.session.get('state')
    server_state = request.GET.get('state')
    if browser_state != server_state:
        log.error("state mismatch")
        return HttpResponse(status=400)
    next_url = server_state.partition('|')[2]
    # Get Auth0 Code
    code = request.GET.get('code', None)
    if not code:
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
    if not getattr(user, 'is_active', None):
        return redirect('verify')
    if user:
        log_in(request, user)
        # Check if first-time login and redirect to account page
        if (user.last_login - user.created) < datetime.timedelta(minutes=1):
            messages.success(
                request,
                "Welcome and thanks for your support!"
            )
            messages.warning(
                request,
                "Next, review the below and click 'Save'."
            )
            return redirect('account')
        # Otherwise, redirect to next_url
        return redirect(next_url)
    log.error("no user")
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
    comments = account.comments.all()
    attendees = account.attendees.all()
    metrics = {}
    metrics['members'] = sum([
        Account.objects.all().count(),
        Account.objects.filter(is_spouse=True).count(),
    ])
    metrics['comments'] = Comment.objects.all(
    ).count()
    metrics['events'] = Attendee.objects.filter(
        is_confirmed=True,
    ).count()
    metrics['schools'] = Student.objects.values(
        'school',
    ).distinct(
    ).count()
    metrics['students'] = Student.objects.all(
    ).count()
    return render(
        request,
        'app/pages/dashboard.html',
        context={
            'account': account,
            'metrics': metrics,
            'comments': comments,
            # 'shares': shares,
            'attendees': attendees,
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
    if request.POST:
        form = AccountForm(request.POST, instance=account)
        formset = StudentFormSet(request.POST, request.FILES, instance=account)
        if form.is_valid() and formset.is_valid():
            account = form.save()
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
                if account.comments.count() == 0:
                    messages.warning(
                        request,
                        mark_safe("Next, please send a comment to the Superintendent!"),
                    )
                    return redirect('comments')
                else:
                    return redirect('account')
            else:
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
        'app/pages/account.html',
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
        'app/pages/delete.html',
        {'form': form,},
    )


@login_required
def comments(request):
    account = request.user.account
    issue = Issue.objects.get(state=10)
    comment = account.comments.filter(issue=issue).first()
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.account = account
            comment.issue = issue
            if account.user.is_verified:
                comment.approve()
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
        'app/pages/comments.html',
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
        raise PermissionDenied("You can not delete others' comments")
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
        'app/pages/comment_delete.html',
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
        'app/pages/events.html',
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
        'app/pages/event.html',
        context = {
            'event': event,
            'attendees': attendees,
            'form': form,
        }
    )

def comment(request, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
    )
    count = sum([
        Account.objects.all().count(),
        Account.objects.filter(is_spouse=True).count(),
    ])
    return render(
        request,
        'app/pages/comment.html',
        context = {
            'comment': comment,
            'count': count,
        }
    )

@login_required
def share(request):
    return render(
        request,
        'app/pages/share.html',
    )
