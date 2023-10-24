from django.db import models
import uuid
from Users.models import MyUser


class Course(models.Model):
    name = models.CharField(max_length=100)
    discipline = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=1)
    grade = models.CharField(max_length=2)
    topics = models.PositiveIntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class MySubjects(models.Model):
    name = models.ManyToManyField(Course, blank=True, related_name='my_subjects')
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def selected(self):
        if self.name.exists():
            return 'True'
        else:
            return 'False'


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.IntegerField()
    subject = models.ForeignKey(Subject, related_name='subject_id', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    topics_count = models.CharField(max_length=5)
    test_size = models.PositiveIntegerField()
    time = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topic')
    name = models.CharField(max_length=100)
    file1 = models.FileField(upload_to='studyFiles', default='file.pdf')
    file2 = models.FileField(upload_to='studyFiles', default='start.mp4')
    order = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Progress(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subtopic = models.ManyToManyField(Subtopic, related_name='progress_subtopic')
    topic = models.ManyToManyField(Topic, related_name='progress')

    def __str__(self):
        return str(self.user)


class Notifications(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    about = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TopicExamNotifications(Notifications):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class TopicalExamResults(Notifications):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.CASCADE)
    test = models.UUIDField()

    def __str__(self):
        return str(self.user)
    
class PaymentNotifications(Notifications):
    amount = models.PositiveIntegerField()
    subscription_type = models.CharField(max_length=10)
    beneficiaries = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.user)

class AccountInquiries(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    message = models.TextField(max_length=500)
