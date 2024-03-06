from django.db.models.signals import post_save

from Finance.models import StudentFeeMpesaTransaction, StudentFeePayment

# from SubjectList.models import MySubjects, Course
from .models import MyUser, PersonalProfile, AcademicProfile, StudentsFeeAccount
from django.dispatch import receiver


@receiver(post_save,sender=MyUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        PersonalProfile.objects.create(user=instance)
        if instance.role == 'Student':
            AcademicProfile.objects.create(user=instance)

        else:
            pass


@receiver(post_save, sender=StudentFeeMpesaTransaction)
def create_student_fee_payment(sender, instance, created, **kwargs):
    """
    Signal receiver to create a StudentFeePayment instance when a StudentFeeMpesaTransaction is created.
    """
    balance = StudentsFeeAccount.objects.get(adm_no=instance.adm_no).balance
    if created:
        # Assuming you have a method to calculate the balance based on the transaction amount
        balance = balance - instance.amount

        # Create a new StudentFeePayment instance
        StudentFeePayment.objects.create(
            user=balance.user,  # Assuming there's a user field in StudentFeeMpesaTransaction
            transaction_id=instance.receipt,
            balance=balance,
        )