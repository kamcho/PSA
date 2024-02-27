from turtle import mode
import uuid
from django.db import models
from SubjectList.models import Subject, Topic, Subtopic


class Updates(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(max_length=500)
    date = models.DateField(auto_now=True)
    file = models.FileField(upload_to='Updates/', null=True)

    def __str__(self):
        return str(self.title)
