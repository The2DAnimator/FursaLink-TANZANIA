"""WhatsApp Business Cloud API messaging (mock fallback when unconfigured)."""
import requests

from apps.integrations.base import BaseService


class WhatsAppService(BaseService):
    name = "whatsapp"
    required_keys = ("WHATSAPP_API_TOKEN", "WHATSAPP_PHONE_ID")

    def send(self, to: str, body: str):
        if not self.is_live:
            return self._mock("send_whatsapp", to=to, body=body)
        try:  # pragma: no cover - network dependent
            url = f"https://graph.facebook.com/v19.0/{self.config['WHATSAPP_PHONE_ID']}/messages"
            headers = {
                "Authorization": f"Bearer {self.config['WHATSAPP_API_TOKEN']}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": body},
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            return {"status": "sent", "response": resp.json()}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "detail": str(exc)}
