# First-Party
# Local
from django.contrib.auth import get_user_model
from factory import Faker
from factory import PostGenerationMethodCall
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    email = Faker('email')
    password = PostGenerationMethodCall('set_unusable_password')
    is_active = True
    class Meta:
        model = User
