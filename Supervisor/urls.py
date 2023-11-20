from django.urls import path
from . views import *
from . import views


urlpatterns = [
    path('', SupervisorHomeView.as_view(), name='supervisor-home'),
    path('AddUser/', CreateUser.as_view(), name='create-user'),
    path('StudentsView/', StudentsView.as_view(), name='students-view'),
    path('StudentsProfile/<str:email>/', StudentProfile.as_view(), name='students-profile'),
    path('STudentsExamProfile/<str:email>/', StudentExamProfile.as_view(), name='students-exam-profile'),
    path('StudentsOptions/<str:email>/', StudentTaskSelect.as_view(), name='students-task-slect'),
    path('StudentsTestView/<str:email>/', StudentTestsView.as_view(), name='students-test-view'),
    path('StudentsTestDetailView/<str:test_type>/<str:email>/<str:test_id>/Test', StudentTestDetailView.as_view(), name='students-test-detail-view'),
    path('Classes/', ClassesView.as_view(), name='classes'),
    path('Classes/<str:class_id>/Info', ClassDetail.as_view(), name='class-profile'),
    path('tests/', TestTaskView.as_view(), name='test-type'),
    path('Knec-config/', KNECExamConfig.as_view(), name='knec-config'),
    path('<str:subject>/<str:uuid>/Add-Quiz/', KNECAddQuiz.as_view(), name='knec-add-quiz'),
    path('<str:subject>/<str:uuid>/Add-Selection/', KNECAddSelection.as_view(), name='knec-add-selection'),
    path('<str:subject>/<str:uuid>/Save-Question/', SaveQuiz.as_view(), name='save-knec-quiz'),
    path('Scools/', SchoolSelect.as_view(), name='schools'),
    path('Schools/<str:uuid>/Home', SchoolTaskSelect.as_view(), name='school'),
    path('<str:uuid>/Review/', TestReview.as_view(), name='knec-test-review'),

]
