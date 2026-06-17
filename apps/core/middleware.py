"""Audit logging middleware.

Records mutating API requests (POST/PUT/PATCH/DELETE) to the AuditLog table so
administrators have a tamper-evident trail of who changed what. Read requests
are intentionally skipped to keep the log high-signal.
"""
import logging

logger = logging.getLogger(__name__)

_AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_IGNORED_PREFIXES = ("/static/", "/media/", "/admin/jsi18n")


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._maybe_log(request, response)
        except Exception:  # pragma: no cover - audit logging must never break a request
            logger.exception("Failed to write audit log entry")
        return response

    def _maybe_log(self, request, response):
        if request.method not in _AUDITED_METHODS:
            return
        if any(request.path.startswith(p) for p in _IGNORED_PREFIXES):
            return

        from apps.core.models import AuditLog

        user = getattr(request, "user", None)
        AuditLog.objects.create(
            user=user if (user and user.is_authenticated) else None,
            action=f"{request.method} {request.path}",
            method=request.method,
            path=request.path[:255],
            status_code=getattr(response, "status_code", None),
            ip_address=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:400],
        )
