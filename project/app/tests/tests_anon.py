# Django
# Third-Party
import pytest
from django.urls import reverse


def test_deploy():
    assert True


@pytest.mark.django_db
def test_index(anon_client, issue):
    path = reverse('index')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_about(anon_client):
    path = reverse('about')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_privacy(anon_client):
    path = reverse('privacy')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_support(anon_client):
    path = reverse('support')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_faq(anon_client):
    path = reverse('faq')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_account(anon_client):
    path = reverse('account')
    response = anon_client.get(path)
    assert response.status_code == 302

def test_board(anon_client):
    path = reverse('board')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_updates(anon_client):
    path = reverse('updates')
    response = anon_client.get(path)
    assert response.status_code == 200

def test_comments(anon_client):
    path = reverse('comments')
    response = anon_client.get(path)
    assert response.status_code == 302

def test_delete(anon_client):
    path = reverse('delete')
    response = anon_client.get(path)
    assert response.status_code == 302

def test_admin(anon_client):
    path = reverse('admin:index')
    response = anon_client.get(path)
    assert response.status_code == 302

@pytest.mark.django_db
def test_dashboard(anon_client):
    path = reverse('dashboard')
    response = anon_client.get(path)
    assert response.status_code == 302
