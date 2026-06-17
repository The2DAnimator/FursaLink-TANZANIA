from django.apps import AppConfig


class OpportunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.opportunities"
    verbose_name = "Opportunities"

    def ready(self):
        try:
            import apps.opportunities.signals  # noqa: F401
        except ImportError:
            pass
