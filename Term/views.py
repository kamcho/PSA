from typing import Any
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from SubjectList.models import Subject
from Term.models import CurrentTerm, Exam
from django.contrib.messages import success,error
from Users.models import AcademicProfile, MyUser
# Create your views here.


class AddSubjectScore(TemplateView):
    template_name = 'Term/add_score.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        subject_id= self.kwargs['subject']
        subject = Subject.objects.get(id=subject_id)
        term = CurrentTerm.objects.all().last()
        excluded = Exam.objects.filter(subject=subject, term=term.term).values_list('user__email')

        students = AcademicProfile.objects.filter(current_class__class_name=class_id).exclude(user__email__in=excluded)
        if not students:
            success(self.request, 'You have entered marks for all students')
        context['subject'] = subject
        context['students'] = students
        return context
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            email = request.POST.get('user')
            user = MyUser.objects.get(email=email)
            score = request.POST.get('score')
            try:
                term = CurrentTerm.objects.all().last()
                subject = self.get_context_data().get('subject')
                exam = Exam.objects.create(user=user, subject=subject, score=score, term=term.term)
                success = (self.request, f'Succesfully added marks for {user}. score = {score}')
                request.session['exclude'] = email
            except Exception as e:
                error(request, 'Marks already exists')

        return redirect(request.get_full_path())


    
