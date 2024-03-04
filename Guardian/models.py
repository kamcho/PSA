from django.db import models

from Users.models import MyUser

# Create your models here.


class MyKids(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    kids = models.ManyToManyField(MyUser, related_name='kids')

    def __str__(self):
        return str(self.user)