import logging
import math
from django.db import DatabaseError
from django.db.models import Count, F

from django import template
from django.db.models import Sum
from django.shortcuts import redirect
import datetime

from Exams.models import StudentTest, StudentsAnswers, ClassTestStudentTest, ClassTest,  GeneralTest, \
    TopicalQuizes, TopicalQuizAnswers
from Finance.models import Invoices
from SubjectList.models import *
from Term.models import Exam

from Users.models import MyUser, SchoolClass

register = template.Library()
logger = logging.getLogger('django')

@register.filter
def divide(value, arg):
    try:
        value = int(value)
        arg = int(arg)
        return round((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def progress(subject_id, count):
    try:
        subtopics = Subtopic.objects.filter(subject__id=subject_id).count()
        print(subtopics, count)
        progress = (count / subtopics) * 100
        progress = round(progress, 0)
        return progress
    except Exception as e:
        print(str(e))
        return 0


@register.filter
def get_user_progress_topic(user, subject):
    subject = Subject.objects.get(id=subject)
    progress = Progress.objects.filter(user=user, subject=subject).last()
    if progress:
        try:
            current_subtopic = progress.subtopic.last()  # Get the latest subtopic
            if current_subtopic:
                return current_subtopic

        except Subtopic.DoesNotExist:
            try:
                introduction = Topic.objects.filter(subject=subject).last()
                introduction = Subtopic.objects.filter(topic=introduction).last()
                return introduction
            except Topic.DoesNotExist:
                return None
            except Subtopic.DoesNotExist:
                return None
    else:
        try:
            introduction = Topic.objects.filter(subject=subject).last()
            introduction = Subtopic.objects.filter(topic=introduction).last()
            return introduction
        except Topic.DoesNotExist:
            return None
        except Subtopic.DoesNotExist:
            return None


@register.filter
def topic_in_progress(user, topic):
    try:
        progress = Progress.objects.filter(user=user, topic=topic)
        if progress:
            return True
        else:
            return False

    except Exception as e:
        return False


@register.filter
def guardian_topic_view(email, topic):
    try:
        user = MyUser.objects.get(email=email)
        progress = Progress.objects.filter(user=user, topic=topic)
        if progress.exists():
            return True
        else:
            return False


    except Exception as e:
        return False


@register.filter
def subtopic_in_progress(user, subtopic):
    try:
        progress = Progress.objects.filter(user=user, subtopic=subtopic)
        if progress:
            return True
        else:
            return False

    except Exception as e:
        return False


@register.filter
def guardian_subtopic_view(email, subtopic):
    try:
        user = MyUser.objects.get(email=email)
        progress = Progress.objects.filter(user=user, subtopic=subtopic)
        if progress:
            return True
        else:
            return False

    except Exception as e:
        return False


@register.filter
def test_is_done(user, test_uuid):
    try:
        class_test = ClassTestStudentTest.objects.filter(user=user, test=test_uuid)
        student_test = StudentTest.objects.filter(user=user, uuid=test_uuid)
        if student_test or class_test :

            return True
        else:
            return False

        return True

    except DatabaseError:
        return False


@register.filter
def class_test_progress(test_uuid):
    class_test = ClassTest.objects.filter(uuid=test_uuid).last()
    class_id = class_test.class_id
    student_count = SchoolClass.objects.filter(class_name=class_id).first()
    test_count = ClassTestStudentTest.objects.filter(test=test_uuid).count()

    return f' {test_count} / {student_count.class_size} '


@register.filter
def class_test_average(test_uuid):
    tests = ClassTestStudentTest.objects.filter(test=test_uuid)
    test = ClassTest.objects.filter(uuid=test_uuid).first()
    total_marks = tests.aggregate(total_marks=Sum('marks'))['total_marks']
    if int(tests.count()) == 0:
        return 0
    else:
        average = (int(total_marks) / int(tests.count()))
        average = round(average)

        return f'{average} / {test.test_size} '


@register.filter
def class_test_active(date):
    if datetime.date.today() > date:
        return True
    else:
        return False


@register.filter
def split_value(value, delimiter):
    return value.split(delimiter)[0]


@register.filter
def topical_average(user, topic):
    tests = StudentTest.objects.filter(user=user, topic__name=topic)

    total_marks = tests.aggregate(total_marks=Sum('marks'))['total_marks']
    average = round(int(total_marks) / int(tests.count()))
    return average


@register.filter
def topical_average_count(user, topic):
    tests = StudentTest.objects.filter(user=user, topic__name=topic)
    return tests.count()


@register.filter
def subject_analytics_marks(user, subject):
    student_test = StudentTest.objects.filter(subject__id=subject, user=user)
    sum_marks_and_test_sizes = student_test.aggregate(total_marks=Sum('marks'))
    total_marks = sum_marks_and_test_sizes['total_marks']

    return int(total_marks)


@register.filter
def subject_analytics_size(user, subject):
    student_test = StudentTest.objects.filter(subject__id=subject, user=user)
    sum_marks_and_test_sizes = student_test.aggregate(total_test_size=Sum('test_size'))
    total_test_size = sum_marks_and_test_sizes['total_test_size']
    return int(total_test_size)


@register.filter
def get_subject(subject):
    subject = Subject.objects.get(id=subject)
    return subject


@register.filter
def topic_analytics_strength(user, topic):
    topical_answers = StudentsAnswers.objects.filter(user=user, quiz__topic__name=topic, is_correct=True).count()
    class_test_answers = StudentsAnswers.objects.filter(user=user, quiz__topic__name=topic,
                                                        is_correct=True).count()
    passed = int(topical_answers) + int(class_test_answers)
    return passed


@register.filter
def topic_analytics_weakness(user, topic):
    topical_answers = StudentsAnswers.objects.filter(user=user, quiz__topic__name=topic, is_correct=False).count()
    class_test_answers = StudentsAnswers.objects.filter(user=user, quiz__topic__name=topic,
                                                        is_correct=False).count()
    failed = int(topical_answers) + int(class_test_answers)
    return failed


@register.filter
def topic_analytics_count(user, topic):
    passed = topic_analytics_strength(user, topic)
    failed = topic_analytics_weakness(user, topic)
    total = passed + failed

    return total


@register.filter
def get_topics(user, subject):
    if user is  int:
        topical_tests = StudentTest.objects.filter(user=user, subject=subject)
    else:
        topical_tests = StudentTest.objects.filter(user__email=user, subject=subject)

    topical_topics = topical_tests.values('topic__name')
    return topical_topics


@register.filter
def get_test_count(user, subject):
    if user is int:
        topical_tests = StudentTest.objects.filter(user=user, subject=subject).count()
        class_test = ClassTestStudentTest.objects.filter(user=user, test__subject=subject).count()
        general_test = GeneralTest.objects.filter(user=user, subject=subject).count()
    else:
        topical_tests = StudentTest.objects.filter(user__email=user, subject=subject).count()
        class_test = ClassTestStudentTest.objects.filter(user__email=user, test__subject=subject).count()
        general_test = GeneralTest.objects.filter(user__email=user, subject=subject).count()

    return topical_tests + class_test  + general_test


@register.filter
def get_topic_count(user, subject):
    if user is int:
        topical_tests = StudentTest.objects.filter(user__email=user, subject=subject).annotate(
    similar_topic=F('topic')
).annotate(
    count=Count('similar_topic')
).values('similar_topic').distinct().order_by('similar_topic').count()
    else:

        topical_tests = StudentTest.objects.filter(user__email=user, subject=subject).annotate(
    similar_topic=F('topic')
).annotate(
    count=Count('similar_topic')
).values('similar_topic').distinct().order_by('similar_topic').count()
    return topical_tests


@register.filter
def get_correct_choice(quiz):
    correct_choice = TopicalQuizAnswers.objects.get(quiz__quiz=quiz, is_correct=True)

    return correct_choice.choice




@register.simple_tag
def get_class_highest(class_id, subject, term):
    
    scores = Exam.objects.filter(user__academicprofile__current_class__class_id=class_id, subject__id=subject, term__term=term)
    highest = scores.values('score').order_by('-score').first()
    if highest:

        return highest['score']
    else:
        return 'Not Found'
    

@register.simple_tag
def get_class_lowest(class_id, subject, term):
    scores = Exam.objects.filter(user__academicprofile__current_class__class_id=class_id, subject__id=subject, term__term=term)
    lowest = scores.values('score').order_by('score').first()
    if lowest:

        return lowest['score']
    else:
        return 'Not Found'
    
@register.simple_tag
def get_class_average(class_id, subject, term):
    scores = Exam.objects.filter(user__academicprofile__current_class__class_id=class_id, subject__id=subject, term__term=term)
    total_marks = scores.aggregate(total_marks=Sum('score'))['total_marks']
    print(total_marks)
    

    if total_marks:

        average = (int(total_marks)/ int(scores.count()))

        return round(average,3)
    else:
        return 'Not Found'

@register.simple_tag
def get_class_overall_average(class_id, grade, term):
    scores = Exam.objects.filter(user__academicprofile__current_class__class_id=class_id, subject__grade=grade, term__term=term)
    total_marks = scores.aggregate(total_marks=Sum('score'))['total_marks']

    if total_marks:

        average = (int(total_marks)/ int(scores.count()))

        return round(average,3)
    else:
        return 'Not Found'
    

@register.simple_tag
def get_stream_overall_average(class_id, grade, term):
    class_id = SchoolClass.objects.get(class_id=class_id)
    class_id = SchoolClass.objects.filter(grade=class_id.grade).values_list('class_id')

    scores = Exam.objects.filter(user__academicprofile__current_class__class_id__in=class_id, subject__grade=grade, term__term=term)
    # print(scores)
    ranking = scores.values('user','score').order_by().aggregate(total_marks=Sum('score'))['total_marks']
    total_marks = scores.aggregate(total_marks=Sum('score'))['total_marks']

    if total_marks:

        average = (int(total_marks)/ int(scores.count()))

        return round(average,3)
    else:
        return 'Not Found'

@register.simple_tag
def get_user_term_average(user, grade, term):
    scores = Exam.objects.filter(user=user, subject__grade=grade, term__term=term)
    print(scores.explain())
    total_marks = scores.aggregate(total_marks=Sum('score'))['total_marks']

    if total_marks:

        average = (int(total_marks)/ int(scores.count()))

        return round(average,3)
    else:
        return 'Not Found'


@register.simple_tag
def get_class_overall_ranking(class_id, grade, term):
    scores = Exam.objects.filter(user__academicprofile__current_class__class_id=class_id, subject__grade=grade, term__term=term)
    # print(scores)
    ranking = scores.values('user','score').order_by().aggregate(total_marks=Sum('score'))['total_marks']
    total_marks = scores.aggregate(total_marks=Sum('score'))['total_marks']

    if scores:

      

        return scores
    else:
        return 'Not Found'


@register.simple_tag
def is_class_teacher(user):
    class_id = SchoolClass.objects.filter(class_teacher=user).values_list('class_name')
    classes = ""
    if class_id:
        for class_name in class_id:
            classes += str((class_name)[0]) + ', '


        return str(classes)
    else:
        return " "
    



@register.simple_tag
def get_subject_score(user, grade, subject, term):
    score = Exam.objects.filter(user__email=user, subject__grade=grade, subject=subject, term__term=term).first()
    # print(user,subject,term,grade)
    
    if score:

      

        return score.score
    else:
        return 'Not Found'
    
@register.filter
def get_student_latest_score(user, subject):
    exam = Exam.objects.filter(subject__id=subject).last()
    score = exam.score


    return score


@register.filter
def average_percentile(topic, count):
    answers = StudentsAnswers.objects.filter(quiz__topic__id=topic).count()
    percentage = (count / answers) * 100
    percentage = round(percentage, 2)
    
    return percentage

@register.simple_tag
def topic_percentile(topic):
    answers = StudentsAnswers.objects.filter(quiz__topic__id=topic)
    if answers.count() != 0:
        passed = answers.filter(is_correct=True).count()
        percentage = (passed / answers.count()) * 100
        percentage = round(percentage, 2)
        return percentage
    else:
        return 0