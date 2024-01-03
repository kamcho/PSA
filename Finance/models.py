from enum import unique
from pyexpat import model
from django.db import models
from Term.models import Terms

from Users.models import MyUser

# Create your models here.

class Invoices(models.Model):
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    amount = models.PositiveIntegerField()
    balance = models.PositiveIntegerField(default=0)
    description = models.TextField(max_length=1000)
    received_from = models.CharField(max_length=50)
    contact_info = models.CharField(max_length=15)

    def __str__(self):
        return str(self.received_from)
    
class InvoicePayments(models.Model):
    date = models.DateTimeField(auto_now=True)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    balance = models.PositiveIntegerField()
    cleared = models.BooleanField(default=False)

    def __str__(self):
        return str(self.invoice.received_from) + ' ' + str(self.amount)

class InitiatedPayments(models.Model):
    choices = (
         ('Remedial', 'Remedial'),
         ('Invoice', 'Invoice'),
         ('Salary', 'Salary')
    )
    date = models.DateTimeField(auto_now=True)
    tracking_id = models.CharField(max_length=100, null=True)
    checkout_id = models.CharField(max_length=100, unique=True)
    beneficiaries = models.ManyToManyField(MyUser, null=True)
    amount = models.PositiveIntegerField(default=100)
    purpose = models.CharField(max_length=300, choices=choices)

    def __str__(self):
        return str(self.checkout_id)


class ProcessedPayments(models.Model):
    initiator_id = models.ForeignKey(InitiatedPayments, on_delete=models.CASCADE)
    processed_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100)
    status = models.BooleanField()

    def __str__(self):
        return str(self.initiator_id)
    
# class SalaryPayouts(models.Model):
#     user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now=True)
#     transaction_id = models.ForeignKey(MpesaPayouts, on_delete=models.CASCADE)
    
     

class MpesaPayouts(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    checkout_id = models.ForeignKey(ProcessedPayments, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()
    balance = models.PositiveIntegerField()
    receipt = models.CharField(max_length=15)

    def __str__(self):
        return str(self.user.email)
    

class SalaryPayouts(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    transaction_id = models.ForeignKey(MpesaPayouts, on_delete=models.CASCADE)
    

class TermFeeStructure(models.Model):
    term = models.ForeignKey(Terms, on_delete=models.CASCADE)
    grade = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()

    def __str__(self):
            return str(self.term.year) + ' ' + str(self.term.term) + ' ' + str(self.grade)
    
class StudentFeeMpesaTransaction(models.Model):
    receipt = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    adm_no = models.CharField(max_length=10)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
            return str(self.adm_no)
    
class StudentFeePayment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    transaction_id = models.ForeignKey(StudentFeeMpesaTransaction, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
            return str(self.user)
    
    


