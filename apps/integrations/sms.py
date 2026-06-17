"""SMS delivery via Twilio (mock fallback when unconfigured)."""
from apps.integrations.base import BaseService


class SMSService(BaseService):
    name = "twilio_sms"
    required_keys = ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER")

    def send(self, to: str, body: str):
        if not self.is_live:
            return self._mock("send_sms", to=to, body=body)
        try:  # pragma: no cover - network dependent
            from twilio.rest import Client

            client = Client(self.config["TWILIO_ACCOUNT_SID"], self.config["TWILIO_AUTH_TOKEN"])
            message = client.messages.create(
                body=body, from_=self.config["TWILIO_FROM_NUMBER"], to=to
            )
            return {"status": "sent", "sid": message.sid}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "detail": str(exc)}
