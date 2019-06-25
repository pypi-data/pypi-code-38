from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.views.generic.edit import ModelFormMixin

from . import models
# Create your views here.
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from django.http import JsonResponse
