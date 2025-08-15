from django.db import models

class Experience(models.Model):
    company = models.CharField(max_length=120)
    title = models.CharField(max_length=160)
    summary = models.CharField(max_length=240)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} — {self.title}"