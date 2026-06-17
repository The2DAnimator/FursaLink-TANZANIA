from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.leads.models import Lead


@receiver(pre_save, sender=Lead)
def set_lead_score(sender, instance, **kwargs):
    instance.score = instance.compute_score()
