from django.contrib import admin

from Discipline.models import ClassIncident, IncidentBooking, StudentDisciplineScore

# Register your models here.
admin.site.register(ClassIncident)
admin.site.register(StudentDisciplineScore)
admin.site.register(IncidentBooking)
