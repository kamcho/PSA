import uuid as uuid
from django.db import models
import uuid
# Create your models here.
from Exams.models import TopicalQuizes, TopicalQuizAnswers, ClassTest
from SubjectList.models import Subject, Topic, Subtopic,  Notifications
from Users.models import MyUser, SchoolClass


class TeacherProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    subject = models.ManyToManyField(Subject)

    def __str__(self):
        return str(self.user)


class StudentList(models.Model):
    user = models.ForeignKey(MyUser, related_name='teacher_user', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, default='9', on_delete=models.CASCADE)
    class_id = models.ForeignKey(SchoolClass, default='1', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class ClassTestNotifications(Notifications):
    test = models.ForeignKey(ClassTest, on_delete=models.CASCADE)
    class_id = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.test)
