import pytest

from apps.businesses.models import Business

pytestmark = pytest.mark.django_db


def test_anonymous_can_list_businesses(api, make_user):
    owner = make_user(email="owner@example.com", role="business_owner")
    Business.objects.create(owner=owner, name="Acme Co")
    resp = api.get("/api/v1/businesses/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1


def test_owner_can_create_business(auth_client):
    client, user = auth_client(role="business_owner")
    resp = client.post("/api/v1/businesses/", {"name": "My Biz"}, format="json")
    assert resp.status_code == 201
    assert resp.data["owner"] == user.id
    assert resp.data["slug"] == "my-biz"


def test_non_owner_cannot_edit_business(api, make_user):
    owner = make_user(email="owner2@example.com", role="business_owner")
    other = make_user(email="other@example.com")
    biz = Business.objects.create(owner=owner, name="Owned")
    api.force_authenticate(user=other)
    resp = api.patch(f"/api/v1/businesses/{biz.slug}/", {"name": "Hacked"}, format="json")
    assert resp.status_code == 403


def test_admin_can_verify_business(api, admin_user, make_user):
    owner = make_user(email="owner3@example.com", role="business_owner")
    biz = Business.objects.create(owner=owner, name="ToVerify")
    api.force_authenticate(user=admin_user)
    resp = api.post(f"/api/v1/businesses/{biz.slug}/verify/")
    assert resp.status_code == 200
    biz.refresh_from_db()
    assert biz.verification_status == Business.VerificationStatus.VERIFIED


def test_review_creates_and_average(api, make_user):
    owner = make_user(email="owner4@example.com", role="business_owner")
    reviewer = make_user(email="rev@example.com")
    biz = Business.objects.create(owner=owner, name="Reviewed")
    api.force_authenticate(user=reviewer)
    resp = api.post(
        "/api/v1/reviews/", {"business": biz.id, "rating": 4, "comment": "Nice"}, format="json"
    )
    assert resp.status_code == 201
    biz.refresh_from_db()
    assert biz.average_rating == 4.0
