# ============================================
# poc/experiences/services.py
# Servicios y señales para mantener actualizado
# el modelo CompanySummary automáticamente
# ============================================

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Experience, Comment


# =======================
# 🔹 FUNCIÓN AUXILIAR
# =======================
def _summarize(company: str):
    """
    Recalcula y actualiza el resumen de una empresa.
    
    - Intenta usar un servicio externo `summarize_company` (si está disponible).
    - Si falla, genera un resumen mínimo con conteo de posts y comentarios,
      de forma que nunca se rompa el flujo de guardado.
    """
    try:
        # Import "perezoso" (lazy import): evita dependencias circulares
        from .services import summarize_company  
        summarize_company(company)
        return
    except Exception:
        # ⚠️ Fallback ultra simple en caso de error
        from django.utils import timezone
        from .models import CompanySummary, Experience, Comment

        # Contar posts y comentarios de la empresa
        posts = Experience.objects.filter(company__iexact=company).count()
        comments = Comment.objects.filter(experience__company__iexact=company).count()
        text = "Resumen pendiente de cálculo (servicio no disponible por ahora)."

        # Actualizar o crear el resumen
        CompanySummary.objects.update_or_create(
            company=company,
            defaults={
                "summary": text,
                "total_posts": posts,
                "total_comments": comments,
                "last_computed": timezone.now(),
            }
        )


# =======================
# 🔹 SEÑALES SOBRE COMMENTS
# =======================

@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def _recalc_on_comment_change(sender, instance, **kwargs):
    """
    Cada vez que se crea o elimina un comentario,
    recalculamos el resumen de la empresa correspondiente.
    """
    company = getattr(instance.experience, "company", None)
    if company:
        _summarize(company)


# =======================
# 🔹 SEÑALES SOBRE EXPERIENCE (cambios de empresa)
# =======================

@receiver(pre_save, sender=Experience)
def _recalc_on_experience_company_change(sender, instance, **kwargs):
    """
    Detecta si una publicación cambia de empresa.
    - Si cambia, recalculamos tanto la empresa vieja como la nueva.
    """
    if not instance.pk:  # Si es un objeto nuevo, no hay "empresa previa"
        return
    try:
        old = Experience.objects.get(pk=instance.pk)
    except Experience.DoesNotExist:
        return

    if old.company != instance.company:
        # Recalcular para la empresa anterior
        if old.company:
            _summarize(old.company)
        # Y para la empresa nueva
        if instance.company:
            _summarize(instance.company)


# =======================
# 🔹 SEÑALES SOBRE EXPERIENCE (crear / eliminar)
# =======================

@receiver(post_save, sender=Experience)
@receiver(post_delete, sender=Experience)
def _recalc_on_experience_create_delete(sender, instance, **kwargs):
    """
    Cada vez que se crea o elimina una experiencia,
    recalculamos el resumen de su empresa.
    """
    company = getattr(instance, "company", None)
    if company:
        _summarize(company)