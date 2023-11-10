from django.urls import path
# from django.contrib.auth import views as auth_views
from .views import Partner

urlpatterns = [

    path('Partner-Home/', Partner.as_view(), name='partner-home'),
   

]
