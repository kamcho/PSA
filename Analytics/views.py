import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.db.models import Count
from django.views.generic import TemplateView
from Exams.models import *
from Teacher.models import *
from Users.models import PersonalProfile

logger = logging.getLogger('django')


class IsStudent(UserPassesTestMixin):
    """
        ensure email passed is that of a student
    """
    def test_func(self):
        user_email = self.kwargs['mail']  # Get the user's email from the URL
        try:
            if self.request.user.role == 'Teacher':
                return True
            elif self.request.user.role == 'Guardian':
                student = MyUser.objects.get(email=user_email)
                user = self.request.user.uuid
                # Get a user with the passed email
                student = PersonalProfile.objects.get(user__email=user_email)

                return student.ref_id == user  # limits viewership to students in watch list only
            else:
                return False
        except PersonalProfile.ObjectDoesNotExist:

            profile = PersonalProfile.objects.create(user__email=user_email)
            # Any exceptions occurrence limits view
            return False
        except Exception:
            return False


class OverallAnalytics(LoginRequiredMixin, IsStudent, TemplateView):
    """
        view students tests analysis
    """
    template_name = 'Analytics/overall_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(OverallAnalytics, self).get_context_data(**kwargs)
        user_email = self.kwargs['mail']  # Get the user's email from the URL

        try:
            # Try to retrieve the user by their email

            # Fetch analytics data for the user's tests
            tests = StudentTest.objects.filter(user__email=user_email).values('subject__id') \
                .annotate(subject_count=Count('subject__name')).order_by('subject__name').distinct()

            context['tests'] = tests
            context['child'] = MyUser.objects.get(email=user_email)
            if not tests:
                messages.info(self.request, 'We could not find tests to analyse')

        except Exception as e:
            # Handle other unexpected errors
            messages.error(self.request, 'An error occurred. We are fixing it.')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'StudentKNECExams',

                }
            )

        return context


class SubjectAnalytics(LoginRequiredMixin, IsStudent, TemplateView):
    """
        View students performance on a given subject
    """
    template_name = 'Analytics/subject_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(SubjectAnalytics, self).get_context_data(**kwargs)
        user = self.kwargs['mail']
        subject = self.kwargs['subject']

        try:
            user = MyUser.objects.get(email=user)  # get student's instance
            subject = Subject.objects.get(id=subject)  # get subject
            subject = subject.id  # get subject id
            student_tests = StudentTest.objects.filter(user=user, subject__id=subject)  # get topical tests
            class_test = ClassTestStudentTest.objects.filter(user=user, test__subject__id=subject)  # get class tests
            test_count = int(student_tests.count()) + int(class_test.count())
            context['total_tests'] = test_count

            weakness = StudentsAnswers.objects.filter(user=user, quiz__subject__id=subject, is_correct=False). \
                values('quiz__topic__name').annotate(
                Count('quiz__topic__name')).order_by('quiz__topic__name')

            strength = StudentsAnswers.objects.filter(user=user, quiz__subject__id=subject, is_correct=True). \
                values('quiz__topic__name').annotate(
                Count('quiz__topic__name')).order_by('quiz__topic__name')

            context['subject'] = subject
            context['strength'] = strength
            context['weakness'] = weakness
            context['child'] = user
            if test_count == 0:
                messages.info(self.request, 'We could not find students data to analyse.')

        # Handle any errors

        except Subject.DoesNotExist:
            # Handle subject does not exist
            messages.error(self.request, 'Subject not found !!! did you edit the url if not contact us.')


        except Exception as e:
            # Handle any other exceptions

            messages.error(self.request, 'An error occurred. Try again later as we fix the issue.')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'StudentKNECExams',

                }
            )


        return context
