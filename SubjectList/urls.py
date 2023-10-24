from django.urls import path
from SubjectList.views import Learning, MediaSelect, Read, Assignment, Finish, AssignmentDetail, Syllabus, Messages, MyProgress, \
    ContactUs

urlpatterns = [

    path('Grade-<str:grade>/Subjects/', Learning.as_view(), name='learn'),
    path('E-Learning/<str:topic> /<str:subtopic>/<str:media>/Study', Read.as_view(), name='read'),
    path('Assignments/', Assignment.as_view(), name='assignments'),
    path('<str:uuid>/Assignment-Lobby', AssignmentDetail.as_view(), name='assignment-lobby'),
    path('Save/<str:topic> /<str:subtopic>/Save-Progress/', Finish.as_view(), name='save-progress'),
    path('<str:subject_id>/Syllabus-Coverage/', Syllabus.as_view(), name='syllabus'),
    path('<str:topic>/<str:subtopic>/Media-Select/', MediaSelect.as_view(), name='media' ),
    path('Notifications/', Messages.as_view(), name='notifications'),
    path('Grade-<str:grade>/Learning-Progress', MyProgress.as_view(), name='progress'),
    path('Support/', ContactUs.as_view(), name='contact')

]
