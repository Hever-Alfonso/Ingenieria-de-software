from django.contrib import admin
from .models import Experience

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("company", "title", "created_at")
    search_fields = ("company", "title", "summary")