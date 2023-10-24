import logging
import math
from django.db.models import Count, F

from django import template
from django.db.models import Sum
from django.shortcuts import redirect
import datetime

from Exams.models import StudentTest, StudentsAnswers, ClassTestStudentTest, ClassTest, StudentKNECExams, GeneralTest, \
    TopicalQuizes, TopicalQuizAnswers
from SubjectList.models import *

from Users.models import MyUser, SchoolClass

register = template.Library()
logger = logging.getLogger('django')

@register.filter
def divide(value, arg):
    try:
        value = int(value)
        return round((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def get_user_progress_topic(user, subject):
    subject = Subject.objects.get(id=subject)
    progress = Progress.objects.filter(user=user, subject=subject).last()
    if progress:
        try:
            current_subtopic = Subtopic.objects.get(name=progress.subtopic)
            return current_subtopic

        except Subtopic.DoesNotExist:
            try:
                introduction = Topic.objects.get(subject=subject, order=1)
                introduction = Subtopic.objects.get(topic=introduction, order=1)
                return introduction
            except Topic.DoesNotExist:
                return None
            except Subtopic.DoesNotExist:
                return None
    else:
        try:
            introduction = Topic.objects.get(subject=subject, order=1)
            introduction = Subtopic.objects.get(topic=introduction, order=1)
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
        knec_test = StudentKNECExams.objects.filter(user=user, test=test_uuid)
        if student_test or class_test or knec_test:

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
        knec_test = StudentKNECExams.objects.filter(user=user, test__subject=subject).count()
        general_test = GeneralTest.objects.filter(user=user, subject=subject).count()
    else:
        topical_tests = StudentTest.objects.filter(user__email=user, subject=subject).count()
        class_test = ClassTestStudentTest.objects.filter(user__email=user, test__subject=subject).count()
        knec_test = StudentKNECExams.objects.filter(user__email=user, test__subject=subject).count()
        general_test = GeneralTest.objects.filter(user__email=user, subject=subject).count()

    return topical_tests + class_test + knec_test + general_test


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