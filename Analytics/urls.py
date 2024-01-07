from .views import *
from . import views
from django.urls import path

urlpatterns = [
    path('<str:mail>/Analytics/', OverallAnalytics.as_view(), name='overall-analytics'),
    path('<str:mail>/<str:subject>/Review/', SubjectAnalytics.as_view(), name='subject-analysis'),
    path('Subjects/<str:grade>/', SubjectView.as_view(), name='subject-view'),
    path('<str:id>/Analysis/', SubjectAnalysis.as_view(), name='subject-id-analysis'),



    ]