from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('', Reception.as_view(), name='reception'),
   


]