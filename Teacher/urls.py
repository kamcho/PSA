from django.urls import path
from .views import *
from . import views



urlpatterns = [
    path('', TeacherView.as_view(), name='teachers-home'),
    path('Class/<str:class>/<str:subject>/', TaskViewSelect.as_view(), name='class-task-view-select'),
    path('<str:class>/<str:subject>/Tests/', TestsView.as_view(), name='teacher-tests-view'),
    path('class/<str:uuid>/Analytics/', ClassTestAnalytics.as_view(), name='class-test-analytics'),
    path('<str:class>/Student-List/', StudentsView.as_view(), name='students-list'),
    path('<str:class>/<str:subject>/Create-Test/', InitialiseCreateTest.as_view(), name='initialise-test'),
    path('load_class/', views.load_class, name='load-class'),
    path('Select-Topic/', ClassTestSelectTopic.as_view(), name='test-topic-select'),
    path('Questions-Selection/', UserQuestionsSelect.as_view(), name='user-question-selection'),
    path('System/Select-Questions/', views.SystemQuestionsSelect, name='system-question-selection'),
    path('get-questions/', views.get_topical_quizzes, name='get_topical_quizzes'),
    path('add-quiz-to-session/', views.add_question_to_session, name='add-quiz-to-session'),
    path('save-test/', SaveTest.as_view(), name='save-test'),
    path('My-Classes/', ClassesView.as_view(), name='my-classes'),
    path('Create-Question/', CreateQuestion.as_view(), name='create-questions'),
    path('load_topics/', views.load_topic, name='load-topics'),
    path('load_subtopics/', views.load_subtopics, name='load-subtopics'),
    path('Add-Answers/', AddAnswerSelection.as_view(), name='add-answer'),
    path('Save-Question/', SaveQuiz.as_view(), name='save-quiz'),
    path('Dashboard/', DashBoard.as_view(), name='dashboard'),
    path('get_subjects/', views.get_subjects, name='get_subjects'),
    path('DashBoard/AcademicProfile/', SubjectSelect.as_view(), name='subjects-selection'),
    path('Subscriptions/', Subscriptions.as_view(), name='subscriptions'),

]
