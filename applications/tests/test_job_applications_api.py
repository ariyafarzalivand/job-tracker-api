import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from applications.models import JobApplication

APPLICATIONS_URL = "/api/applications/"

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="test-pass-123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="bob", password="test-pass-123")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    # Skips the login step, so each test focuses on one behaviour.
    api_client.force_authenticate(user=user)
    return api_client


def test_list_requires_authentication(api_client):
    response = api_client.get(APPLICATIONS_URL)

    assert response.status_code == 401


def test_create_application_sets_owner_from_logged_in_user(auth_client, user):
    payload = {
        "company": "Test GmbH",
        "position": "Backend Developer",
        "applied_date": "2026-11-20",
    }

    response = auth_client.post(APPLICATIONS_URL, payload, format="json")

    assert response.status_code == 201
    application = JobApplication.objects.get()
    assert application.owner == user
    # Status was not sent, so the model default must apply.
    assert application.status == JobApplication.Status.APPLIED


def test_user_sees_only_own_applications(auth_client, user, other_user):
    JobApplication.objects.create(
        owner=user,
        company="Mine GmbH",
        position="Developer",
        applied_date="2026-11-20",
    )
    JobApplication.objects.create(
        owner=other_user,
        company="Not Mine AG",
        position="Developer",
        applied_date="2026-11-20",
    )

    response = auth_client.get(APPLICATIONS_URL)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["company"] == "Mine GmbH"