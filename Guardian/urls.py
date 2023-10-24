from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from . import views
# app_name = 'Guardian'
urlpatterns = [
    path('My-Kids/', MyKidsView.as_view(), name='my-kids'),
    path('', GuardianHome.as_view(), name='guardian-home'),
    path('Learner/<str:email>/', views.TaskSelection.as_view(), name='task-view-select'),
    path('Guardian/<str:email>/test-/quiz/', KidTests.as_view(), name='kid-test'),
    path('<str:email>/<str:subject>/TopicInfo', KidExamTopicView.as_view(), name='kid-exam-topic-id'),
    path('<str:email>/<str:subject>/<str:topic>/Info', KidExamSubjectDetail.as_view(), name='kid-exam-subject-id'),
    path('<str:instance>/<str:email>/<str:uuid>/Test-Revision/', KidTestRevision.as_view(), name='kid-test-revision'),
    path('Quiz/<str:email>/<str:name>/', KidTestDetail.as_view(), name='kid-tests-detail'),
    path('View/<str:email>/<str:grade>/progress/', LearnerProgress.as_view(), name='learner-learning-progress'),
    path('<str:name>/<str:grade>/<str:email>/syllabus-coverage/', LearnerSyllabus.as_view(), name='learners-syllabus'),

]