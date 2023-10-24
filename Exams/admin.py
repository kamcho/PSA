from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(TopicalQuizes)
admin.site.register(TopicalQuizAnswers)
admin.site.register(StudentTest)
admin.site.register(StudentsAnswers)
admin.site.register(ClassTest)
admin.site.register(ClassTestStudentTest)
admin.site.register(KNECGradeExams)
admin.site.register(StudentKNECExams)
admin.site.register(GeneralTest)