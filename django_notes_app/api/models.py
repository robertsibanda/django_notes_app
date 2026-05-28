from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    """Model representing a note belonging to a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self) -> str:
        """Return the first 50 characters of the note body."""
        return self.body[:50] if self.body else ""
    
