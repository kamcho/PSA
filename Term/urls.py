from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('Class/<str:class_id>/<str:subject>/Add-Scores/', AddSubjectScore.as_view(), name='add-score'),
    path('', TermListView.as_view(), name='terms'),
    path('<str:term>/', TermInfo.as_view(), name='term-info')


]