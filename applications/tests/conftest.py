import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="alice", password="test-pass-123"
    )


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(
        username="bob", password="test-pass-123"
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    # Skips the login step, so each test focuses on one behaviour.
    api_client.force_authenticate(user=user)
    return api_client
