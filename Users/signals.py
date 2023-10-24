from django.db.models.signals import post_save

# from SubjectList.models import MySubjects, Course
from .models import MyUser, PersonalProfile, AcademicProfile
from django.dispatch import receiver


@receiver(post_save,sender=MyUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        PersonalProfile.objects.create(user=instance)
        if instance.role == 'Student':
            AcademicProfile.objects.create(user=instance)

        else:
            pass
