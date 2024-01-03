import uuid
from django.db import models
from SubjectList.models import Subject, Topic, Subtopic


class Schools(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    school_type = models.CharField(max_length=100, default='Primary')

    def __str__(self):
        return str(self.name)

    class Meta:
        managed = False
