from django.urls import path
from . views import *
from . import views










urlpatterns = [
    path('', SupervisorHomeView.as_view(), name='supervisor-home'),
    path('tests/', TestTaskView.as_view(), name='test-type'),
    path('Knec-config/', KNECExamConfig.as_view(), name='knec-config'),
    path('<str:subject>/<str:uuid>/Add-Quiz/', KNECAddQuiz.as_view(), name='knec-add-quiz'),
    path('<str:subject>/<str:uuid>/Add-Selection/', KNECAddSelection.as_view(), name='knec-add-selection'),
    path('<str:subject>/<str:uuid>/Save-Question/', SaveQuiz.as_view(), name='save-knec-quiz'),
    path('Scools/', SchoolSelect.as_view(), name='schools'),
    path('Schools/<str:uuid>/Home', SchoolTaskSelect.as_view(), name='school'),
    path('<str:uuid>/Review/', TestReview.as_view(), name='knec-test-review'),

]
