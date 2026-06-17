import pytest

from apps.businesses.models import Business
from apps.leads.models import Lead
from apps.subscriptions.models import Payment, Plan, Subscription

pytestmark = pytest.mark.django_db


def test_checkout_with_mock_gateway_activates_subscription(auth_client):
    client, user = auth_client(role="business_owner")
    plan = Plan.objects.create(name="Premium", tier=Plan.Tier.PREMIUM, price=75000)
    resp = client.post(
        "/api/v1/subscriptions/checkout/",
        {"plan": plan.id, "provider": "mpesa", "phone": "+255700000000"},
        format="json",
    )
    assert resp.status_code == 201
    sub = Subscription.objects.get(user=user)
    assert sub.status == Subscription.Status.ACTIVE
    payment = Payment.objects.get(subscription=sub)
    assert payment.status == Payment.Status.SUCCESS
    assert payment.reference


def test_lead_score_is_computed_on_save(make_user):
    owner = make_user(email="o@example.com", role="business_owner")
    biz = Business.objects.create(owner=owner, name="LeadCo")
    lead = Lead.objects.create(
        business=biz, type=Lead.Type.PARTNERSHIP, message="x" * 100, industry="agriculture"
    )
    assert lead.score > 0


def test_user_only_sees_own_leads(api, make_user):
    owner_a = make_user(email="a@example.com", role="business_owner")
    owner_b = make_user(email="b@example.com", role="business_owner")
    biz_a = Business.objects.create(owner=owner_a, name="A")
    biz_b = Business.objects.create(owner=owner_b, name="B")
    Lead.objects.create(business=biz_a)
    Lead.objects.create(business=biz_b)
    api.force_authenticate(user=owner_a)
    resp = api.get("/api/v1/leads/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
