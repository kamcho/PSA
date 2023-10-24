from django.urls import path,include
from django.contrib.auth import views as auth_views

from Logs.views import HLogs

urlpatterns = [

    path('logs/', HLogs.as_view(), name='logging')


]