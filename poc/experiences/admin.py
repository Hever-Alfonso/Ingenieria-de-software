# ------------------------------
# Importamos el admin de Django y nuestros modelos
# ------------------------------
from django.contrib import admin
from .models import Experience, Comment, CompanySummary

# ------------------------------
# Administración del modelo Experience
# ------------------------------
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la tabla de la vista de administración
    list_display = ("company", "title", "created_at")
    # Campos por los que se podrá buscar en el panel de admin
    search_fields = ("company", "title", "summary")

# ------------------------------
# Administración del modelo Comment
# ------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la tabla
    list_display = ("experience", "author", "created_at")
    # Búsqueda: incluye campos relacionados (experience__title, experience__company)
    search_fields = ("experience__title", "experience__company", "text")

# ------------------------------
# Administración del modelo CompanySummary
# ------------------------------
@admin.register(CompanySummary)
class CompanySummaryAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la tabla
    list_display = ("company", "total_posts", "total_comments", "last_computed")
    # Campo por el cual se podrá buscar
    search_fields = ("company",)