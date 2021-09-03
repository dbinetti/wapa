# Django
# Third-Party
import pytest
from django.urls import reverse


def test_deploy():
    assert True

@pytest.mark.django_db
def test_index(admin_client):
    path = reverse('admin:index')
    response = admin_client.get(path)
    assert response.status_code == 200
