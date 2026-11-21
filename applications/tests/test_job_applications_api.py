import logging

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


def create_application(owner, company="Example GmbH", **extra_fields):
    # Small helper so each test only states what matters to it.
    return JobApplication.objects.create(
        owner=owner,
        company=company,
        position="Developer",
        applied_date="2026-11-20",
        **extra_fields,
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


def test_filter_by_status(auth_client, user):
    create_application(user, company="Applied AG")
    create_application(
        user, company="Interview GmbH", status=JobApplication.Status.INTERVIEW
    )

    response = auth_client.get(APPLICATIONS_URL, {"status": "interview"})

    assert response.data["count"] == 1
    assert response.data["results"][0]["company"] == "Interview GmbH"


def test_search_by_company_name(auth_client, user):
    create_application(user, company="Siemens AG")
    create_application(user, company="Bosch GmbH")

    response = auth_client.get(APPLICATIONS_URL, {"search": "siemens"})

    assert response.data["count"] == 1
    assert response.data["results"][0]["company"] == "Siemens AG"


def test_ordering_by_company(auth_client, user):
    create_application(user, company="Zeta AG")
    create_application(user, company="Alpha GmbH")

    response = auth_client.get(APPLICATIONS_URL, {"ordering": "company"})

    companies = [item["company"] for item in response.data["results"]]
    assert companies == ["Alpha GmbH", "Zeta AG"]


def test_search_never_returns_other_users_applications(auth_client, other_user):
    # Filters work on top of the user's own queryset, so this must stay empty.
    create_application(other_user, company="Secret AG")

    response = auth_client.get(APPLICATIONS_URL, {"search": "secret"})

    assert response.data["count"] == 0


def test_create_logs_id_but_not_personal_data(auth_client, user, caplog, monkeypatch):
    # The "applications" logger does not propagate to the root logger,
    # which is where caplog listens, so allow it for this test only.
    monkeypatch.setattr(logging.getLogger("applications"), "propagate", True)
    payload = {
        "company": "Private GmbH",
        "position": "Backend Developer",
        "applied_date": "2026-11-20",
    }

    with caplog.at_level(logging.INFO, logger="applications"):
        response = auth_client.post(APPLICATIONS_URL, payload, format="json")

    assert response.status_code == 201
    assert f"Application created: id={response.data['id']}" in caplog.text
    # Personal data must never be written to log files.
    assert "Private GmbH" not in caplog.text
