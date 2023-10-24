import datetime

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.utils import timezone
from django.views.generic import TemplateView

from Exams.models import TopicalQuizes, KNECGradeExams, TopicalQuizAnswers
from SubjectList.models import Subject, Topic, Subtopic, Course
from Supervisor.models import KnecQuizzes, KnecQuizAnswers, Schools


class SupervisorHomeView(TemplateView):
    template_name = 'Supervisor/supervisor_home.html'

    def get_context_data(self, **kwargs):
        context = super(SupervisorHomeView, self).get_context_data(**kwargs)
        return context


class TestTaskView(TemplateView):
    template_name = 'Supervisor/test_type_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class KNECExamConfig(TemplateView):
    """
        A view to set test configurations of a given test
    """
    template_name = 'Supervisor/knec_config.html'

    def get_context_data(self, **kwargs):
        context = super(KNECExamConfig, self).get_context_data(**kwargs)
        try:
            subjects = Course.objects.all()  # Get all subjects
            tests = KNECGradeExams.objects.all()  # Get all exams
            context['session_data'] = self.request.session.get('knec_config', None)
            context['tests'] = tests
            context['subjects'] = subjects
        except Exception:
            messages.error(self.request, 'An error occurred, if problem persists contact support')
        return context

    def post(self, request):
        if request.method == "POST":
            date = datetime.datetime.now().strftime('%Y')
            user = request.user

            # Get data from form
            p_subject = request.POST.get('subject')
            grade = request.POST.get('grade')
            term = request.POST.get('term')
            test_size = request.POST.get('test_size')
            try:
                subject = Subject.objects.get(name=p_subject, grade=grade)  # Get subject by id

                # Try and check if an exam matching the same criteria exists
                test = KNECGradeExams.objects.filter(grade=grade, subject__id=subject.id, term=term, year=date).first()
                if test:
                    test_id = test.uuid
                else:
                    # create if none is found
                    knec_test = KNECGradeExams.objects.create(teacher=user, grade=grade, subject=subject, term=term,
                                                              test_size=test_size, year=date, date=timezone.now())
                    test_id = knec_test.uuid

                # Add data to session
                knec_config = {'subject': subject.id, 'grade': grade, 'term': term, 'year': date}
                request.session['knec_config'] = knec_config

                return redirect('knec-add-quiz', subject, test_id)

            except Exception:
                messages.error(self.request, 'An error occurred but we are fixing it')

                return redirect(request.get_full_path())


class KNECAddQuiz(TemplateView):
    """
        Add a question to the test
    """
    template_name = 'Supervisor/knec_add_quiz.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            test_id = self.kwargs['uuid']
            subject_id = self.request.session.get('knec_config')['subject']
            test = KNECGradeExams.objects.get(uuid=test_id)  # get exam
            context['subject'] = test.subject  # get subject

            context['term'] = self.request.session.get('knec_config')['term']
            context['test_id'] = test_id

            context['count'] = test.quiz.all().count()  # get total number of questions added
        except Exception:
            # Hanlde any exceptions
            messages.error(self.request, 'An error occurred, were fixing it')

        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":  # Corrected method name to uppercase
            url_subject = self.kwargs['subject']
            test_id = self.kwargs['uuid']

            # get data from form
            quiz = request.POST.get('quiz')
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            sub_topic = request.POST.get('subtopic')

            if quiz and sub_topic and subject and topic:  # ensure all data is available

                # Parse data and add it to session
                data = {'quiz': quiz, 'subject': subject, 'topic': topic, 'subtopic': sub_topic}
                request.session['quiz'] = data
                return redirect('knec-add-selection', subject, test_id)
            else:
                return redirect('knec-add-quiz', url_subject, test_id)


class KNECAddSelection(TemplateView):
    """
        View to add choices to previous added question
    """
    template_name = 'Supervisor/knec_add_selection.html'

    def get_context_data(self, **kwargs):
        context = super(KNECAddSelection, self).get_context_data(**kwargs)
        context['quiz'] = self.request.session.get('quiz')  # get question from session

        return context

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            # get data from url
            subject = self.kwargs['subject']
            test_id = self.kwargs['uuid']

            # get data from form
            selection1 = self.request.POST.get('selection1')
            selection2 = self.request.POST.get('selection2')
            selection3 = self.request.POST.get('selection3')
            selection4 = self.request.POST.get('selection4')

            if selection1 and selection2 and selection3 and selection4:
                # Parse data and add to session
                self.request.session['selection_info'] = {'selection1': selection1,
                                                          'selection2': selection2,
                                                          'selection3': selection3,
                                                          'selection4': selection4
                                                          }
                return redirect('save-knec-quiz', subject, test_id)

            else:
                return redirect('knec-add-selection', subject, test_id)


def parse_quiz(request):
    # Parse data
    session_quiz_data = request.session.get('quiz')
    topic = session_quiz_data['topic']
    sub_topic = session_quiz_data['subtopic']
    quiz = session_quiz_data['quiz']
    session_selection_data = request.session.get('selection_info')
    selection1 = session_selection_data['selection1']
    selection2 = session_selection_data['selection2']
    selection3 = session_selection_data['selection3']
    selection4 = session_selection_data['selection4']
    return sub_topic, topic, quiz, selection1, selection2, selection3, selection4


def save_selection(test_quiz, selection1, selection2, selection3, selection4):
    # Bulk create questions
    quiz_answers = [
        KnecQuizAnswers(quiz=test_quiz, choice=selection1, is_correct=True),
        KnecQuizAnswers(quiz=test_quiz, choice=selection2, is_correct=False),
        KnecQuizAnswers(quiz=test_quiz, choice=selection3, is_correct=False),
        KnecQuizAnswers(quiz=test_quiz, choice=selection4, is_correct=False),
    ]  # Parse data
    try:
        with transaction.atomic():
            KnecQuizAnswers.objects.bulk_create(quiz_answers)  # Bulk create
    except Exception:
        pass
    return None


class SaveQuiz(TemplateView):
    template_name = 'Supervisor/save_quiz.html'

    def get_context_data(self, **kwargs):
        context = super(SaveQuiz, self).get_context_data(**kwargs)
        try:
            quiz = self.request.session.get('quiz')
            context['quiz'] = quiz
            context['selection'] = self.request.session.get('selection_info')
            context['subject'] = Subtopic.objects.get(subject=quiz['subject'])  # get subtopic
        except Exception:
            messages.error(self.request, 'An error occurred and you are required to restart this process again')

        return context

    def post(self, request, **kwargs):
        # handle POST requests
        if request.method == 'POST':
            test_id = self.kwargs['uuid']
            subject = self.kwargs['subject']
            try:

                sub_topic, topic, quizz, selection1, selection2, selection3, selection4 = parse_quiz(request)  # get data from session
                db_sub_topic = Subtopic.objects.get(id=sub_topic)  # get subtopic

                # Create question
                test_quiz = KnecQuizzes.objects.create(subject=db_sub_topic.subject, topic=db_sub_topic.topic,
                                                       subtopic=db_sub_topic,
                                                       quiz=quizz)
                save_selection(test_quiz, selection1, selection2, selection3, selection4)  # create choices

                # Get test and add question to it
                knec_test = KNECGradeExams.objects.get(uuid=test_id)
                knec_test.quiz.add(test_quiz)

            except Exception:
                # Handle any errors
                messages.error(self.request, 'An error occurred, Contact support')

                return redirect(request.get_full_path())



        return redirect('knec-add-quiz', subject, test_id)


class TestReview(TemplateView):
    """
        A view to review test info and questions
    """
    template_name = 'Supervisor/test_review.html'

    def get_context_data(self, **kwargs):
        context = super(TestReview, self).get_context_data(**kwargs)
        try:
            test_id = self.kwargs['uuid']
            test = KNECGradeExams.objects.get(uuid=test_id)  # get knec exams
            quiz_uuids = [quiz.quiz for quiz in test.quiz.all()]
            context['quizzes'] = test.quiz.all()  # get all questions in that test
        except Exception:
            messages.error(self.request, 'Ann error occurred, Contact support')

        return context


class SchoolSelect(TemplateView):
    """
         A view to view all schools
    """
    template_name = 'Supervisor/school_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            schools = Schools.objects.all()  # get all schools
            context['schools'] = schools

        except Exception:
            messages.error(self.request, 'An error occurred')
        return context


class SchoolTaskSelect(TemplateView):
    """
        View tasks operation possible
    """
    template_name = 'Supervisor/school_task_select.html'

    def get_context_data(self, **kwargs):
        uuid = self.kwargs['uuid']
        try:
            context = super(SchoolTaskSelect, self).get_context_data(**kwargs)
            school = Schools.objects.get(uuid=uuid)  # get a specific school
            context['school'] = school
        except Exception:
            messages.error(self.request, 'An error occurred were fixing it')

        return context
