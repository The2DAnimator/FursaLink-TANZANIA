"""Email delivery via SendGrid with a Django-backend fallback."""
from django.conf import settings
from django.core.mail import send_mail

from apps.integrations.base import BaseService


class EmailService(BaseService):
    name = "sendgrid"
    required_keys = ("SENDGRID_API_KEY",)

    def send(self, to: str, subject: str, body: str, html: str | None = None):
        if self.is_live:
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail

                message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=to,
                    subject=subject,
                    plain_text_content=body,
                    html_content=html,
                )
                client = SendGridAPIClient(self.config["SENDGRID_API_KEY"])
                response = client.send(message)
                return {"status": "sent", "code": response.status_code}
            except Exception:  # pragma: no cover - network dependent
                # Fall through to Django backend (console/SMTP) on provider error.
                pass
        # Fallback: Django email backend (console in dev, SMTP in prod).
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [to],
            html_message=html,
            fail_silently=True,
        )
        return {"status": "sent-fallback", "to": to}
