import datetime
import logging

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

from .forms import AccountForm
from .forms import DeleteForm
from .forms import StudentForm
from .models import Student
from .tasks import get_auth0_data

log = logging.getLogger(__name__)

# Verified Email
def is_verified(user):
    return user.data.get('email_verified', False) if user.data else False


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
    email = request.user.email
    return render(
        request,
        'app/pages/verify.html',
        context={
            'email': email,
        },
    )

def verified(request):
    # try:
    #     data = get_auth0_data(request.user.username)
    # except Exception as e:
    #     log.error(e)
    #     messages.error(
    #         request,
    #         mark_safe("Your account couldn't be verified; please try again or contact <a href='mailto:support@westadaparents.com'>support@westadaparents.com</a>."),
    #     )
    #     return redirect('account')
    # email_verified = data.get('email_verified', False)
    # if email_verified:
    #     request.user.data = data
    #     request.user.save()
    #     request.user.refresh_from_db()
    messages.success(
        request,
        "Thank you -- your account has been verified!",
    )
    return redirect('account')
    # messages.error(
    #     request,
    #     "Your account couldn't be verified; please try again or contact support.",
    # )
    # return redirect('verify')

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
            "Email address is required",
        )
        return redirect('logout')
    user = authenticate(request, **payload)

    if user and user.is_active == False:
       messages.warning(request, 'Please Confirm Your Email', extra_tags="")
       return redirect('verify')
    if user:
        log_in(request, user)
        if user.is_admin:
            return redirect('admin:index')
        if (user.last_login - user.created) < datetime.timedelta(minutes=1):
            messages.success(
                request,
                "Thanks for joining the West Ada Parents Association!  We'll be sending more updates soon; for now, please update your account information below."
            )
            return redirect('account')
        return redirect(next_url)
    return HttpResponse(status=403)

def logout(request):
    log_out(request)
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'return_to': request.build_absolute_uri(reverse('goodbye')),
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

def goodbye(request):
    return render(
        request,
        'app/pages/goodbye.html',
        context={
        },
    )

# Account
# @user_passes_test(is_verified, login_url='verify')
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
                "Saved!",
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
