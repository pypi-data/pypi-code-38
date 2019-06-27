from django_szuprefix.utils.views import ContextJsonDumpsMixin, FormResponseJsonMixin
from . import models, mixins
# Create your views here.
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from django.http import JsonResponse


class PartyCreateView(FormResponseJsonMixin, ContextJsonDumpsMixin, CreateView):
    model = models.Party
    fields = ('name', 'worker_count')


class WorkerCreateView(mixins.PartyMixin, FormResponseJsonMixin, ContextJsonDumpsMixin, CreateView):
    model = models.Worker
    fields = ('name', 'number', 'position', 'position', 'is_active', 'profile')
