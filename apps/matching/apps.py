from django.apps import AppConfig


class MatchingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.matching"
    verbose_name = "Matching"

    def ready(self):
        try:
            import apps.matching.signals  # noqa: F401
        except ImportError:
            pass
