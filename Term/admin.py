from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Terms)
admin.site.register(Exam)
admin.site.register(CurrentTerm)
admin.site.register(ClassTermRanking)
admin.site.register(StreamTermRanking)
admin.site.register(Grade)
admin.site.register(GradeModel)