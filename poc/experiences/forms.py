# ============================================
# poc/experiences/forms.py
# Definición de formularios basados en modelos
# ============================================

from django import forms
from .models import Experience, Comment


# =======================
# 🔹 FORMULARIO EXPERIENCE
# =======================
class ExperienceForm(forms.ModelForm):
    """
    Formulario basado en el modelo Experience.
    Se utiliza para que los usuarios puedan crear nuevas publicaciones
    (experiencias) directamente desde la interfaz web.
    """
    class Meta:
        # Modelo en el cual se basa este formulario
        model = Experience
        
        # Campos del modelo que queremos mostrar en el formulario
        fields = ["company", "title", "summary", "body"]


# =======================
# 🔹 FORMULARIO COMMENT
# =======================
class CommentForm(forms.ModelForm):
    """
    Formulario para agregar comentarios a una publicación.
    Solo incluye el campo 'text' (contenido del comentario).
    """
    class Meta:
        # Modelo en el cual se basa este formulario
        model = Comment
        
        # Campo único a capturar desde el usuario
        fields = ["text"]
        
        # Personalización del widget:
        #   - Textarea en lugar de input de texto
        #   - 3 filas de alto
        #   - Placeholder que guía al usuario
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Escribe tu comentario…"
                }
            )
        }