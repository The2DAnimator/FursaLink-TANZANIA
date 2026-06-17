from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import JobSeekerProfile, User


@receiver(post_save, sender=User)
def ensure_job_seeker_profile(sender, instance, created, **kwargs):
    """Auto-create a job seeker profile when a job seeker registers."""
    if created and instance.role == User.Role.JOB_SEEKER:
        JobSeekerProfile.objects.get_or_create(user=instance)
