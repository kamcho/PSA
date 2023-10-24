from django.db import models
from django.db import models

from Users.models import MyUser


class LogEntry(models.Model):
    ERROR_LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    app_name = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)  # URL that caused the error
    school = models.UUIDField()
    level = models.CharField(max_length=10, choices=ERROR_LEVEL_CHOICES)  # Error level
    error_type = models.CharField(max_length=100)  # Error type (e.g., ValueError, KeyError)
    message = models.TextField()  # Error message
    user = models.ForeignKey(MyUser, related_name='caller', on_delete=models.SET_NULL, blank=True, null=True)  # User associated with the error
    model = models.CharField(max_length=100, blank=True, null=True)  # Model associated with the error
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp when the error occurred
    object_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.error_type}: {self.message}"
