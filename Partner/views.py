from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


class Partner(TemplateView):
    template_name = 'Partner/home.html'