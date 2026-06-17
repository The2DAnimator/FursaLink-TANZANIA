from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.jobs"
    verbose_name = "Jobs"

    def ready(self):
        try:
            import apps.jobs.signals  # noqa: F401
        except ImportError:
            pass
