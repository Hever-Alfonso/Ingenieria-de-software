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
from .models import Experience, Comment, CompanySummary


# ============================================================
# 🔹 Normalización de marca
# ------------------------------------------------------------
# _norm(company): reduce variantes de nombre a un "núcleo" comparable.
#   - elimina sufijos comunes ("S.A.S.", "S.A.", "Colombia")
#   - pasa a minúsculas y limpia espacios
#   Ejemplo: "Claro Colombia" -> "claro"
#            "Claro S.A.S."   -> "claro"
# ============================================================
def _norm(s: str) -> str:
    return (s or "").strip().lower()\
        .replace(" s.a.s.", "").replace(" s.a.", "").replace(" colombia", "")


# ============================================================
# 🔹 Construcción del corpus
# ------------------------------------------------------------
# _build_corpus(company):
#   - Busca publicaciones y comentarios cuyo company contenga el nombre
#     tal cual y/o el "núcleo" (_norm(company)).
#   - Concatena título, resumen y cuerpo de publicaciones + texto de comentarios.
#   - Devuelve: (texto_concatenado, total_publicaciones, total_comentarios)
# ============================================================
def _build_corpus(company: str) -> tuple[str, int, int]:
    core = _norm(company)

    # Publicaciones de la marca y sus variantes
    posts = (Experience.objects.filter(company__icontains=company) |
             Experience.objects.filter(company__icontains=core))

    # Comentarios de esas publicaciones
    comments = (Comment.objects.filter(experience__company__icontains=company) |
                Comment.objects.filter(experience__company__icontains=core))

    # Unimos textos relevantes en un corpus
    post_texts = [f"{p.title}\n{p.summary}\n{p.body}" for p in posts]
    comment_texts = [c.text for c in comments]
    corpus = "\n".join(post_texts + comment_texts).strip()

    return corpus, posts.count(), comments.count()


# ============================================================
# 🔹 Generación del insight (frase resumen)
# ------------------------------------------------------------
# _insight_summary(text, company):
#   - Tokeniza el texto y quita 'stopwords' (palabras vacías).
#   - Cuenta palabras más frecuentes.
#   - Genera una frase natural usando las top 2–5 palabras clave.
#   - Si no hay material suficiente, devuelve un mensaje informativo.
# ============================================================
def _insight_summary(text: str, company: str) -> str:
    import re
    from collections import Counter

    # Extraemos palabras de 3+ letras y pasamos a minúsculas
    words = re.findall(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,}", (text or "").lower())

    # Lista simple de stopwords en español (puedes ajustarla si quieres)
    stop = {
        "para","por","con","las","los","una","unos","unas","que","como","muy","pero",
        "este","esta","esto","esa","ese","son","del","de","la","el","y","o","en","un",
        "se","al","más","mas","sus","sobre","sin","a","es","hay","ser","fue","está",
        "estan","están","estaba","estaban","solo","solo","tambien","también","ya",
        "lo","le","les","nos","me","mi","tu","su","si","sí","no"
    }

    # Filtramos palabras vacías
    keywords = [w for w in words if w not in stop]
    if not keywords:
        return f"No hay suficiente información para generar un resumen sobre {company}."

    # Tomamos las más frecuentes (hasta 6 para tener material)
    common = [w for w, _ in Counter(keywords).most_common(6)]

    # Seleccionamos las top 5 para la frase
    top = common[:5]

    # Construimos una frase natural según cuántas palabras tengamos
    if len(top) == 1:
        joined = top[0]
        return f"Los usuarios hablan principalmente de {joined} en {company}."
    elif len(top) == 2:
        joined = " y ".join(top)
        return f"En general, los usuarios resaltan {joined} en {company}."
    else:
        joined = ", ".join(top[:-1]) + f" y {top[-1]}"
        return f"En general, los usuarios mencionan con mayor frecuencia {joined} en {company}."


# ============================================================
# 🔹 Cálculo y guardado del resumen agregado
# ------------------------------------------------------------
# _compute_and_store_summary(company):
#   - Construye corpus y métricas agregadas.
#   - Genera el texto resumen (insight) o un fallback si no hay datos.
#   - Actualiza/crea la fila de CompanySummary para esa empresa.
# ============================================================
def _compute_and_store_summary(company: str) -> None:
    corpus, n_posts, n_comments = _build_corpus(company)

    text = (
        f"No hay suficiente información para generar un resumen sobre {company}."
        if not corpus else _insight_summary(corpus, company)
    )

    CompanySummary.objects.update_or_create(
        company=company,
        defaults={
            "summary": text,
            "total_posts": n_posts,
            "total_comments": n_comments,
            "last_computed": timezone.now(),
        }
    )


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