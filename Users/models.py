
from enum import unique
import random
from django.db import models

# Create your models here.
import uuid

from django.db import models

from django.urls import reverse
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

# from Teacher.models import SchoolClass


class MyUserManager(BaseUserManager):
    def create_user(self, email, role, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        user = self.model(


            email=email,
            role=role,
            # adm_no=adm_no,



        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(

            email=email,
            role='Admin',
            # uuid=uuid.uuid4(),
            password=password,
            # adm_no=adm_no

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    class Role(models.TextChoices):
        Student = "Student"
        Teacher = "Teacher"
        ADMIN = "ADMINISTRATOR"
        Guardian = "Guardian"
        Supervisor = "Supervisor"
        Finance = "Finance"
        Receptionist = "Receptionist"


    base_role = Role.Student
    # adm_no = models.CharField(max_length=15, unique=True, default=uuid.uuid4)

    email = models.EmailField(unique=True)
    adm_no = models.CharField(max_length=100, default=random.randint(15784, 999999))
    uuid = models.CharField(max_length=100, default=str(uuid.uuid4), unique=True)
    
    role = models.CharField(max_length=15, choices=Role.choices, default=base_role)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'


    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class TeacherManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs)
        return result.filter(role=MyUser.Role.Teacher)


class Teacher(MyUser):
    base_role = MyUser.Role.Teacher
    teacher = TeacherManager()

    class Meta:
        proxy = True


class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Student)


class Student(MyUser):
    base_role = MyUser.Role.Student
    student = StudentManager()

    class Meta:
        proxy = True


class GuardianManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Guardian)


class Guardian(MyUser):
    base_role = MyUser.Role.Guardian
    guardian = GuardianManager()

    class Meta:
        proxy = True


class SupervisorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Supervisor)


class Supervisor(MyUser):
    base_role = MyUser.Role.Supervisor
    partner = SupervisorManager()

    class Meta:
        proxy = True

class ReceptionistManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Receptionist)


class Receptionist(MyUser):
    base_role = MyUser.Role.Receptionist
    partner = ReceptionistManager()

    class Meta:
        proxy = True

class FinanceManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=MyUser.Role.Finance)


class Finance(MyUser):
    base_role = MyUser.Role.Finance
    partner = SupervisorManager()

    class Meta:
        proxy = True

class SchoolClass(models.Model):
    class_id = models.UUIDField(default=uuid.uuid4, unique=True)
    grade = models.PositiveIntegerField()
    class_name = models.CharField(max_length=100)
    class_size = models.PositiveIntegerField(default=30)
    class_teacher = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.grade) + ' ' + str(self.class_name)
    
    class Meta:
        unique_together = ('grade', 'class_name')
    
    

class AcademicProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)

    current_class = models.ForeignKey(SchoolClass, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
    
class PersonalProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=30)
    ref_id = models.CharField(max_length=100, blank=True)
    l_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.user.email
    

class TeacherPaymentProfile(models.Model):
    options = (
        ('Phone', 'Phone'),
        ('Bank', 'Bank')
    )
    
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    salary = models.PositiveIntegerField(default=20000)
    default_payment = models.CharField(max_length=100, choices=options)

    def __str__(self):
        return self.user.email
    


class StudentsFeeAccount(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email



class Schools(models.Model):
    name = models.CharField(max_length=300, unique=True)
    school_id = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return self.name

