import imp
from pydoc import describe

from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib import messages
from Discipline.models import ClassIncident, IncidentBooking, StudentDisciplineScore
from Supervisor.models import ExtraCurricular
from Users.models import MyUser
# Create your views here.

def deductPoints(user, score):
    profile = StudentDisciplineScore.objects.get(user=user)
    profile.points = profile.points - score
    profile.save()

    return None

def restorePoints(user, score):
    profile = StudentDisciplineScore.objects.get(user=user)
    profile.points = profile.points + score
    profile.save()

    return None
class CreateClassIncident(TemplateView):
    template_name = 'Discipline/create_incident.html'

    def post(self, request, **kwargs):
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            degree = request.POST.get('degree')
            score = request.POST.get('points')
            incident = ClassIncident.objects.create(name=name, incident_degree=degree, description=description, points=score )

            return redirect(request.get_full_path())

class Incidents(TemplateView):
    template_name = 'Discipline/incidents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incidents = ClassIncident.objects.all().order_by('-points')
        context['incidents'] = incidents
        return context
    
class ManageIncident(TemplateView):
    template_name = 'Discipline/manage_incident.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident_id = self.kwargs['id']
        try:
            incident = ClassIncident.objects.get(id=incident_id)
            context['incident'] = incident
        except ClassIncident.DoesNotExist:
            messages.error(self.request, 'Incident With The Given ID Does Not Exist!')
        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            degree = request.POST.get('degree')
            score = request.POST.get('points')
            incident = self.get_context_data().get('incident')
            if 'update' in request.POST:
                incident.name = name
                incident.description = description
                incident.incident_degree = degree
                incident.points = score
                incident.save()
                messages.success(request, 'SUCESS !')
                return redirect(request.get_full_path())
            else:
                incident = incident.delete()
                messages.success(request, 'SUCESS !')
                return redirect('incidents')


class BookedIncidents(TemplateView):
    template_name = 'Discipline/booked_students.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        role = self.request.user.role
        if role == 'Teacher':
            incidents = IncidentBooking.objects.filter(booked_by=self.request.user).order_by('-date')
            context['template'] = 'Teacher/teachers_base.html'
        else:
            incidents = IncidentBooking.objects.all().order_by('date')
            context['template'] = 'Supervisor/base.html'
        context['incidents'] = incidents
        return context
    
class ManageBookedIncident(TemplateView):
    template_name = 'Discipline/manage_booked_incident.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident_id = self.kwargs['id']
        incident = IncidentBooking.objects.get(id=incident_id)
        context['incidents'] = ClassIncident.objects.all().order_by('-points')
        context['incident'] = incident
        return context
    

    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            incident = self.get_context_data().get('incident')
            if 'delete' in request.POST:
                incident.delete()
                restorePoints(incident.user, incident.incident.points)
                return redirect('booked-students')
            else:
                name = request.POST.get('name')
                name = ClassIncident.objects.get(id=name)
                print(name.points,  incident.incident.points)
                points = incident.incident.points - name.points 
                restorePoints(incident.user, points)
                incident.incident = name
                incident.save()

                return redirect(request.get_full_path())

    

class StudentsDisciplineProfile(TemplateView):
    template_name = 'Discipline/students_discipline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.kwargs['email']
        l_user = MyUser.objects.get(email=email)
        incidents = IncidentBooking.objects.filter(user__email=email)
        context['incidents'] = incidents
        curricular = ExtraCurricular.objects.filter(students=l_user)
        context['events'] = curricular
        print(curricular)
        if not incidents:
            messages.info(self.request, 'This student does not have any Indiscipline incidents.')
        
        try:
            profile = StudentDisciplineScore.objects.get(user__email=email)
            context['profile'] = profile
        except StudentDisciplineScore.DoesNotExist:
            try:
                user = MyUser.objects.get(email=email)
                profile = StudentDisciplineScore.objects.create(user=user)
                context['profile'] = profile
            except MyUser.DoesNotExist:
                messages.error(self.request, 'We could not find any users matching your query !')


        return context


    

class BookIncident(TemplateView):
    template_name = 'Discipline/book_incident.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classes = ClassIncident.objects.all().order_by('-points')
        context['classes'] = classes
        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            adm_no = request.POST.get('adm_no')
            recepient = request.POST.get('recipient')
            incident = request.POST.get('incident')
            teacher = request.user
            try:
                student = MyUser.objects.get(email=adm_no, role='Student')
                if 'verify' in request.POST:
                    context = {
                        'student': student,
                        'classes': self.get_context_data().get('classes'),}
                    return render(request, self.template_name, context=context)
                else:
                    incident = ClassIncident.objects.get(id=incident)
                    booking = IncidentBooking.objects.create(user=student, incident=incident, booked_by=teacher)
                    deductPoints(student, incident.points)
                    messages.success(request, 'Incident Report was Succesful')
              
                return redirect(request.get_full_path())
                
            except MyUser.DoesNotExist:
                messages.error(request, f'Student with {adm_no} Admission Number Does Not Exist !!')
                return redirect(request.get_full_path())
            else:
                 pass


            return redirect(request.get_full_path())