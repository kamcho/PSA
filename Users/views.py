from typing import Any
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView
from SubjectList.models import Progress, Topic

from Users.models import PersonalProfile, MyUser, AcademicProfile, SchoolClass
import logging

logger = logging.getLogger('django')

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


# views.py
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MyUser, AcademicProfile, PersonalProfile
from .serializers import MyUserSerializer, AcademicProfileSerializer, PersonalProfileSerializer

from django.contrib.auth.hashers import make_password

class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        user_data_list = request.data  # Assuming request.data is a list
        errors = []

        for user_data in user_data_list:
            user_serializer = MyUserSerializer(data=user_data.get('user', {}))
            if user_serializer.is_valid():
                user_data['user']['password'] = make_password(user_data['user']['password'])  # Hash the password

                user = user_serializer.save()

                academic_profile_data = user_data.get('academic_profile', {})
                
                if academic_profile_data:
                    academic_profile_data['user'] = user.id
                    academic_profile_serializer = AcademicProfileSerializer(data=academic_profile_data)
                    if academic_profile_serializer.is_valid():
                        academic_profile_serializer.save()
                    else:
                        errors.append({'academic_profile_error': academic_profile_serializer.errors})
                        user.delete()

                personal_profile_data = user_data.get('personal_profile', {})
                if personal_profile_data:
                    personal_profile_data['user'] = user.id
                    personal_profile_serializer = PersonalProfileSerializer(data=personal_profile_data)
                    if personal_profile_serializer.is_valid():
                        personal_profile_serializer.save()
                    else:
                        errors.append({'personal_profile_error': personal_profile_serializer.errors})
                        user.delete()

            else:
                errors.append({'user_error': user_serializer.errors})

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Users created successfully'})

    


    
class StaticViewSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return ['student-home', 'redirect', 'profile', 'register', 'login', 'edit-profile' ]  # Add the names of your static views

    def location(self, item):
        return reverse(item)
class RegisterView(TemplateView):
    template_name = "Users/register.html"

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            email = request.POST.get('email')
            pwd1 = request.POST.get('pwd1')
            pwd2 = request.POST.get('pwd2')
            role = request.POST.get('role')
            grade = request.POST.get('grade')

            if email and pwd2 and pwd1:
                if pwd2 == pwd1:
                    try:
                        user = MyUser.objects.create_user(email=email, role=role, password=pwd1)
                        user.save()

                        messages.success(request, f'Account for {email} has been created successfully.')
                        if role == 'Student':
                            academic_profile, created = AcademicProfile.objects.get_or_create(user=user)
                            grade = SchoolClass.objects.get(grade=grade)
                            academic_profile.current_class = grade
                            academic_profile.save()
                        user = authenticate(self.request, username=email, password=pwd1)

                        if user is not None:
                            # Log the user in
                            login(self.request, user)
                            # Redirect to a success page
                            return redirect('redirect')
                        else:
                            return redirect('login')

                            

                    except IntegrityError as e:
                        messages.error(request, str(e))
                else:
                    messages.error(request, 'The passwords did not match!')
            else:
                messages.error(request, 'You did not completely fill out the form.')

        return redirect(request.get_full_path())




class Login(TemplateView):
    template_name = 'Users/login.html'

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            # Create an instance of the AuthenticationForm and populate it with user-submitted data

            username = self.request.POST.get('email')
            password = self.request.POST.get('password')
            user = authenticate(self.request, username=username, password=password)

            if user is not None:
                # Log the user in
                login(self.request, user)
                # Redirect to a success page
                return redirect('redirect')
            else:
                # Return an error message if authentication fails
                messages.error(self.request, "Invalid username or password. Try again !")
                return redirect(self.request.get_full_path())


class MyProfile(LoginRequiredMixin, TemplateView):
    """
        view and manipulate a user's profile.
        Attach a learner to your watch list for parents/guardians
    """
    template_name = "Users/profile.html"

    def get_context_data(self, **kwargs):
        context = super(MyProfile, self).get_context_data(**kwargs)
        
        # Check user's role and use appropriate base Html Template
        if self.request.user.role == 'Student':
            # get the current logged in user(learner) current grade and associated Subjects
            context['base_html'] = 'Users/base.html'
        elif self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        elif self.request.user.role in ['Supervisor', 'Finance']:
            context['base_html'] = 'Supervisor/base.html'
        
        else:
            # If logged in user's role doesn't match any criteria log out the user and show message
            messages.error(self.request, 'You are not authorised to use this system!')
            # redirect('logout')

        return context

    def post(self, args, **kwargs):
        # Check for Post requests
        if self.request.method == "POST":
            user = self.request.user
            # Check which button is clicked
            if 'profile' in self.request.POST:
                try:

                        # Get logged in user's profile for editing
                        profile = PersonalProfile.objects.get(user=user)  # get users personal profile
                        f_name = self.request.POST.get('first-name').lower()
                        new_phone_number = self.request.POST.get('phone-number')
                        l_name = self.request.POST.get('last-name').lower()
                        surname = self.request.POST.get('surname').lower()
                        if new_phone_number:
                            profile.phone = new_phone_number
                        profile.f_name = f_name
                        profile.l_name = l_name
                        profile.surname = surname
                        profile.save()
                        messages.success(self.request, 'Profile has been successfully Updated!')

                except PersonalProfile.DoesNotExist as e:
                    # Create personal profile if none is found
                    messages.error(self.request, 'OOOps that did not work, Please try again!!')
                    personal_profile = PersonalProfile.objects.create(user=user)

                except IntegrityError:
                    messages.error(self.request, 'A user with this phone number already exists !! If this number belongs to you contact @support')

                except Exception as e:
                    # Handle any unhandled errors
                    messages.error(self.request, 'Sorry, there was an issue updating your profile. Please try again.')
                    error_message = str(e)  # Get the error message as a string
                    error_type = type(e).__name__

                    logger.critical(
                        error_message,
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': settings.SCHOOL_ID,
                            'error_type': 'DatabaseError',
                            'user': self.request.user,
                            'level': 'Critical',
                            'model': 'Database Error',
                        }
                    )

                # Add a learner to a guardians watch list
            elif 'attachment' in self.request.POST:
                try:
                    if self.request.user.role == 'Guardian':
                        mail = self.request.POST.get('mail')
                        name = self.request.POST.get('name').lower()

                        learner = PersonalProfile.objects.get(user__email=mail)  # get users profile
                        # Ensure users first name matches the value of first name and ensure that the user is a student.
                        if learner.f_name.lower() == name and learner.user.role == 'Student':
                            ref_id = self.request.user.uuid
                            learner.ref_id = ref_id
                            learner.save()
                            messages.success(self.request, f'Succesfully added {mail} to your watch list')
                        
                        else:
                            messages.error(self.request, 'Sorry, we could not find a User matching your search!!.\
                                            Ensure that the user is a student and has updated his/her names.')

                    else:
                        messages.error(self.request, 'Sorry, You are not authorised to perform this action.')

                except PersonalProfile.DoesNotExist as e:
                    # Create personal profile if none is found
                    messages.error(self.request, 'OOOps that did not work, Please try again!!')
                    personal_profile = PersonalProfile.objects.create(user__email=mail)
                except Exception as e:
                    # Handle any exceptions
                    messages.error(self.request, 'Sorry, An error occurred. Please try again later !!')
                    error_message = str(e)  # Get the error message as a string
                    error_type = type(e).__name__

                    logger.critical(
                        error_message,
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': settings.SCHOOL_ID,
                            'error_type': 'DatabaseError',
                            'user': self.request.user,
                            'level': 'Critical',
                            'model': 'DatabaseError',
                        }
                    )

        return redirect(self.request.get_full_path())


class LoginRedirect(LoginRequiredMixin, TemplateView):
    """
        Redirect a user based on their role
    """
    template_name = 'Users/login_redirect.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        try:
            user = self.request.user
            role = user.role
            profile = self.request.user.personalprofile
            f_name = profile.f_name
        except ObjectDoesNotExist as e:
            profile = PersonalProfile.objects.create(user=user)
            f_name = profile.f_name

        except Exception as e:
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
                    'level': 'Warning',
                    'model': 'DatabaseError',
                }
            )
        finally:

            # If a user has not updated their profile redirect them to profile editing page
            if f_name == '':
                return redirect('edit-profile')
            else:
                if role == 'Student':
                    return redirect('student-home')
                elif role == 'Guardian':
                    return redirect('guardian-home')
                elif role == 'Teacher':
                    return redirect('teachers-home')
                elif role in ['Supervisor', 'Finance']:
                    return redirect('supervisor-home')
                
                else:

     
                    return redirect('logout')


def finish_profile_setup(user, f_name, l_name, surname, phone):
 
    profile = PersonalProfile.objects.get(user=user)
    profile.f_name = f_name
    profile.l_name = l_name
    if phone:
        profile.phone = phone
    profile.surname = surname
    profile.save()
    return None


class FinishSetup(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        User's profile edit Page, mainly for first time account users
    """
    template_name = 'Users/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            if self.request.user.role == 'Student':
                # get the current logged in user(learner) current grade and associated Subjects
                context['base_html'] = 'Users/base.html'
            elif self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            elif self.request.user.role == 'Supervisor':
                context['base_html'] = 'Supervisor/base.html'

        except:
            context['base_html'] = 'Users/base.html'
            messages.error(self.request, 'Not logged in')


        return context

    def post(self, request, **kwargs):
        if request.method == 'POST':
            f_name = request.POST.get('f_name').lower()
            l_name = request.POST.get('l_name').lower()
            surname = request.POST.get('surname').lower()
            phone = request.POST.get('phone')
            user = self.request.user  # get user from session.

            try:
                # Get user's profile for editing
                if self.request.user.role == 'Admin':
                    messages.error(self.request, 'You can only use the admin interface')
                    return redirect('logout')
                if f_name and l_name and surname:
                    finish_profile_setup(user=user, f_name=f_name, l_name=l_name, surname=surname, phone=phone)


            # if no profile matching query is found, create it and update it
            except PersonalProfile.DoesNotExist as e:
                PersonalProfile.objects.create(user=user)
                finish_profile_setup(user=user, f_name=f_name, l_name=l_name, surname=surname, phone=phone)

            except IntegrityError:
                messages.error(self.request, 'A user with this phone number already exists !! If this number belongs to you contact @support')
                return redirect(request.get_full_path())



            except Exception as e:
                messages.error(request, 'We could not process your request, try again.!!')
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

            # Finally reroute a user based on their role
            finally:

                if request.user.role == 'Student':
                    return redirect('student-home')
                elif request.user.role == 'Guardian':
                    return redirect('guardian-home')
                elif request.user.role == 'Teacher':
                    return redirect('teachers-home')
                elif request.user.role in ['Supervisor', 'Finance']:
                    return redirect('supervisor-home')
                else:
                    messages.error(request, 'Role not found')
                    return redirect(request.get_full_path())
            
        else:
            return redirect(request.get_full_path())

    # ensure a user is only editing their profile.
    def test_func(self):
        user = self.request.user
        profile = get_object_or_404(PersonalProfile, user=user)
        return profile.user == user  # Check if the profile belongs to the logged-in user


def rout(request):
    try:
        role = request.user.role
        print(role)

        if role == 'Guardian':
            return redirect('guardian-home')
        elif role == 'Student':
            return redirect('student-home')
        elif role == 'Teacher':
            return redirect('teacher-home')
        elif role == 'Partner':
            return redirect('partner-home')
        elif role in ['Finance', 'Supervisor']:
            return redirect('supervisor-home')
    except:
        return redirect('logout')


class StudentsHome(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Home view for the Student's dashboard.
    Displays the user's progress and related information.
    """
    template_name = 'Users/home.html'

    def get_context_data(self, **kwargs):
        """
        Populate the context with data for the template.
        """
        context = super().get_context_data(**kwargs)
        try:
            # Retrieve the user's last viewed subject from progress model
            user = self.request.user
            academic_profile = AcademicProfile.objects.get(user=user)
            progress_queryset = Progress.objects.filter(user=user)
            last_subject = progress_queryset.last()

            # Check if a user has any saved progress
            if last_subject:
                # Get the order of the last topic in the last subject
                number = last_subject.topic.last().order
                next_topic_id = int(number) + 1

                # Retrieve the next topic in the same subject
                next_topic = Topic.objects.filter(subject=last_subject.subject, order=next_topic_id).first()

                # Retrieve subjects and related information for the user
                subject = progress_queryset.filter(subject__isnull=False) \
                    .values('subject__name', 'subject__id','subject__grade','subject__topics', 'subject__topics').annotate(subtopic_count=Count('subtopic', distinct=True))

                # Populate the context with data
                context['next'] = next_topic
                context['last_subject'] = last_subject
                context['subjects'] = subject
            grade = academic_profile.current_class.grade
            if grade is None:
                raise AttributeError

            context['grade'] = grade



        except AttributeError as e:
            context['grade'] = 4
            messages.error(self.request, 'You did not specify the current class'
                                         ' you are in. Please contact @support immediately')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
            logger.critical(
                f'This user has not specified class, {error_message}',
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': settings.SCHOOL_ID,
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',

                    'model': 'AcademicProfile',
                    # Add more custom fields as needed
                }
            )



        except AcademicProfile.DoesNotExist as e:
            academic_profile = AcademicProfile.objects.create(user=user)
            context['grade'] = 4
            messages.error(self.request, 'Dear user, you have not specified the current class you are in. Please contact @support')

            

        except Exception as e:
            context['grade'] = 4

            messages.error(self.request, f' {str(e)} An error occurred. Please contact @support')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
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
                    # Add more custom fields as needed
                }
            )


        return context
    
    def test_func(self):
        try:
            role = self.request.user.role
            return role == 'Student'        
        except:
            return False

    
        
