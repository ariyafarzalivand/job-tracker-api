from applications.models import JobApplication

APPLICATIONS_URL = "/api/applications/"


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
    assert response.data["count"] == 1
    assert response.data["results"][0]["company"] == "Mine GmbH"


def create_application(owner, company="Example GmbH"):
    # Small helper so each test only states what matters to it.
    return JobApplication.objects.create(
        owner=owner,
        company=company,
        position="Developer",
        applied_date="2026-11-20",
    )


def detail_url(application):
    return f"{APPLICATIONS_URL}{application.id}/"


def test_user_can_update_own_application(auth_client, user):
    application = create_application(user)

    response = auth_client.patch(
        detail_url(application), {"status": "interview"}, format="json"
    )

    assert response.status_code == 200
    application.refresh_from_db()
    assert application.status == JobApplication.Status.INTERVIEW


def test_user_can_delete_own_application(auth_client, user):
    application = create_application(user)

    response = auth_client.delete(detail_url(application))

    assert response.status_code == 204
    assert not JobApplication.objects.exists()


def test_user_cannot_view_another_users_application(auth_client, other_user):
    application = create_application(other_user)

    response = auth_client.get(detail_url(application))

    # 404 instead of 403, so the API does not reveal that the object exists.
    assert response.status_code == 404


def test_user_cannot_delete_another_users_application(auth_client, other_user):
    application = create_application(other_user)

    response = auth_client.delete(detail_url(application))

    assert response.status_code == 404
    assert JobApplication.objects.filter(pk=application.pk).exists()


def test_create_rejects_invalid_status(auth_client):
    payload = {
        "company": "Test GmbH",
        "position": "Backend Developer",
        "applied_date": "2026-11-20",
        "status": "not-a-real-status",
    }

    response = auth_client.post(APPLICATIONS_URL, payload, format="json")

    assert response.status_code == 400
    assert "status" in response.data


def test_list_is_paginated(auth_client, user):
    # One more application than fits on a single page (PAGE_SIZE is 20).
    for number in range(21):
        create_application(user, company=f"Company {number}")

    response = auth_client.get(APPLICATIONS_URL)

    assert response.status_code == 200
    assert response.data["count"] == 21
    assert len(response.data["results"]) == 20
    # A link to the second page must be offered.
    assert response.data["next"] is not None
