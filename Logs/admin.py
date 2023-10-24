from django.contrib import admin

# Register your models here.
from Logs.models import LogEntry

admin.site.register(LogEntry)