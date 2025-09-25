from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Review
from .services import update_enterprise_summary

# ============================================================
# 🔔 SEÑALES
# 1) Cambio en Review -> Actualizar resumen de Enterprise con AI.
# ============================================================

@receiver(post_save, sender=Review)
def refresh_summary_on_review_save(sender, instance: Review, created, **kwargs):
    transaction.on_commit(lambda: update_enterprise_summary(instance.enterprise_id))

@receiver(post_delete, sender=Review)
def refresh_summary_on_review_delete(sender, instance: Review, **kwargs):
    transaction.on_commit(lambda: update_enterprise_summary(instance.enterprise_id))