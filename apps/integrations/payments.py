"""Payment gateway abstractions.

A common ``PaymentGateway`` interface with concrete implementations for the
Tanzanian mobile-money providers (M-Pesa, Airtel Money, Tigo Pesa) and Stripe.
All gateways fall back to a deterministic MOCK that simulates a successful
charge so subscription / advertising flows work end-to-end without live
merchant credentials.
"""
import uuid

from apps.integrations.base import BaseService


class PaymentGateway(BaseService):
    """Base payment gateway. Subclasses implement ``_charge_live``."""

    currency = "TZS"

    def charge(self, *, amount, phone=None, token=None, reference=None, metadata=None):
        reference = reference or f"FL-{uuid.uuid4().hex[:12].upper()}"
        if not self.is_live:
            result = self._mock(
                "charge", amount=str(amount), currency=self.currency, reference=reference
            )
            result.update({"reference": reference, "provider_ref": f"MOCK-{reference}", "success": True})
            return result
        return self._charge_live(  # pragma: no cover - network dependent
            amount=amount, phone=phone, token=token, reference=reference, metadata=metadata or {}
        )

    def _charge_live(self, **kwargs):  # pragma: no cover
        raise NotImplementedError


class MpesaGateway(PaymentGateway):
    name = "mpesa"
    required_keys = ("MPESA_CONSUMER_KEY", "MPESA_CONSUMER_SECRET")

    def _charge_live(self, *, amount, phone, reference, **_):  # pragma: no cover
        # Real implementation issues an STK push via the Daraja API.
        return {"success": False, "detail": "Live M-Pesa STK push not configured", "reference": reference}


class AirtelMoneyGateway(PaymentGateway):
    name = "airtel_money"
    required_keys = ("AIRTEL_CLIENT_ID", "AIRTEL_CLIENT_SECRET")

    def _charge_live(self, *, amount, phone, reference, **_):  # pragma: no cover
        return {"success": False, "detail": "Live Airtel Money not configured", "reference": reference}


class TigoPesaGateway(PaymentGateway):
    name = "tigo_pesa"
    required_keys = ("TIGO_API_KEY",)

    def _charge_live(self, *, amount, phone, reference, **_):  # pragma: no cover
        return {"success": False, "detail": "Live Tigo Pesa not configured", "reference": reference}


class StripeGateway(PaymentGateway):
    name = "stripe"
    currency = "USD"
    required_keys = ("STRIPE_SECRET_KEY",)

    def _charge_live(self, *, amount, token, reference, metadata, **_):  # pragma: no cover
        import stripe

        stripe.api_key = self.config["STRIPE_SECRET_KEY"]
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=self.currency.lower(),
            payment_method=token,
            confirm=True,
            metadata={"reference": reference, **metadata},
        )
        return {"success": intent.status == "succeeded", "provider_ref": intent.id, "reference": reference}


GATEWAYS = {
    MpesaGateway.name: MpesaGateway,
    AirtelMoneyGateway.name: AirtelMoneyGateway,
    TigoPesaGateway.name: TigoPesaGateway,
    StripeGateway.name: StripeGateway,
}


def get_gateway(provider: str) -> PaymentGateway:
    try:
        return GATEWAYS[provider]()
    except KeyError as exc:
        raise ValueError(f"Unknown payment provider: {provider}") from exc
