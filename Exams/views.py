import datetime
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError
from django.shortcuts import redirect
from Guardian.views import IsGuardian

from SubjectList.views import IsStudent
from .models import *
from django.views.generic import TemplateView
from SubjectList.models import TopicalExamResults, TopicExamNotifications

logger = logging.getLogger('django')



class Exams(LoginRequiredMixin, IsStudent, TemplateView):
    """
    Group topical test by subject.
    """
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display user's exams grouped by subject.

        This method fetches the user's exams, groups them by subject, and displays the subjects in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            # Lists to store subject IDs
            subject_ids = []

            # Retrieve student test data
            student_tests = StudentTest.objects.filter(user=user)
            topical_subject_counts = student_tests.values('subject__id')
            topical_tests = topical_subject_counts.order_by('subject__id')

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
            if total_tests_count == 0:
                messages.warning(self.request, 'You have not taken any Examinations !')

            # Retrieve the Subject objects with the common subject IDs
            subjects = Subject.objects.filter(id__in=subject_ids_set)

            context['test_count'] = total_tests_count
            context['subjects'] = subjects


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

    


class ExamTopicView(LoginRequiredMixin, IsStudent, TemplateView):
    """
    Group topical test by topic.
    """
    template_name = 'Exams/exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display exams grouped by topic for a specific subject.

        This method fetches the user's exams for a specific subject, groups them by topic, and displays the topics
        in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(ExamTopicView, self).get_context_data(**kwargs)
        user = self.request.user
        subject_id = self.kwargs['subject']

        try:
            # Retrieve student test data for the subject
            subject_tests = StudentTest.objects.filter(user=user, subject__id=subject_id) \
                .values('topic__name').order_by('topic').distinct()

            # Retrieve KNEC test data for the subject
            knec_tests = StudentKNECExams.objects.filter(user=user, subject__id=subject_id)

            # Retrieve class test data for the subject, excluding a specific UUID
            class_tests = ClassTestStudentTest.objects.filter(user=user, test__subject__id=subject_id)

            # Retrieve General Tests
            general_tests = GeneralTest.objects.filter(user=user, subject__id=subject_id)

            context['subject'] = subject_tests
            context['general'] = general_tests
            context['tests'] = knec_tests
            context['class_tests'] = class_tests
            context['subject_name'] = self.kwargs['subject']
            if not (subject_tests or knec_tests or class_tests):
                messages.info(self.request, 'We could not find results matching your query.')

        except DatabaseError as e:
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

 


class ExamSubjectDetail(LoginRequiredMixin, IsStudent, TemplateView):
    """
    View tests in the selected topic.
    """
    template_name = 'Exams/subject_detail.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display tests for a selected subject and topic.

        This method fetches the user's tests for a specific subject and topic, and displays them in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(ExamSubjectDetail, self).get_context_data(**kwargs)

        # Get subject and topic from URL parameters
        subject_id = self.kwargs['subject']
        topic_name = self.kwargs['topic']

        try:
            # Retrieve tests for the selected subject and topic
            tests = StudentTest.objects.filter(
                user=self.request.user,
                subject__id=subject_id,
                topic__name=topic_name
            )

            context['subject'] = tests
            if not tests:
                messages.info(self.request, 'We could not find results matching your query.')

        except DatabaseError as e:
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




class TestDetail(LoginRequiredMixin, IsStudent, TemplateView):
    template_name = 'Exams/test_detail.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display details of a specific test for the user.

        This method fetches details of a specific test (based on the instance) for the user and displays them in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(TestDetail, self).get_context_data(**kwargs)
        user = self.request.user
        test_uuid = self.kwargs['uuid']
        instance = self.kwargs['instance']
        try:
            test_uuid = uuid.UUID(test_uuid)  # Convert the string to a UUID object
            if instance in ['Topical', 'KNECGradeExams', 'ClassTests', 'GeneralTest']:
                if instance == 'Topical':


                    model = 'StudentTest'
                    answers = StudentsAnswers.objects.filter(user=user, test_object_id=test_uuid)
                    ids = answers.values('quiz')
                  
                    undone_lst = []
                    for item in ids:
                        item = item['quiz']
                        undone_lst.append(item)
                    
                    uuid_strings = [str(uuid) for uuid in undone_lst]
                    

                    
                    test = StudentTest.objects.get(user=user, uuid=test_uuid)
                    undone = test.quiz.exclude(id__in=uuid_strings)
                    context['undone'] = undone

                elif instance == 'KNECGradeExams':

                    model = 'StudentKNECExams'
                    test = StudentKNECExams.objects.get(user=user, test=test_uuid)
                    answers = StudentsKnecAnswers.objects.filter(user=user, test=test)

                elif instance == 'ClassTests':

                    model = 'ClassTestStudentTest'
                    answers = StudentsAnswers.objects.filter(user=user, test_object_id=test_uuid)
                    test = ClassTestStudentTest.objects.get(user=user, test=test_uuid)
                   

                else:
                    model = 'GeneralTest'
                    answers = StudentsAnswers.objects.filter(user=user, test_object_id=test_uuid)
                    test = GeneralTest.objects.get(user=user, uuid=test_uuid)
                    print(answers, test)


                context['quizzes'] = answers
                context['marks'] = test
                context['instance'] = instance
            else:
                messages.error(self.request, 'Invalid URL. Please do not edit the url')

        except ValueError:
            # Handle invalid UUID format
            messages.error(self.request, 'Invalid UUID format. Please do not edit the url !!.')

        except ObjectDoesNotExist as e:
            messages.error(self.request, 'We could not find the test!. please contact @support')
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
                    'model': model,

                }
            )





        except DatabaseError as e:
            messages.error(self.request, 'An error occurred!!. Do not be alarmed we are fixing it.')
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
        # Set the base HTML template based on user role
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        else:
            context['base_html'] = 'Users/base.html'

        return context



class StudentTestLobby(LoginRequiredMixin, IsStudent, TemplateView):
    template_name = 'Exams/start.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display details of the starting point for an exam.

        This method fetches details of a starting point for an exam (based on the topic name) and displays them in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(StudentTestLobby, self).get_context_data(**kwargs)

        try:
            topic_name = self.kwargs['topic']
            test_id = kwargs['uuid']
            user = self.request.user

            # Retrieve the topic based on the 'pk' parameter from the URL
            topics = Topic.objects.get(name=topic_name)
            test = StudentTest.objects.filter(user=user, uuid=test_id)
            print(test, topics)
            if test:
                context['done'] = 'True'
                messages.info(self.request, 'This test has already been done and cannot be retaken.')

            # Check if topic is None (no object found)

            context['topic'] = topics

        except Topic.DoesNotExist as e:
            # Handle the case where no object is found
            context['topic'] = None
            messages.error(self.request, 'An error occurred !!! Dear Student do not edit the url !!')
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
                    'model': 'Topic',

                }
            )

        except Exception as e:
            # Handle other DatabaseError if needed
            messages.error(self.request, 'An error occurred !!! We are fixing it. '
                                         'If the problem persists contact @support')
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

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            user = request.user
            test_uuid = kwargs['uuid']
            topic_name = kwargs['topic']

            try:
                # Retrieve the topic based on the 'pk' parameter from the URL
                topic = Topic.objects.get(name=topic_name)
                test_size = topic.test_size
                duration = topic.time

                print(topic)

                # Create a new StudentTest object
                test = StudentTest.objects.create(
                    user=user,
                    subject=topic.subject,
                    uuid=test_uuid,
                    topic=topic,
                    test_size=test_size,
                    duration=duration
                )

                # Retrieve and add a set of quizzes to the test
                quizzes = TopicalQuizes.objects.filter(topic=topic).order_by('?')[:test_size]
                test.quiz.add(*quizzes)
                
                self.request.session['test_mode'] = 'test_mode'
                try:
                    messages = TopicExamNotifications.objects.get(user=user, uuid=test_uuid).delete()
                except:
                    pass

                # Redirect to the 'tests' view with appropriate arguments
                return redirect('tests', 'Topical', test.uuid)

            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request,
                               'An error occurred and therefore, you cannot take this test at this time!!.'
                               ' Stand by as we fix the issue. Sorry for any inconveniences caused!!')
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
            return redirect(request.get_full_path())




class GeneralTestLobby(LoginRequiredMixin, IsStudent, TemplateView):
    template_name = 'Exams/general_test_lobby.html'

    def get_context_data(self, **kwargs):
        context = super(GeneralTestLobby, self).get_context_data(**kwargs)
        try:
            test_id = self.kwargs['uuid']
            test = GeneralTest.objects.get(uuid=test_id)
            context['test'] = test
        except Exception as e:
            messages.error(self.request, 'We could not find your Test at this moment. Please contact @support.')
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
            test_id = self.kwargs['uuid']
            user = self.request.user
            self.request.session['test_mode'] = 'test_mode'

            try:
                message = TopicExamNotifications.objects.get(user=user, uuid=test_id).delete()

            except:
                pass


            return redirect('tests', 'GeneralTest', test_id)


def get_test_instance(user, instance, test_id):
    try:
        instance_list = ['Topical', 'ClassTests', 'GeneralTest', 'KNECGradeExams']

        test_id = uuid.UUID(test_id)
        if instance in instance_list:

            if instance == 'Topical':
                questions = StudentTest.objects.get(user=user, uuid=test_id)
                instance_type = 'StudentTest'

            elif instance == 'ClassTests':
                questions = ClassTest.objects.get(uuid=test_id)
                instance_type = 'ClassTests'

            elif instance == 'GeneralTest':
                questions = GeneralTest.objects.get(user=user, uuid=test_id)
                instance_type = 'GeneralTest'

            elif instance == 'KNECGradeExams':
                questions = KNECGradeExams.objects.get(uuid=test_id)
                instance_type = 'KNECGradeExams'

            return questions, instance_type
        else:
            raise ValueError



    except MultipleObjectsReturned:
        raise MultipleObjectsReturned

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist  # Return None for both questions and instance_type if the object does not exist
    except ValueError:
        raise ValueError


    except Exception:
        raise Exception


class Tests(LoginRequiredMixin, IsStudent, TemplateView):
    template_name = 'Exams/tests.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        test_mode = self.request.session.get('test_mode', None)
        if test_mode:
            test_id = kwargs['uuid']
            instance = self.kwargs['instance']

            user = self.request.user
            question_index = self.request.session.get('index', 0)
            try:
                questions, instance_type = get_test_instance(user=user, instance=instance, test_id=test_id)
                context['test'] = questions

                context['instance_type'] = instance_type
                if questions:
                    test_size = questions.quiz.all().count()
                    print(test_size)
                    self.request.session['test_size'] = test_size
                    self.request.session['instance_type'] = instance_type

                    if question_index >= len(questions.quiz.all()):
                        context['message'] = "Test is completed."

                    else:
                        current_question = questions.quiz.all()[question_index]
                        self.request.session['quiz'] = str(current_question)

                        if instance_type == 'KNECGradeExams':
                            choices = KnecQuizAnswers.objects.filter(quiz=current_question)

                        else:
                            choices = TopicalQuizAnswers.objects.filter(quiz=current_question).order_by('?')
                        correct_choice = choices.filter(is_correct=True)
                        print(choices.count())
                        if int(choices.count()) != 4 or correct_choice is None:
                            messages.error(self.request, 'This test is not complete try it later')
                            context['invalidate'] = True
                        else:
                            context['choices'] = choices
                            context['quiz'] = current_question
                            context['index'] = question_index + 1
                            numbers = [i + 1 for i in range(len(questions.quiz.all()))]
                            context['list'] = numbers
                            context['instance'] = instance

                            context['test_id'] = test_id

            except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
                messages.error(self.request, 'An error occurred while getting this test. Contact @support')
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
                        'model': 'TESTS',

                    }
                )

            except ValueError as e:
                messages.error(self.request, 'Invalid UUID or Test format !! Do not edit the url.')
                context['error'] = True

            except Exception as e:
                messages.error(self.request, f'An exception occurred and we are fixing it!! {e}')
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
                        'model': 'DatabaseError',

                    }
                )
        else:
            context['test_mode'] = None

        return context

    def post(self, request, **kwargs):

        if request.method == 'POST':
            test_mode = self.request.session.get('test_mode', None)
            if test_mode:
                try:
                    test_size = request.session.get('test_size')
                    user = request.user
                    instance = self.kwargs['instance']
                    test_id = kwargs['uuid']
                    selection = request.POST.get('choice')  # Get the selected choice ID from the POST data
                    question_index = request.session.get('index', 0)
                    # test = self.get_context_data().get('test')
                    # instance_type = self.get_context_data().get('instance_type')
                    test, instance_type = get_test_instance(user, instance, test_id)

                    if instance_type == 'KNECGradeExams':
                        quiz = KnecQuizzes.objects.filter(id=request.session['quiz']).first()
                        selection = KnecQuizAnswers.objects.filter(uuid=selection).first()
                        correct = KnecQuizAnswers.objects.filter(uuid=selection.uuid, is_correct=True).first()
                    else:

                        quiz = TopicalQuizes.objects.filter(id=request.session['quiz']).first()
                        selection = TopicalQuizAnswers.objects.filter(uuid=selection).first()
                        correct = selection if selection.is_correct else None
                        # correct = TopicalQuizAnswers.objects.filter(uuid=selection.uuid, is_correct=True).first()

                    if correct:
                        if instance_type == 'ClassTests':
                            student_test = ClassTestStudentTest.objects.get(user=user, test=test)
                            student_test.marks = int(student_test.marks) + 1
                            student_test.save()
                            is_correct = True
                        elif instance_type == 'KNECGradeExams':
                            student_test = StudentKNECExams.objects.get(user=user, test=test)
                            student_test.marks = int(student_test.marks) + 1
                            student_test.save()
                            is_correct = True


                        else:
                            test.marks = int(test.marks) + 1
                            test.save()
                            is_correct = True

                    else:
                        is_correct = False

                    if instance_type == 'KNECGradeExams':
                        test_uuid = StudentKNECExams.objects.get(user=user, test=test_id)
                        answer = StudentsKnecAnswers.objects.create(user=user, quiz=quiz,
                                                                    selection=selection,
                                                                    is_correct=is_correct, test=test_uuid)
                    else:

                        answer = StudentsAnswers.objects.create(user=user, quiz=quiz, test_object_id=test.uuid,
                                                                selection=selection,
                                                                is_correct=is_correct)
                    if question_index >= int(test_size) - 1:
                        # The exam is completed, redirect to a summary page
                        if 'index' in request.session:
                            del request.session['index']
                            del request.session['test_mode']

                        return redirect('finish', instance, test_id)

                    else:

                        request.session['index'] = question_index + 1
                        return redirect(request.path)


                except (MultipleObjectsReturned, ObjectDoesNotExist, IntegrityError) as e:
                    messages.error(self.request, 'An error occurred! Please contact support!')
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
                            'model': 'TESTS',

                        }
                    )

                except ValueError:
                    messages.error(self.request, 'Invalid UUID or Test format !! Do not edit the url.')

                except Exception as e:
                    messages.error(self.request, f'An exception occurred. please try again later as we fix this issues !')
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
                            'model': 'Exception',

                        }
                    )

                messages.error(self.request, 'Invalid test configurations')
            return redirect('students-home')
        return redirect(self.request.get_full_path())



class Finish(LoginRequiredMixin, IsStudent, TemplateView):
    template_name = 'Exams/finish.html'

    def get_context_data(self, **kwargs):
        context = super(Finish, self).get_context_data(**kwargs)
        test_id = self.kwargs['uuid']
        # topic = self.kwargs['pk']
        instance = self.kwargs['instance']

        user = self.request.user
        context['test_uuid'] = test_id
        try:
            test, instance_type = get_test_instance(user, instance, test_id)
            print(test, instance_type)
            message = f'Congratulations on completing your test. The results' \
                      ' are out, click the button below to view the results. '
            if instance_type in ['ClassTests', 'StudentTest', 'GeneralTest']:
                # try:









                if instance_type == 'ClassTests':
                    about = f'The results for {test.teacher} assignment is out.'
                    print(about)
                    notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about,
                                                                      message=message, subject=test.subject,
                                                                      notification_type='class-results')
                    marks = ClassTestStudentTest.objects.get(user=user, test=test_id)
                    context['score'] = marks.marks
                    context['test'] = marks
                    context['size'] = test.test_size
                    context['instance'] = instance

                elif instance == 'GeneralTest':
                    about = f'The results  are out.'
                    notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about,
                                                                      message=message, subject=test.subject,
                                                                      notification_type='general-results',
                                                                      )
                    context['score'] = test.marks

                    context['test'] = test


                else:
                    topic = test.topic
                    print(test)
                    about = f'The results for {topic} are out.'
                    notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about,
                                                                      message=message, subject=test.subject,
                                                                      notification_type='topical-results',
                                                                      topic=topic)
                    context['score'] = test.marks

                    context['test'] = test


            elif instance_type == 'KNECGradeExams':
                about = 'Your results for this terms KNEC exams are out. Click the button below to view results.'
                notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about,
                                                                  message=message, subject=test.subject,
                                                                  notification_type='knec-results',
                                                                  )
                marks = StudentKNECExams.objects.get(user=user, test=test_id)
                context['score'] = marks.marks
                context['test'] = marks
                context['size'] = test.test_size
                context['instance'] = instance_type
                print(instance_type, test_id)

        except Exception as e:
            messages.error(self.request, 'An error occurred. Do not be alarmed we have already saved your test.'
                                         ' You can view the results from Exam page')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.warning(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Warning',
                    'model': 'Exception',
                    'object_id':test_id

                }
            )


        return context


class SetTest(LoginRequiredMixin, IsGuardian, TemplateView):
    """
    View for setting a test for a specific subject.
    """
    template_name = 'Exams/set_test.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the set test page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'subject'.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(SetTest, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']

        try:
            # Attempt to retrieve topics related to the specified subject
            topics = Topic.objects.filter(subject__id=subject)

            context['topics'] = topics

        except Exception as e:
            # Handle any exceptions that may occur
            messages.error(self.request, 'An error occurred while fetching topics for the test. Please try again.')
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
                    'model': 'Exception',

                }
            )

        return context

    def post(self, request, **kwargs):
        if self.request.method == "POST":

            user = self.kwargs['mail']
            user = MyUser.objects.get(email=user)
            subject = self.kwargs['subject']
            subject = Subject.objects.get(id=subject)
            topics = self.request.POST.getlist('topics')
            print(topics[0])
            exam_type = self.request.POST.get('exam-type')

            test_size = self.request.POST.get('size')
            test_size = int(test_size)
            if topics:
                try:
                    test_id = uuid.uuid4()
                    date = datetime.datetime.now()

                    message = 'The test you requested is now available, Good luck.'

                    if exam_type == 'Topical':
                        topic = Topic.objects.get(id=topics[0])
                        about = f'You have a new test. View more info below.(topical){topic}'

                        notification = TopicExamNotifications.objects.create(user=user, about=about,
                                                                             notification_type='retake',
                                                                             subject=subject,
                                                                             date=date,
                                                                             message=message,
                                                                             topic=topic
                                                                             )
                    else:
                        about = f'You have a new test. View more info below.'

                        notification = TopicExamNotifications.objects.create(user=user, about=about,
                                                                             notification_type='general',
                                                                             date=date,
                                                                             uuid=test_id,
                                                                             subject=subject, message=message,
                                                                             )

                    test = GeneralTest.objects.create(user=user, subject=subject, uuid=test_id)
                    failed_quiz = StudentsAnswers.objects.filter(is_correct=False, quiz__topic__in=topics).order_by('?')[:3]
                    quizes = TopicalQuizes.objects.filter(topic__in=topics)
                    done_quiz = StudentsAnswers.objects.filter(quiz__topic__in=topics)

                    new_quiz = quizes.exclude(id__in=done_quiz).order_by('?')[:test_size - 3]
                    failed_count = int(failed_quiz.count())
                    new_count = int(new_quiz.count())

                    if failed_count >= 3 and new_count >= 12:
                        test.quiz.add(*failed_quiz)
                        test.quiz.add(*new_quiz)

                    elif failed_count <= 3 and new_count >= 12:

                        # new_quiz = quizes.exclude(uuid__in=done_quiz).order_by('?')[:(test_size-failed_count)]
                        test.quiz.add(*failed_quiz)
                        test.quiz.add(*new_quiz)
                        quizzes = quizes.order_by('?')[:test_size]
                        test.quiz.add(*quizzes)

                    else:
                        questions = TopicalQuizes.objects.filter(topic__in=topics).order_by('?')[:test_size]
                        test.quiz.add(*questions)

                    return redirect('guardian-home')
                except Exception as e:
                    messages.error(self.request, 'We could not create a test at this time. Please contact @support')
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
                            'model': 'Exception',

                        }
                    )
                    return redirect(self.request.get_full_path())
            else:
                messages.error(self.request, 'Please select a topic to continue !')
                return redirect(self.request.get_full_path())

    


class KNECExamView(LoginRequiredMixin, IsStudent, TemplateView):
    """
    View for displaying KNEC exams for a specific grade.
    """
    template_name = 'Exams/knec_exam_view.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the KNEC exam view page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'grade'.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(KNECExamView, self).get_context_data(**kwargs)
        grade = self.kwargs['grade']

        try:
            # Attempt to retrieve the subjects for the specified grade
            subjects = KNECGradeExams.objects.filter(grade=grade)
            if not subjects:
                messages.info(self.request, 'We could not find Tests matching your query!')

            context['subjects'] = subjects
            context['grade'] = grade

        except Exception as e:
            # Handle any exceptions that may occur
            messages.error(self.request, 'An error occurred while fetching KNEC exams. We are fixing this issue.'
                                         'Try again later.')
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
                    'model': 'KNECGradeExams',

                }
            )

        return context


class KNECExamList(LoginRequiredMixin, IsStudent, TemplateView):
    """
    View for listing KNEC exams for a specific grade and subject.
    """
    template_name = 'Exams/knec_exam_list.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the KNEC exam list page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'grade' and 'subject'.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(KNECExamList, self).get_context_data(**kwargs)
        grade = self.kwargs['grade']
        subject = self.kwargs['subject']

        try:
            # Attempt to retrieve the KNEC exams for the specified grade and subject
            exams = KNECGradeExams.objects.filter(grade=grade, subject__id=subject)

            context['exams'] = exams
            context['grade'] = grade
            if not exams:
                messages.info(self.request, 'There are no tests matching your query.')

        except Exception as e:
            # Handle any exceptions that may occur
            messages.error(self.request, 'An error occurred while fetching KNEC exams. We are fixing this issue.'
                                         'Try again later.')
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
                    'model': 'KNECGradeExams',

                }
            )


        return context


class StartKnec(LoginRequiredMixin, IsStudent, TemplateView):
    """
    View for starting a KNEC exam.
    """
    template_name = 'Exams/start_knec.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare context data for rendering the exam start page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'uuid' and 'grade'.

        Returns:
            dict: Context data for rendering the template.
        """
        context = super(StartKnec, self).get_context_data(**kwargs)
        test_uuid = self.kwargs['uuid']
        grade = self.kwargs['grade']

        try:
            # Attempt to retrieve the KNEC exam based on UUID and grade
            test = KNECGradeExams.objects.get(uuid=test_uuid, grade=grade)
            context['test'] = test

        except Exception as e:
            # Handle the case where no matching exam is found or multiple tests are found
            messages.error(self.request, 'We could not process your request at this time. Please contact @support')
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
                    'model': 'KNECGradeExams',

                }
            )

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to start a KNEC exam.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Keyword arguments from the URL, including 'uuid' and 'grade'.

        Returns:
            HttpResponseRedirect: Redirects to the appropriate exam page.
        """
        if request.method == "POST":
            user = self.request.user
            test_uuid = self.kwargs['uuid']

            try:
                # Attempt to retrieve the KNEC exam based on UUID and grade
                knec_test = self.get_context_data().get('test')
                subject = Subject.objects.get(id=knec_test.subject.id)

                # Create a StudentKNECExams object for the user
                student_test = StudentKNECExams.objects.create(user=user, subject=subject, test=knec_test)

                # Redirect to the KNEC exam page
                return redirect('tests', 'KNECGradeExams', test_uuid)


            except Exception as e:
                # Handle no subject found
                messages.error(request, 'There was an error starting this test. Please contact @support')
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

        return redirect(request.get_full_path())  # Redirect to the appropriate page on error
        
