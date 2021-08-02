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
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import AccountForm
from .forms import DeleteForm
from .forms import StudentForm
from .forms import WrittenCommentForm
from .models import Comment
from .models import Issue
from .models import SpokenComment
from .models import Student
from .models import WrittenComment

log = logging.getLogger(__name__)


# Root
def index(request):
    return render(
        request,
        'app/pages/index.html',
        context = {
        },
    )

# Authentication
def join(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    next_url = request.GET.get('next', 'account')
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
    next_url = request.GET.get('next', 'account')
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
        if user.is_admin:
            return redirect('admin:index')
        if (user.last_login - user.created) < datetime.timedelta(minutes=1):
            messages.success(
                request,
                "Thanks for joining the West Ada Parents Association!  Please update your account information below."
            )
            return redirect('account')
        if next_url != '/account':
            return redirect(next_url)
        if user.account.is_public:
            if user.account.comments.count == 0:
                messages.success(
                    request,
                    "Consider adding a public comment to give your voice more weight."
                )
            else:
                messages.success(
                    request,
                    "You can add or delete your public comments below."
                )
            return redirect('comments')
        messages.success(
            request,
            "Consider making your name public to encourage others to join."
        )
        return redirect('account')
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
        if form.is_valid():
            account = form.save()
            messages.success(
                request,
                mark_safe("Saved!  You can also <a href='/comments'>review and make public comments</a>."),
            )
            return redirect('account')
    else:
        form = AccountForm(instance=account)
    return render(
        request,
        'app/pages/account.html',
        context={
            'form': form,
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
def delete_student(request, student_id):
    try:
        student = Student.objects.get(
            id=student_id,
            account=request.user.account,
        )
    except Student.DoesNotExist:
        raise PermissionDenied("You can not delete another's student.")
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            student.delete()
            messages.error(
                request,
                "Student Deleted!",
            )
            return redirect('account')
    else:
        form = DeleteForm()
    return render(
        request,
        'app/pages/delete_student.html',
        context = {
            'form': form,
            'student': student,
        },
    )

@login_required
def add_student(request):
    account = request.user.account
    form = StudentForm(request.POST or None)
    if form.is_valid():
        student = form.save(commit=False)
        student.account = account
        student.save()
        messages.success(
            request,
            "Student Added!"
        )
        return redirect('account')
    return render(
        request,
        'app/pages/add_student.html',
        context = {
            'form': form,
        }
    )

@login_required
def edit_student(request, student_id):
    try:
        student = Student.objects.get(
            id=student_id,
            account=request.user.account,
        )
    except Student.DoesNotExist:
        raise PermissionDenied("You can not edit another's student.")
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student.save()
            messages.success(
                request,
                'Saved!',
            )
            return redirect('account')
    form = StudentForm(instance=student)
    return render(
        request,
        'app/pages/edit_student.html',
        context = {
            'form': form,
            'student': student,
        }
    )


@login_required
def comments(request):
    account = request.user.account
    issue = Issue.objects.latest('date')
    personals = account.comments.order_by(
        'created',
    )
    publics = Comment.objects.filter(
        account__is_public=True,
        state=Comment.STATE.approved,
        account__user__is_active=True,
        issue=issue,
    ).select_related(
        'account',
        'account__user',
    ).order_by(
        # '-is_featured',
        '-created',
    )
    return render(
        request,
        'app/pages/comments.html',
        context={
            'personals': personals,
            'publics': publics,
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


@login_required
def submit_spoken_comment(request):
    account = request.user.account
    if not account.is_public:
        messages.warning(
            request,
            "You must make your name Public to make a comment",
        )
        return redirect('account')
    return render(
        request,
        'app/pages/submit_spoken_comment.html',
    )

@csrf_exempt
@require_POST
@login_required
def video_submission(request):
    if request.method == 'POST':
        issue = Issue.objects.latest('date')
        payload = json.loads(request.body)
        comment = SpokenComment(
            account=request.user.account,
        )
        comment.video.name = payload['public_id']
        comment.issue = issue
        comment.save()
        messages.success(
            request,
            "Comment Submitted!  You'll receive an email once approved."
        )
    return HttpResponse()

@login_required
def submit_written_comment(request):
    account = request.user.account
    if not account.is_public:
        messages.warning(
            request,
            "You must make your name Public to make a comment",
        )
        return redirect('account')
    form = WrittenCommentForm(request.POST or None)
    if form.is_valid():
        issue = Issue.objects.latest('date')
        comment = form.save(commit=False)
        comment.account = account
        comment.issue = issue
        comment.save()
        messages.success(
            request,
            "Comment Submitted!  You'll receive an email once approved."
        )
        return redirect('comments')
    return render(
        request,
        'app/pages/submit_written_comment.html',
        context = {
            'form': form,
        }
    )
