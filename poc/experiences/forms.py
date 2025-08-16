# poc/experiences/forms.py
from django import forms
from .models import Experience

# =======================
# 🔹 FORMULARIO EXPERIENCE
# =======================
class ExperienceForm(forms.ModelForm):
    """
    Formulario basado en el modelo Experience.
    Se utiliza para crear nuevas experiencias desde la interfaz web.

    Django genera automáticamente los inputs HTML a partir de los campos
    que indiquemos en 'fields'.
    """

    class Meta:
        # Modelo del cual se va a generar el formulario
        model = Experience  

        # Campos que estarán disponibles en el formulario
        fields = ["company", "title", "summary", "body"]
        # Nota: el campo 'author' y 'created_at' NO se incluyen aquí
        # porque:
        # - author lo asociamos automáticamente en la vista con request.user
        # - created_at se asigna solo al guardar (auto_now_add)