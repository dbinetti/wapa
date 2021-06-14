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
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string

from .forms import AccountForm
from .forms import DeleteForm

log = logging.getLogger(__name__)

# Verified Email
def is_verified(user):
    return user.data['email_verified']

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
    next_url = request.GET.get('next', '/account')
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
    log.info(payload)
    if not 'email' in payload:
        messages.error(
            request,
            "Email address is required",
        )
        return redirect('logout')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        if user.is_admin:
            return redirect('admin:index')
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
@user_passes_test(is_verified, login_url='verify')
@login_required
def account(request):
    account = request.user.account
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
            # 'comments': comments,
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
