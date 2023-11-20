from pyexpat import model
from django.db import models
from SubjectList.models import Subject

from Users.models import MyUser

# Create your models here.
class Terms(models.Model):
    choices = (
        ('Term 1','Term1'),
        ('Term 2', 'Term 2'),
        ('Term 3', 'Term 3')
    )
    term = models.CharField(max_length=10, choices=choices)
    year = models.CharField(max_length=10)


    def __str__(self):
        return str(self.term)
    
class CurrentTerm(models.Model):
    choices = (
        ('Term 1','Term 1'),
        ('Term 2', 'Term 2'),
        ('Term 3', 'Term 3')
    )
    term = models.ForeignKey(Terms, on_delete=models.CASCADE)
    mode = models.BooleanField(default=False)
  


    def __str__(self):
        return str(self.term)
    
class Exam(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Terms, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    comments = models.TextField(max_length=100)

    class Meta:
        unique_together = ('user', 'subject', 'term')

    def __str__(self):
        return str(self.user)

