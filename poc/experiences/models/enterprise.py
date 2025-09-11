from django.db import models
from django.db.models import Avg

class Enterprise(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    AI_summary  = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def reviews_count(self):
        """Devuelve el número real de reviews asociadas a esta empresa."""
        return self.reviews.count()

    @property
    def average_rating(self):
        """Devuelve el promedio de estrellas de todas las calificaciones."""
        result = self.reviews.aggregate(avg=Avg("rating"))
        return result["avg"] or 0
