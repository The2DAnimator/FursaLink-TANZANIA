from django.apps import AppConfig


class MarketpricesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.marketprices"
    verbose_name = "Marketprices"

    def ready(self):
        try:
            import apps.marketprices.signals  # noqa: F401
        except ImportError:
            pass
