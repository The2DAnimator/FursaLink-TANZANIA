from django.apps import AppConfig


class AdvertisingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.advertising"
    verbose_name = "Advertising"

    def ready(self):
        try:
            import apps.advertising.signals  # noqa: F401
        except ImportError:
            pass
