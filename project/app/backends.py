from django.contrib.auth.backends import ModelBackend

# Local
from .models import User


class Auth0Backend(ModelBackend):

    def authenticate(self, request, **kwargs):
        username = kwargs.get('username', None)
        name = kwargs.get('name', None)
        email = kwargs.get('email', None)
        is_verified = kwargs.get('email_verified', False)
        try:
            user = User.objects.get(
                username=username,
            )
            user.name = name
            user.email = email
            user.is_verified = is_verified
            user.data = kwargs
        except User.DoesNotExist:
            user = User(
                username=username,
                name=name,
                email=email,
                is_verified=is_verified,
                data=kwargs,
            )
            user.set_unusable_password()
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
