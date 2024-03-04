from django.urls import path
from . views import *
from . import views


urlpatterns = [
    path('', SupervisorHomeView.as_view(), name='supervisor-home'),
    path('Admin-Dashboard/', SupervisorDashboard.as_view(), name='admin-dashboard'),
    path('AddUser/', CreateUser.as_view(), name='create-user'),
    path('ArchivedUsers/', ArchivedUsers.as_view(), name='archived-users'),
    path('StudentsView/', StudentsView.as_view(), name='students-view'),
    path('TeachersView/', TeachersView.as_view(), name='teachers-view'),
    path('StudentsProfile/<str:email>/', StudentProfile.as_view(), name='students-profile'),
    path('ManageUser/<str:email>/', ManageStudent.as_view(), name='manage-user'),
    path('TeacherProfile/<str:email>/', TeachersProfile.as_view(), name='teachers-profile'),
    path('TeacherInfo/<str:email>/', TeachersInfo.as_view(), name='teachers-info'),
    path('TeachersFinancials/<str:email>/', TeachersFinancials.as_view(), name='teachers-financials'),
    path('StudentsExamProfile/<str:email>/', StudentExamProfile.as_view(), name='students-exam-profile'),
    path('StudentsOptions/<str:email>/', StudentTaskSelect.as_view(), name='students-task-slect'),
    path('StudentsTestView/<str:email>/', StudentTestsView.as_view(), name='students-test-view'),
    path('StudentsTestDetailView/<str:test_type>/<str:email>/<str:test_id>/Test', StudentTestDetailView.as_view(), name='students-test-detail-view'),
    path('Classes/', ClassesView.as_view(), name='classes'),
    path('Classes/<str:class_id>/Info', ClassDetail.as_view(), name='class-profile'),
    path('Classes/<str:class_id>/Ranking/', ClassStudentsRanking.as_view(), name='class-students-ranking'),
    path('tests/', TestTaskView.as_view(), name='test-type'),
    path('ManageClassTeacher/', ManageClassTeacher.as_view(), name='class-teacher'),
   
    path('Classes/<str:class_id>/<str:subject>/<str:term>/Results/', ClassSubjectDetail.as_view(), name='class-subject-detail'),
    path('<str:class_id>/Promote/', Promote.as_view(), name='promote'),
    path('<str:class_id>/ClassTestAnalytics/', ClassTestAnalytics.as_view(), name='class-exam-analytics'),
    path('CreateNotice/', CreateNotice.as_view(),name='create-notice'),
    path('Notices/', Notices.as_view(), name='notices'),
    path('Notice-Update/<str:notice_id>/', NoticeID.as_view(), name='notice-id'),
    path('Create-Activity/', AddActivity.as_view(), name='create-activity'),
    path('AddStudents/', AddStudents.as_view(), name='add-students'),
    path('Add-Files/', AddFiles.as_view(), name='add-files'),
    path('View-activities/', ViewActivities.as_view(), name='activities'),
    path('View-activity/<str:activity_id>/', ViewActivity.as_view(), name='view-activity'),
    path('Enable-Exam-Mode', ExamMode.as_view(), name='exam-mode'),
    path('Print-Card/<str:email>/<str:grade>/<str:term>/<str:rank>/', PrintReport.as_view(), name='print-report'),

]
