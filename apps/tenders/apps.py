from django.apps import AppConfig


class TendersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenders"
    verbose_name = "Tenders"

    def ready(self):
        try:
            import apps.tenders.signals  # noqa: F401
        except ImportError:
            pass
