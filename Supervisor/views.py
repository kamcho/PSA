import datetime

from itertools import groupby

from urllib import request
from django import contrib
from django.db.models import F, IntegerField, Count, Sum
from django.core.exceptions import ObjectDoesNotExist

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.utils import timezone
from django.views.generic import TemplateView
from Finance.models import MpesaPayouts
from Teacher.models import StudentList, TeacherProfile
from Term.models import ClassTermRanking, CurrentTerm, Exam
from Users.models import AcademicProfile, MyUser, PersonalProfile, SchoolClass, StudentsFeeAccount, TeacherPaymentProfile
from Exams.models import ClassTestStudentTest, GeneralTest, StudentTest, TopicalQuizes, TopicalQuizAnswers
from SubjectList.models import Subject, Topic, Subtopic, Course


class SupervisorHomeView(TemplateView):
    template_name = 'Supervisor/supervisor_home.html'

    def get_context_data(self, **kwargs):
        context = super(SupervisorHomeView, self).get_context_data(**kwargs)
        return context



class SupervisorDashboard(TemplateView):
    template_name = 'Supervisor/admin_dashboard.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        current_term = CurrentTerm.objects.all().first()
        print(current_term)
        if current_term:
            context['current_term'] = current_term
        else:
            context['current_term'] = False


        return context



class CreateUser(TemplateView):
    template_name = 'Supervisor/create_user.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        classes = SchoolClass.objects.all()
        context['classes'] = classes
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                email = request.POST.get('email')
                f_name = request.POST.get('f_name')
                l_name = request.POST.get('l_name')
                surname = request.POST.get('surname')
                role = request.POST.get('role')
                gender = request.POST.get('gender')
                print(role,f_name)
                if role == 'Student':
                    class_id = request.POST.get('class')
                    user = MyUser.objects.create(email=email, role=role, password='defaultpwd')
                    profile = PersonalProfile.objects.get(user=user)
                    print(profile, '\n\n\n\n\n\n')
                    class_id = SchoolClass.objects.get(class_name=class_id)
                    profile.f_name = f_name
                    profile.l_name = l_name
                    profile.surname = surname
                    profile.gender = gender
                    profile.save()
                    academia = AcademicProfile.objects.get(user=user)
                    academia.current_class = class_id
                    academia.save()

                    return redirect('students-profile', email)
            
                elif role in ['Teacher', 'Supervisor']:
                    user = MyUser.objects.create(email=email, role=role, password='defaultpwd')
                    profile = PersonalProfile.objects.get(user=user)
                    profile.f_name = f_name
                    profile.l_name = l_name
                    profile.surname = surname
                    profile.save()

                    return redirect(request.get_full_path())
            except IntegrityError:
               messages.error(self.request, 'A user with this email/adm_no already exists !') 
            except Exception:
                messages.error(self.request, 'We could not save the user. Contact @support')

            return redirect(request.get_full_path())






class StudentsView(TemplateView):
    template_name = 'Supervisor/students_view.html'

    def get_context_data(self, **kwargs):
        context = super(StudentsView, self).get_context_data(**kwargs)
        try:
            params = self.request.session.get('params', None)
            if params:
                users = PersonalProfile.objects.filter(Q(f_name__contains=params) | Q(l_name__contains=params)
                                                    | Q(surname__contains=params) | Q(user__email__contains=params) ).values_list('user__email')
                users = MyUser.objects.filter(email__in=users, role='Student')
                if not users:
                    messages.warning(self.request, 'We could not find any users matching your query')
            else:
                users  = MyUser.objects.filter(role='Student', is_active=True)
            context['users'] = users
        except Exception:
            messages.error(self.request, 'We could not fetch students from the database')
        return context
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            context = super(StudentsView, self).get_context_data(**kwargs)

            params = request.POST.get('search')
            if params:

                
                self.request.session['params'] = params
            else:
                try:
                    del self.request.session['params']
                except KeyError:
                    pass
                
            return redirect(request.get_full_path())
        

class TeachersView(TemplateView):
    template_name = 'Supervisor/teachers_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            params = self.request.session.get('params', None)
            if params:
                users = PersonalProfile.objects.filter(Q(f_name__contains=params) | Q(l_name__contains=params)
                                                    | Q(surname__contains=params) | Q(user__email__contains=params) ).values_list('user__email')
                users = MyUser.objects.filter(email__in=users, role='Teacher')
                if not users:
                    messages.warning(self.request, 'We could not find any users matching your query')
            else:
                users  = MyUser.objects.filter(role='Teacher', is_active=True)
            context['users'] = users
        except Exception:
            messages.error(self.request, 'We could not fetch Teachers from the database')
        return context
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            params = request.POST.get('search')
            if params:

                
                self.request.session['params'] = params
            else:
                try:
                    del self.request.session['params']
                except KeyError:
                    pass
                
            return redirect(request.get_full_path())
        

class TeachersProfile(TemplateView):
    template_name = 'Supervisor/teachers_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        user = MyUser.objects.get(email=email)
        my_class = StudentList.objects.filter(user=user)
        context['classes'] = my_class
        context['teacher'] = user

        return context
    
class TeachersInfo(TemplateView):
    template_name = 'Supervisor/teacher_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        user = MyUser.objects.get(email=email)
        my_class = StudentList.objects.filter(user=user)
   
            # get teacher profile
       
        context['classes'] = my_class
        context['teacher'] = user

        return context
class TeachersFinancials(TemplateView):
    template_name = 'Supervisor/teacher_financials.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        try:
            profile = TeacherPaymentProfile.objects.get(user__email=email)
            context['profile'] = profile
        except ObjectDoesNotExist:
            try:
                user = MyUser.objects.get(email=email)
                profile = TeacherPaymentProfile.objects.create(user=user)
                context['profile'] = profile
            except:
                messages.error(self.request, 'An error occured !!. Please DO NOT edit the url')
        payouts = MpesaPayouts.objects.filter(user__email=email)
        context['payouts'] = payouts
        return context


class StudentProfile(TemplateView):
    template_name = 'Supervisor/students_profile.html'

    def get_context_data(self, **kwargs):
        context = super(StudentProfile, self).get_context_data(**kwargs)
        email = self.kwargs['email']
        user  = MyUser.objects.get(email=email)
        subjects = Subject.objects.filter(grade=4)
        
        context['subjects'] = subjects
        context['user'] = user
        return context
    


    
class ManageStudent(TemplateView):
    template_name = 'Supervisor/manage_student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        email = self.kwargs['email']
        student = MyUser.objects.get(email=email)
        classes = SchoolClass.objects.all()
        context['classes'] = classes
        context['student'] = student

        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            email = request.POST.get('email')
            f_name = request.POST.get('f_name')
            l_name = request.POST.get('l_name')
            surname = request.POST.get('surname')
            class_id = request.POST.get('class')

            gender = request.POST.get('gender')

            if 'update' in request.POST:
                email = self.kwargs['email']
                profile = PersonalProfile.objects.get(user__email=email)
                if profile.user.role == 'Student':
                    class_id = SchoolClass.objects.get(class_id=class_id)
                    acd_profile = AcademicProfile.objects.get(user__email=email)
                    acd_profile.current_class = class_id
                    acd_profile.save()
                profile.f_name = f_name
                profile.l_name = l_name
                profile.surname = surname
                profile.gender = gender
                profile.save()
                

                return redirect(request.get_full_path())
            elif 'delete' in request.POST:
                user = MyUser.objects.get(email=email)
                user.is_active = False
                user.save()
                messages.info(request, f'You have succesfully deleted {email} from Students Database')
                return redirect('students-view')

            else:
                user = MyUser.objects.get(email=email)
                user.is_active = True
                user.save()
                messages.success(request, f'You have succesfully restored {email} and all acount related data')
                return redirect(self.request.get_full_path())

                
            

class ArchivedUsers(TemplateView):
    template_name = 'Supervisor/archived_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = MyUser.objects.filter(is_active='False')
        context['users'] = users

        return context


            

class StudentExamProfile(TemplateView):
    template_name = 'Supervisor/students_exam_profile.html'

    def get_context_data(self, **kwargs):
        context = super(StudentExamProfile, self).get_context_data(**kwargs)
        email = self.kwargs['email']
        user  = MyUser.objects.get(email=email)
        grade = self.request.session.get('grade', 4)
        scores = Exam.objects.filter(user__email=email, subject__grade=grade) 
        term1 = scores.filter(term__term='Term 1')
        term2 = scores.filter(term__term='Term 2')
        term3 = scores.filter(term__term='Term 3')
        context['term1'] = term1
        context['term2'] = term2
        context['term3'] = term3

        context['scores'] = scores
        context['grade'] = grade
        context['user'] = user
        return context
    
    def post(self, *args, **kwargs):
      
        if self.request.method == 'POST':
            selected = self.request.POST.get('select')
           
            self.request.session['grade'] = selected

            return redirect(self.request.get_full_path())



class StudentTaskSelect(TemplateView):
    template_name = 'Supervisor/student_task_select.html'

    def get_context_data(self, **kwargs):
        context = super(StudentTaskSelect, self).get_context_data(**kwargs)
        email = self.kwargs['email']
        user  = MyUser.objects.get(email=email)
        context['user'] = user
        return context


class StudentTestsView(TemplateView):
    template_name = 'Supervisor/students_test_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        context['email'] = email
        tests = StudentTest.objects.filter(user__email=email)
        class_tests = ClassTestStudentTest.objects.filter(user__email=email)
        general_tests = GeneralTest.objects.filter(user__email=email)
        if not tests and not class_tests and not general_tests:
            messages.warning(self.request, 'This user has not taken any tests')
        
        context['class_tests'] = class_tests
        context['general_tests'] = general_tests
        context['tests'] = tests
        return context


class StudentTestDetailView(TemplateView):
    template_name = 'Supervisor/students_test_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        test_id = self.kwargs['test_id']
        test_type = self.kwargs['test_type']
        try:
            if test_type == 'TopicalTest':
                test = StudentTest.objects.get(user__email=email, uuid=test_id)
                context['status'] = test.archived
            elif test_type == 'ClassTest':
                test = ClassTestStudentTest.objects.get(user__email=email, uuid=test_id)
                context['status'] = test.archived
            elif test_type == 'GeneralTest':
                test = GeneralTest.objects.get(user__email=email, uuid=test_id)
                context['status'] = test.archived
            else:
                messages.error(self.request, 'Invalid Test')
            context['test'] = test

        except :
            messages.error(self.request, 'We could not find this test')

        return context

    def post(self, *args, **kwargs):
        if self.request.method == "POST":

            try:
                if 'delete' in self.request.POST:
                    test_type = self.kwargs['test_type']
                    email = self.kwargs['email']
                    test_id = self.kwargs['test_id']
                    if test_type == 'TopicalTest':
                        test = StudentTest.objects.get(user__email=email, uuid=test_id)
                        test.archived = True
                        test.save()
                    elif test_type == 'ClassTest':
                        test = ClassTestStudentTest.objects.get(user__email=email, uuid=test_id)
                        test.archived = True
                        test.save()
                    elif test_type == 'GeneralTest':
                        test = GeneralTest.objects.get(user__email=email, uuid=test_id)
                        test.archived = True
                        test.save()
                    else:
                        messages.error(self.request, 'Invalid Test')
                elif 'restore' in self.request.POST:
                    test_type = self.kwargs['test_type']
                    email = self.kwargs['email']
                    test_id = self.kwargs['test_id']
                    if test_type == 'TopicalTest':
                        test = StudentTest.objects.get(user__email=email, uuid=test_id)
                        test.archived = False
                        test.save()
                    elif test_type == 'ClassTest':
                        test = ClassTestStudentTest.objects.get(user__email=email, uuid=test_id)
                        test.archived = False
                        test.save()
                    elif test_type == 'GeneralTest':
                        test = GeneralTest.objects.get(user__email=email, uuid=test_id)
                        test.archived = False
                        test.save()
                    else:
                        messages.error(self.request, 'Invalid Test')

            except:
                pass

            return redirect(self.request.get_full_path())
        

class ClassesView(TemplateView):
    template_name = 'Supervisor/classes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classes = SchoolClass.objects.all()
        context['classes'] = classes
        return context     
    
class ClassDetail(TemplateView):
    template_name = 'Supervisor/class_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_id = SchoolClass.objects.get(class_name=class_id)
        context['class'] = class_id
        year = self.request.session.get('year', None)
        term = self.request.session.get('term', 'Term 1')
        if year:
            context['subjects'] = subjects = Subject.objects.filter(grade=year)
            print(subjects)
        else:
            subjects = Subject.objects.filter(grade=class_id.grade)
            context['subjects'] = subjects
            year = class_id.grade
            # print(subjects)

        context['term'] = term
        context['grade'] = year
        
        
        return context
    
    def post(self, request, **args):
        if request.method == 'POST':
            year = request.POST.get('year')
            term = request.POST.get('term')
            request.session['year'] = year
            request.session['term'] = term


            return redirect(request.get_full_path())

class ClassStudentsRanking(TemplateView):
    template_name='Supervisor/class_students_ranking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_instance = SchoolClass.objects.get(class_id=class_id)
        grade = self.request.session.get('year', None)
        term = self.request.session.get('term', None)
        stream = self.request.session.get('stream', False)
        
        if not grade:
            grade = class_instance.grade
        if not term:
            term = CurrentTerm.objects.all().first()
        if stream:
            # file = ClassTermRanking.objects.filter(class_id__class_id=class_id, grade=grade, term__term=term).last()
            # context['file'] = file

            context['class_id'] = class_instance
            class_id = SchoolClass.objects.filter(grade=class_instance.grade)
            context['classes'] = class_id
            class_id = class_id.values_list('class_id')
            print(class_id)

        

            scores = (
            Exam.objects
            .filter(user__academicprofile__current_class__class_id__in=class_id, subject__grade=grade, term__term=term)
            .values('user__personalprofile__f_name', 'user__email', 'user__personalprofile__l_name', 'user__personalprofile__surname', 'user__academicprofile__current_class__class_name')  # Group by the user
            .annotate(total_score=Sum('score'))
            .order_by('-total_score', 'user')  # Order by total_score descending, user ascending
        )
            context['stream'] = True

        else:
            file = ClassTermRanking.objects.filter(class_id__class_id=class_id, grade=grade, term__term=term).last()
            context['file'] = file

            context['class_id'] = class_instance
        
            scores = (
            Exam.objects
            .filter(user__academicprofile__current_class__class_id=class_id, subject__grade=grade, term__term=term)
            .values('user__personalprofile__f_name', 'user__email', 'user__personalprofile__l_name', 'user__personalprofile__surname')  # Group by the user
            .annotate(total_score=Sum('score'))
            .order_by('-total_score', 'user')  # Order by total_score descending, user ascending
        )
        ranked_students = []
        current_rank = 0

        for key, group in groupby(scores, key=lambda student: student['total_score']):
            score_group = list(group)
            
            # Assign the same rank to students with the same score
            for student in score_group:
                student['rank'] = current_rank + 1
            
            # Skip the following rank
            current_rank += len(score_group)

            # Append students to the result list
            ranked_students.extend(score_group)
                
        subjects = Subject.objects.filter(grade=grade)
        context['subjects'] = subjects
        context['students'] = ranked_students
        context['term'] = term
        context['grade'] = grade

        return context
    
    
    

    def post(self, request, **kwargs):
        if request.method == 'POST':
            grade = request.POST.get('year')
            term = request.POST.get('term')
            stream = request.POST.get('stream')

            if stream == 'stream':
                request.session['stream'] = grade
            else:
                request.session['stream'] = None


                
            
            request.session['year'] = grade
            request.session['term'] = term
            




        return redirect(request.get_full_path())


def rank(marks_object):
        
    return marks_object
class ClassSubjectDetail(TemplateView):
    template_name = 'Supervisor/class_subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        class_name = SchoolClass.objects.get(class_id=class_id)
        subject = self.kwargs['subject']
        term = self.kwargs['term']
        scores = Exam.objects.filter(user__academicprofile__current_class__class_id=class_id, subject__id=subject, term__term=term).order_by('-score')
        context['tests'] = scores
        context['class'] = class_name
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
