from django.db import models
from django.contrib.auth.models import User  # <-- agregar

class Experience(models.Model):
    company = models.CharField(max_length=120)
    title   = models.CharField(max_length=160)
    summary = models.CharField(max_length=240)
    body    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # <-- nuevo