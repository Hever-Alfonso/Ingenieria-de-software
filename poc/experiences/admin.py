# ------------------------------
# Importamos el admin de Django y nuestros modelos
# ------------------------------
from django.contrib import admin
from .models import Enterprise, Review, Comment

# ------------------------------
# Administración del modelo Enterprise
# ------------------------------
@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    # Lo que ves en la tabla
    list_display = ("name", "ai_summary_short", "reviews_count", "average_rating")
    # Buscar solo por campos reales (no por propiedades)
    search_fields = ("name", "AI_summary")
    ordering = ("name",)

    # Muestra un resumen cortico en la lista
    def ai_summary_short(self, obj):
        if not obj.AI_summary:
            return "—"
        return (obj.AI_summary[:60] + "…") if len(obj.AI_summary) > 60 else obj.AI_summary
    ai_summary_short.short_description = "Resumen"

# ------------------------------
# Administración del modelo Review
# ------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("enterprise", "title", "author", "anonymous", "rating", "created_at")
    search_fields = ("title", "body", "enterprise__name", "author__username")
    list_filter = ("anonymous", "rating", "created_at", "enterprise")
    ordering = ("-created_at",)

# ------------------------------
# Administración del modelo Comment
# ------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "author", "created_at")
    search_fields = ("text", "author__username", "review__title", "review__enterprise__name")
    list_filter = ("created_at",)
    ordering = ("created_at",)