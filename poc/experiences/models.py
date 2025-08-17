# ============================================
# poc/experiences/models.py
# Definición de modelos principales del sistema
# ============================================

from django.db import models
from django.contrib.auth.models import User  # Modelo de usuarios de Django
from django.utils import timezone


# =======================
# 🔹 MODELO EXPERIENCE
# =======================
class Experience(models.Model):
    """
    Representa una publicación/experiencia dentro de la plataforma.
    Cada experiencia incluye:
    - company: nombre de la empresa
    - title: título de la publicación
    - summary: resumen breve
    - body: descripción completa
    - created_at: fecha de creación automática
    - author: usuario que la creó (puede ser NULL si se elimina el usuario)
    """

    # Campos principales
    company = models.CharField(max_length=120)   # Empresa asociada
    title   = models.CharField(max_length=160)   # Título de la publicación
    summary = models.CharField(max_length=240)   # Breve descripción
    body    = models.TextField()                 # Texto completo / detalle

    # Fecha y hora automática de creación
    created_at = models.DateTimeField(auto_now_add=True)

    # Relación con usuario → permite saber quién creó la experiencia
    # Si el usuario se borra, el campo queda en NULL (SET_NULL)
    author = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        """Devuelve un string legible para admin y debugging."""
        return f"{self.company} - {self.title}"


# =======================
# 🔹 MODELO COMMENT
# =======================
class Comment(models.Model):
    """
    Comentario hecho por un usuario sobre una experiencia específica.
    Relación uno-a-muchos: cada experiencia puede tener múltiples comentarios.
    """

    # Relación hacia la experiencia
    experience = models.ForeignKey(
        Experience,
        related_name="comments",
        on_delete=models.CASCADE  # Si se borra la experiencia, se borran sus comentarios
    )

    # Usuario autor del comentario (puede ser anónimo si se borra)
    author = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    # Texto del comentario
    text = models.TextField()

    # Fecha de creación
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Los comentarios se listan del más reciente al más antiguo
        ordering = ["-created_at"]

    def __str__(self):
        """Muestra quién comentó y sobre qué experiencia."""
        who = self.author.username if self.author else "anónimo"
        return f"Comment by {who} on {self.experience_id}"


# =======================
# 🔹 MODELO COMPANY SUMMARY
# =======================
class CompanySummary(models.Model):
    """
    Resumen agregado por empresa.
    - Se actualiza cuando se crean experiencias o comentarios.
    - Guarda un caché para evitar recalcular en cada request.
    """

    company        = models.CharField(max_length=255, unique=True)  # Empresa (única)
    summary        = models.TextField(blank=True)                   # Texto resumen generado
    total_posts    = models.PositiveIntegerField(default=0)          # Número de experiencias
    total_comments = models.PositiveIntegerField(default=0)          # Número de comentarios
    last_computed  = models.DateTimeField(default=timezone.now)      # Última vez que se actualizó

    class Meta:
        verbose_name = "Company summary"
        verbose_name_plural = "Company summaries"

    def __str__(self):
        """Representación legible en admin/debugging."""
        return f"{self.company} ({self.total_posts} posts, {self.total_comments} comentarios)"