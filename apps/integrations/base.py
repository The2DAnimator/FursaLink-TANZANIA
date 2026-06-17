"""Base helpers for external service integrations.

Every integration follows the same pattern: if the required credentials are
configured it talks to the real provider, otherwise it falls back to a MOCK
implementation that logs the call and returns a deterministic success response.
This keeps the whole platform runnable in development, CI and demos without any
third-party accounts, while real credentials can be supplied via environment
variables in production.
"""
import logging

from django.conf import settings

logger = logging.getLogger("apps.integrations")


class BaseService:
    #: settings.INTEGRATIONS keys that must be truthy for live mode.
    required_keys: tuple[str, ...] = ()
    name = "service"

    def __init__(self):
        self.config = settings.INTEGRATIONS

    @property
    def is_live(self) -> bool:
        return all(self.config.get(k) for k in self.required_keys)

    def _mock(self, action: str, **details):
        logger.info("[MOCK %s] %s %s", self.name, action, details)
        return {"status": "mocked", "service": self.name, "action": action, **details}
