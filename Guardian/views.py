import logging
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from Exams.models import StudentTest, StudentsAnswers, ClassTestStudentTest, StudentKNECExams, StudentsKnecAnswers, \
    GeneralTest
from SubjectList.models import Progress, Topic, Subject
from Users.models import MyUser, PersonalProfile, AcademicProfile

logger = logging.getLogger('django')



class IsGuardian(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'Guardian'
    

class GuardianHome(LoginRequiredMixin, IsGuardian, TemplateView):
    """
        Guardians Home Page
    """
    template_name = 'Guardian/guardian_home.html'

    def get_context_data(self, **kwargs):
        context = super(GuardianHome, self).get_context_data(**kwargs)
        user = self.request.user  # get user
        try:
            # Get learners linked to logged in guardian
            my_kids = PersonalProfile.objects.filter(ref_id=user.uuid)  # get linked kids account
            if not my_kids:
                messages.error(self.request, f'We could not find any students in your watch list.'
                                             f' Add a user from your profile page.')
            context['kids'] = my_kids
        except Exception as e:
            # Handle any exceptions
            messages.error(self.request, 'An exception occurred were fixing it')
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
                    'model': 'DatabaseError',

                }
            )

        return context

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            return redirect('profile')




class MyKidsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Guardian view of linked accounts
    """
    template_name = 'Guardian/my_kids_view.html'

    def get_context_data(self, **kwargs):
        context = super(MyKidsView, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            # Get learners linked to logged in guardian
            my_kids = PersonalProfile.objects.filter(ref_id=user.uuid)
            context['kids'] = my_kids
            if not my_kids:
                messages.warning(self.request, f'We could not find any students in your watch list.'
                                             f' Add a user from your profile page.')
                context['kids'] = None
            context['current_time'] = datetime.now()  # Get current time
        except Exception as e:
            messages.error(self.request, 'An error occurred. Do not be alarmed we are fixing the issue')
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
                    'model': 'DatabaseError',

                }
            )


        return context

    def test_func(self):
        return self.request.user.role in ['Guardian', 'Teacher']


class TaskSelection(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Choose to view a learners tests or learning progress
    """
    template_name = 'Guardian/task_select.html'

    def get_context_data(self, **kwargs):
        context = super(TaskSelection, self).get_context_data(**kwargs)
        try:
            email = self.kwargs['email']
            context['email'] = email  # Get a students email from url
            academic_profile = MyUser.objects.get(email=email)
            context['grade'] = academic_profile.academicprofile.current_class.grade



        except AcademicProfile.DoesNotExist as e:
            messages.error(self.request, 'This student has not specified his/her class. Contact @support for assistance')

            profile = AcademicProfile.objects.create(user=academic_profile)
            context['error'] = True
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
                    'model': 'MyUser',

                }
            )

        except AttributeError as e:
            messages.error(self.request, 'This student has not specified his/her class. Contact @support for assistance')
            context['error'] = True
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
                    'model': 'AcademicProfile',

                }
            )




        # choose which base template to use based on roles
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':


            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class KidTests(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View linked students test
    """
    template_name = 'Guardian/kid_tests.html'

    def get_context_data(self, **kwargs):
        context = super(KidTests, self).get_context_data(**kwargs)
        user = self.kwargs['email']
        context['child'] = user
        user = MyUser.objects.get(email=user)

        try:
            # Lists to store subject IDs
            subject_ids = []

            # Retrieve student test data
            student_tests = StudentTest.objects.filter(user=user)
            topical_subject_counts = student_tests.values('subject__id')
            topical_tests = topical_subject_counts.order_by('subject__id')
            print(student_tests)

            # Retrieve class test data
            class_tests = ClassTestStudentTest.objects.filter(user=user)
            class_subject_counts = class_tests.values('test__subject__id')
            my_class_tests = class_subject_counts.order_by('test__subject__id')

            # Retrieve KNEC test data
            knec_tests = StudentKNECExams.objects.filter(user=user)
            knec_subject_counts = knec_tests.values('test__subject__id')
            my_knec_tests = knec_subject_counts.order_by('test__subject__id')

            # Retrieve general test data
            general_tests = GeneralTest.objects.filter(user=user)
            general_subject_counts = general_tests.values('subject__id')
            my_general_tests = general_subject_counts.order_by('subject__id')

            # Collect subject IDs from different types of tests
            if topical_tests:
                for subject_id in topical_tests:
                    subject_ids.append(subject_id['subject__id'])

            if my_general_tests:
                for subject_id in my_general_tests:
                    subject_ids.append(subject_id['subject__id'])

            if my_class_tests:
                for subject_id in my_class_tests:
                    subject_ids.append(subject_id['test__subject__id'])

            if my_knec_tests:
                for subject_id in my_knec_tests:
                    subject_ids.append(subject_id['test__subject__id'])
            # Convert the list of subject IDs to a set to remove duplicates
            subject_ids_set = set(subject_ids)

            # Count the total number of tests
            total_tests_count = (
                    topical_subject_counts.count() +
                    knec_subject_counts.count() +
                    class_subject_counts.count() +
                    general_subject_counts.count()
            )

            # Retrieve the Subject objects with the common subject IDs
            subjects = Subject.objects.filter(id__in=subject_ids_set)
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'

            context['test_count'] = total_tests_count
            context['subjects'] = subjects
            print(subjects)


        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
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
                    'model': 'DatabaseError',

                }
            )

        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class KidExamTopicView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Guardian/kid_exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidExamTopicView, self).get_context_data(**kwargs)
        user = self.kwargs['email']

        try:
            subject = StudentTest.objects.filter(user__email=user, subject__name=self.kwargs['subject']) \
                .values('topic__name', 'subject__grade').order_by('topic').distinct()
            context['subject'] = subject
            knec_test = StudentKNECExams.objects.filter(user__email=user)
            context['tests'] = knec_test
            class_test = ClassTestStudentTest.objects.filter(user__email=user).exclude(
                uuid='c2f49d23-41eb-457a-a147-8e132751774c')
            context['class_tests'] = class_test
            context['subject_name'] = self.kwargs['subject']


        except Exception as e:
            messages.error(self.request, 'An error occurred. Please try again later as we fix this issue.')
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
                    'model': 'DatabaseError',

                }
            )
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        context['email'] = MyUser.objects.filter(email=user).first()

        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class KidExamSubjectDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Guardian/kid_subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidExamSubjectDetail, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']
        topic = self.kwargs['topic']
        user = self.kwargs['email']
        user = MyUser.objects.filter(email=user).first()
        try:
            subject = StudentTest.objects.filter(user=user, subject__name=subject, topic__name=topic)
            context['subject'] = subject


        except Exception as e:
            messages.error(self.request, 'An error occurred when processing your request. Please try again later')
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
                    'model': 'DatabaseError',

                }
            )
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        context['email'] = user

        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class KidTestDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Guardian/kid_test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidTestDetail, self).get_context_data(**kwargs)
        try:
            subject = self.kwargs['name']
            email = self.kwargs['email']
            subject = StudentTest.objects.filter(user__email=email, subject__name=subject)
            context['tests'] = subject
            context['email'] = email
        except Exception as e:
            messages.error(self.request, 'An error occurred when processing your request. Please try again later')

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
                    'model': 'DatabaseError',

                }
            )
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class KidTestRevision(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Guardian/kid_quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidTestRevision, self).get_context_data(**kwargs)
        user = self.kwargs['email']
        test = str(self.kwargs['uuid'])
        instance = self.kwargs['instance']
        user = MyUser.objects.filter(email=user).first()

        try:
            if instance == 'Topical':
                answers = StudentsAnswers.objects.filter(user=user, test_object_id=test)
                test = StudentTest.objects.get(user=user, uuid=test)
            elif instance == 'KNECExams':
                test = StudentKNECExams.objects.filter(user=user, test=test).last()
                answers = StudentsKnecAnswers.objects.filter(user=user, test=test)
            elif instance == 'ClassTests':
                answers = StudentsAnswers.objects.filter(user=user, test_object_id=test)
                test = ClassTestStudentTest.objects.filter(user=user, test=test).last()

            else:
                pass



            context['quizzes'] = answers
            context['marks'] = test


        except Exception as e:
            messages.error(self.request, 'An error occurred when processing your request. Please try again later')

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
                    'model': 'DatabaseError',

                }
            )
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        else:
            context['base_html'] = 'Users/base.html'
        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class LearnerProgress(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View linked students learning progress
    """
    template_name = 'Guardian/learner_progress.html'


    def get_context_data(self, **kwargs):
        context = super(LearnerProgress, self).get_context_data(**kwargs)
        email = self.kwargs['email']  # Get students email from url
        grade = self.kwargs['grade']
        try:
            # Get students progress
            subject = Progress.objects.filter(user__email=email, subject__grade=grade).values('subject__name',
                                                                                               'subject__topics').annotate(
                topic_count=Count('topic', distinct=True))


            context['subject'] = subject
            context['grade'] = grade

        except Exception as e:
            messages.error(self.request, 'An error occurred when processing your request. Please try again later')

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
                    'model': 'DatabaseError',

                }
            )
        # Choose base template based on role
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False


class LearnerSyllabus(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View students syllabus
    """
    template_name = 'Guardian/learners_syllabus.html'

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role == 'Guardian':

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True
        elif user.role == 'Teacher':
            return True

        return False

    def get_context_data(self, **kwargs):
        context = super(LearnerSyllabus, self).get_context_data(**kwargs)
      
        subject = self.kwargs['name']  # Get subject from url
        grade = self.kwargs['grade']
        try:
            # Get all topics by subject
            coverage = Topic.objects.filter(subject__name=subject, subject__grade=grade).order_by('order')
            context['syllabus'] = coverage
            context['subject'] = subject
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'

        except Exception as e:
            messages.error(self.request, 'An error occurred when processing your request. Please try again later')

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
                    'model': 'DatabaseError',

                }
            )

        context['email'] = self.kwargs['email']


        return context
