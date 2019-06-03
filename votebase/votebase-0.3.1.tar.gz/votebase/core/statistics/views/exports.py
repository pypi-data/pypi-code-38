from __future__ import absolute_import

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateResponseMixin

from votebase.core.questions.models import Question
from votebase.core.statistics.handlers.general import OptionsQuestionCsvHandler
from votebase.core.surveys.models import Round, Survey
from votebase.thirdparty.wkhtmltopdf.utils import PDFTemplateResponse


class ExportCsvView(TemplateResponseMixin, View):
    template_name = 'statistics/voter.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=kwargs.get('pk'))
        self.survey = self.question.survey

        if request.user != self.survey.user:
            return HttpResponseForbidden()

        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
        else:
            self.round = None

#        request.breadcrumbs([
#            (_(u'Surveys'), reverse('surveys_index')),
#            (self.survey.title, reverse('questions_index', args=(kwargs.get('pk'), ))),
#            ])

        return super(ExportCsvView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk, round_pk=None):
        try:
            return self.question.get_csv_handler(self.round).export()
        except KeyError:
            return OptionsQuestionCsvHandler(self.question, self.round).export()


class ExportPdfView(TemplateResponseMixin, View):
    template_name = 'statistics/graphs_pdf.html'
    response_class = PDFTemplateResponse
    filename = None
    cmd_options = {
        'margin-top':5,
        'margin-right':10,
        'margin-bottom':10,
        'margin-left':10,
        'page-size': 'A4',
#        'print-media-type': True,
#        'orientation': 'landscape',
#        'collate': True,
        }

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
        else:
            self.round = None

        request.breadcrumbs([
            (_(u'Surveys'), reverse('surveys_index')),
            (self.survey.title, reverse('questions_index', args=(kwargs.get('pk'), ))),
        ])
        return super(ExportPdfView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['html'] = mark_safe(request.POST['html'])
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            'survey': self.survey,
            'round': self.round
        }

    def render_to_response(self, context, **response_kwargs):
        if issubclass(self.response_class, PDFTemplateResponse):
            return super(ExportPdfView, self).render_to_response(
                context=context, filename=self.filename,
                cmd_options=self.cmd_options,
                **response_kwargs
            )

        return super(ExportPdfView, self).render_to_response(
            context=context,
            **response_kwargs
        )
