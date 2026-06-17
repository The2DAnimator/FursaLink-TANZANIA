import pytest

from apps.integrations.email import EmailService
from apps.integrations.payments import get_gateway
from apps.integrations.sms import SMSService

pytestmark = pytest.mark.django_db


def test_payment_gateway_mock_succeeds():
    gateway = get_gateway("mpesa")
    result = gateway.charge(amount=1000)
    assert result["success"] is True
    assert result["reference"].startswith("FL-")


def test_unknown_gateway_raises():
    with pytest.raises(ValueError):
        get_gateway("nope")


def test_sms_service_mock_mode():
    result = SMSService().send(to="+255700000000", body="hello")
    assert result["status"] == "mocked"


def test_email_service_fallback_sends(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    result = EmailService().send(to="x@example.com", subject="Hi", body="Body")
    assert result["status"] in ("sent", "sent-fallback")


def test_schema_endpoint(api):
    assert api.get("/api/schema/").status_code == 200


def test_swagger_docs(api):
    assert api.get("/api/docs/").status_code == 200


def test_home_page_renders(client):
    assert client.get("/").status_code == 200
