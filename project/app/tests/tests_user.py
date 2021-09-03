# Django
# Third-Party
import pytest
from django.urls import reverse


def test_deploy():
    assert True


@pytest.mark.django_db
def test_index(user_client, issue):
    path = reverse('index')
    response = user_client.get(path)
    assert response.status_code == 200

@pytest.mark.django_db
def test_admin(user_client):
    path = reverse('admin:index')
    response = user_client.get(path)
    assert response.status_code == 302

@pytest.mark.django_db
def test_comments(user_client, issue):
    path = reverse('comments')
    response = user_client.get(path)
    assert response.status_code == 200
