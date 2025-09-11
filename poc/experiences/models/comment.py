# experiences/models/comment.py
from django.db import models
from django.conf import settings

class Comment(models.Model):
    review = models.ForeignKey(
        "experiences.Review",
        related_name="comments",
        on_delete=models.CASCADE,
        help_text="Review a la que pertenece este comentario",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="review_comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]  # comentarios más antiguos primero
        indexes = [models.Index(fields=["review", "created_at"])]

    def __str__(self):
        who = self.author.username if self.author else "anónimo"
        return f"Comment by {who} on review {self.review_id}"
