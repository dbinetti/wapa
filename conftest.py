import pytest
from app.factories import UserFactory
from django.test.client import Client


@pytest.fixture
def anon_client():
    client = Client()
    return client


@pytest.fixture
def user():
    user = UserFactory(
        username='user',
        name='User',
        email='user@localhost',
        is_active=True,
        is_admin=False,
    )
    return user

@pytest.fixture
def user_client():
    user = UserFactory(
        username='user',
        name='User',
        email='user@localhost',
        is_active=True,
        is_admin=False,
    )
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def admin_client():
    admin = UserFactory(
        username='admin',
        name='Admin',
        email='admin@localhost',
        is_active=True,
        is_admin=True,
    )
    client = Client()
    client.force_login(admin)
    return client
