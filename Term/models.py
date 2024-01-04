from pyexpat import model
from django.db import models
from SubjectList.models import Subject

from Users.models import MyUser, SchoolClass

# Create your models here.
class Terms(models.Model):
    choices = (
        ('Term 1','Term 1'),
        ('Term 2', 'Term 2'),
        ('Term 3', 'Term 3')
    )
    term = models.CharField(max_length=10, choices=choices)
    year = models.CharField(max_length=10)
    starts_at = models.DateField(auto_created=True, null=True)
    ends_at = models.DateField(auto_created=True, null=True)


    def __str__(self):
        return str(self.term)
    
class CurrentTerm(models.Model):
  
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


class Grade(models.Model):
    grade = models.PositiveIntegerField()

    def __str__(self):
            return str(self.grade)
class ClassTermRanking(models.Model):
    term = models.ForeignKey(Terms, on_delete=models.CASCADE)
    class_id = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    grade = models.PositiveIntegerField()
    file = models.FileField(upload_to='files/')

    def __str__(self):
        return str(self.class_id) + ' ' + str(self.grade)+ ' ' + str(self.term)

    
class StreamTermRanking(models.Model):
    class_id = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    grade = models.PositiveIntegerField()
    file = models.FileField(upload_to='files/')

    def __str__(self):
        return str(self.class_id) + ' ' + str(self.grade)