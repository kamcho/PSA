from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class Reception(TemplateView):
    template_name = 'Reception/recption'