# Django
import json
import urllib

import posthog
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

# Local
from .models import User


class Auth0Backend(ModelBackend):

    def authenticate(self, request, **kwargs):
        username = kwargs.get('username', None)
        name = kwargs.get('name', None)
        email = kwargs.get('email', None)
        try:
            user = User.objects.get(
                username=username,
            )
        except User.DoesNotExist:
            user = User(
                username=username,
                name=name,
                email=email,
                data=kwargs,
            )
            user.set_unusable_password()
            user.save()
            posthog.capture(
                str(user.id),
                'Create Account',
            )
        encoded = request.COOKIES.get(f'ph_{settings.POSTHOG_API_KEY}_posthog', None)
        if encoded:
            decoded = json.loads(urllib.parse.unquote(encoded))
            posthog.alias(
                decoded['distinct_id'],
                str(user.id),
            )
        posthog.identify(
            str(user.id),
            {'name': name, 'email': email,}
        )
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
