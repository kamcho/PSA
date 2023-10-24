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


class KnecQuizzes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    # subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    # topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    quiz = models.TextField(max_length=500)

    def __str__(self):
        return str(self.id)

    # class Meta:
    #     managed = False


class KnecQuizAnswers(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    # quiz = models.ForeignKey(KnecQuizzes, on_delete=models.CASCADE)
    choice = models.CharField(max_length=600)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.uuid)

    # class Meta:
    #     managed = False
