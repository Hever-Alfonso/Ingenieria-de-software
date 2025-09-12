# ============================================================
# poc/experiences/signals.py
# Señales de Django para mantener actualizado CompanySummary
# ------------------------------------------------------------
# ¿Qué hace este archivo?
# - Escucha cambios en Experience y Comment (crear/editar/borrar).
# - Reagrupa todas las publicaciones/comentarios de una "misma marca"
#   aunque tenga variantes en el nombre (p.ej. "Claro", "Claro Colombia",
#   "Claro S.A.S.").
# - Construye un corpus de texto con esos contenidos.
# - Extrae palabras clave más frecuentes y genera un RESUMEN tipo "insight"
#   (frase explicativa) que guardamos en CompanySummary.
# - Así, las vistas de resumen muestran un texto humano y métricas agregadas.
# ============================================================

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Enterprise, Review, Comment

'''
# ============================================================
# 🔔 SEÑALES
# ------------------------------------------------------------
# 1) Cambio en Comment (crear/borrar) → recalcular resumen de su empresa.
# 2) Cambio en Experience:
#      - pre_save: si cambia el 'company', recalcular vieja y nueva empresa.
#      - post_save/post_delete: al crear o borrar, recalcular para esa empresa.
# ------------------------------------------------------------
# Nota: Estas funciones se registran automáticamente porque en apps.py
# tienes:
#   class ExperiencesConfig(AppConfig):
#       ...
#       def ready(self):
#           from . import signals
# Eso hace que al iniciar Django, se importen estas señales.
# ============================================================

@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def _recalc_on_comment_change(sender, instance, **kwargs):
    """Recalcula el resumen cuando se crea o borra un comentario."""
    company = getattr(instance.experience, "company", None)
    if company:
        _compute_and_store_summary(company)


@receiver(pre_save, sender=Experience)
def _recalc_on_experience_company_change(sender, instance, **kwargs):
    """
    Antes de guardar una Experience existente:
    - Si cambia el nombre de la empresa, recalculamos para la anterior y la nueva.
    """
    if not instance.pk:  # Si es una nueva, no hay "valor anterior" que comparar
        return

    try:
        old = Experience.objects.get(pk=instance.pk)
    except Experience.DoesNotExist:
        return

    if old.company != instance.company:
        if old.company:
            _compute_and_store_summary(old.company)
        if instance.company:
            _compute_and_store_summary(instance.company)


@receiver(post_save, sender=Experience)
@receiver(post_delete, sender=Experience)
def _recalc_on_experience_create_delete(sender, instance, **kwargs):
    """
    Al crear o borrar una Experience, recalculamos para su empresa.
    """
    company = getattr(instance, "company", None)
    if company:
        _compute_and_store_summary(company)
'''