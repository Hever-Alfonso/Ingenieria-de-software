from django.db import models
from django.conf import settings

class Review(models.Model):
    enterprise = models.ForeignKey(
        "Enterprise", related_name="reviews", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=160)
    body = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # 1 a 5 estrellas
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.enterprise.name} - {self.title} ({self.rating}⭐)"