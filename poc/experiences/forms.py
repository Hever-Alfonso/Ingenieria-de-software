# ============================================
# poc/experiences/forms.py
# Definición de formularios basados en modelos
# ============================================

from django import forms
from .models import Review, Comment

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# =======================
# FORMULARIO SIGNUP
# =======================
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplico Bootstrap a todos los inputs
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()

# =======================
# FORMULARIO REVIEW
# =======================
class ReviewForm(forms.ModelForm):
    anonymous = forms.BooleanField(
        required=False,
        label="Publicar como anónimo",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Review
        fields = ["title", "body", "rating", "anonymous"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Título de tu experiencia",
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Cuenta tu experiencia con la empresa…",
            }),
            "rating": forms.Select(attrs={"class": "form-select"}, choices=[(i, f"{i} ⭐") for i in range(1, 6)]),
        }
        labels = {
            "title": "Título",
            "body": "Descripción",
            "rating": "Calificación",
        }

    def clean_rating(self):
        r = int(self.cleaned_data["rating"])
        if r < 1 or r > 5:
            raise forms.ValidationError("La calificación debe estar entre 1 y 5 estrellas.")
        return r

'''
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
        model = Review

        # Campos del modelo que queremos mostrar en el formulario
        fields = ["enterprise", "title", "summary", "body"]


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
'''