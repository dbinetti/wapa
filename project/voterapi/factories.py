# First-Party
from factory import Faker
from factory import PostGenerationMethodCall
from factory.django import DjangoModelFactory

# Local
from .models import User


class UserFactory(DjangoModelFactory):
    name = Faker('name_male')
    email = Faker('email')
    password = PostGenerationMethodCall('set_unusable_password')
    is_active = True
    class Meta:
        model = User
