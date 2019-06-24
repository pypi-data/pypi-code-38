from django_tables2 import SingleTableView

from django_szuprefix.utils.views  import FormResponseJsonMixin, ContextJsonDumpsMixin
from . import models
# Create your views here.
from django.views.generic import CreateView,DetailView


class SchoolCreateView(FormResponseJsonMixin, ContextJsonDumpsMixin, CreateView):
    model = models.School
    fields = ('name', 'type')


class StudentDetailView(ContextJsonDumpsMixin, DetailView):
    model = models.Student


class StudentListView(ContextJsonDumpsMixin, SingleTableView):
    model = models.Student
