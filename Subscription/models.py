import datetime

from django.db import models

# Create your models here.
from Users.models import MyUser


class Subscriptions(models.Model):
    type = models.CharField(max_length=30,unique=True)
    amount = models.PositiveIntegerField()
    validity = models.CharField(max_length=10)

    def __str__(self):
        return str(self.type)


class MySubscription(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    expiry = models.DateField(auto_created=True, default=datetime.date.today )
    status = models.BooleanField(default=False)
    type = models.ForeignKey(Subscriptions, to_field='type', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def active(self):
        today = datetime.date.today()
        if self.user.role == 'Student' and today > self.expiry:
            return 'Subscription Expired'
        elif self.user.role == 'Student' and self.expiry > today:
            return 'Active'
        else:
            return self.user.role


class StripeCardPayments(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    transact_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    brand = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now=True)
    created = models.CharField(max_length=15)
    type = models.CharField(max_length=100, default='Platinum')
    student_list = models.CharField(max_length=100, default='Null')

    def __str__(self):
        return str(self.user)
