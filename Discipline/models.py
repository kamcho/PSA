from django.db import models

from Users.models import MyUser

# Create your models here.

class ClassIncident(models.Model):
    incident_degree = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    points = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)
    

class StudentDisciplineScore(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=100)

    def __str__(self):
        return str(self.user)

    
class IncidentBooking(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    incident = models.ForeignKey(ClassIncident, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    booked_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='booker')

    def __str__(self):
        return str(self.user)
