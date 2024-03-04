from django.urls import path
from .views import Exams, ExamTopicView,  ExamSubjectDetail, TestDetail,\
    StudentTestLobby, Tests, Finish, SetTest, GeneralTestLobby

urlpatterns = [

    path('<str:grade>/', Exams.as_view(), name='exams'),
    path('<str:subject>/TopicInfo', ExamTopicView.as_view(), name='exam-topic-id'),
    path('<str:subject>/<str:topic>/Info', ExamSubjectDetail.as_view(), name='exam-subject-id'),
    path('Test/<str:instance>/<str:uuid>/Revision/', TestDetail.as_view(), name='test-detail'),
    path('<str:topic>/<str:uuid>/Instructions', StudentTestLobby.as_view(), name='start'),
    path('<str:uuid>/General-Test', GeneralTestLobby.as_view(), name='general-test'),
    path('<str:instance>/<str:uuid>/Quiz/', Tests.as_view(), name='tests'),
    path('<str:instance>/<str:uuid>/Finish/', Finish.as_view(), name='finish'),
    path('<str:mail>/<str:subject>/set-test/', SetTest.as_view(), name='set-test'),
   
   

]
