from django.db import models
from django.contrib.auth.models import User  # Importamos el modelo de usuario de Django

# =======================
# 🔹 MODELO EXPERIENCE
# =======================
class Experience(models.Model):
    """
    Representa una publicación/experiencia dentro de la plataforma.
    Cada experiencia tiene:
    - company: nombre de la empresa
    - title: título de la publicación
    - summary: breve resumen
    - body: descripción completa
    - created_at: fecha y hora en que fue creada (se asigna automáticamente)
    - author: usuario que la creó (puede ser null si se borra el usuario)
    """

    company = models.CharField(max_length=120)   # Empresa asociada
    title   = models.CharField(max_length=160)   # Título de la experiencia
    summary = models.CharField(max_length=240)   # Resumen breve
    body    = models.TextField()                 # Texto completo / detalle
    created_at = models.DateTimeField(auto_now_add=True)  
    # Fecha automática de creación

    # Relación con usuario → permite saber quién creó la experiencia
    # Si el usuario se borra, el campo queda en NULL (SET_NULL)
    author  = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        """
        Devuelve una representación legible de la experiencia en el admin
        o cuando se imprime el objeto.
        """
        return f"{self.company} - {self.title}"