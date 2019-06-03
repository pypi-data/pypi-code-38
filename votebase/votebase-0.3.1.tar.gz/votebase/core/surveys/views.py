from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import ListView, CreateView, UpdateView, FormView
from django.views.generic.base import View, TemplateResponseMixin

from votebase.core.surveys.forms import SegmentForm, SurveySettingsForm, \
    BrandingForm, BrandingImageForm
from votebase.core.surveys.models import Survey, Round, BrandingImage


class IndexView(ListView):
    model = Survey
    template_name = 'surveys/index.html'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        request.breadcrumbs([(_(u'Surveys'), reverse('surveys_index')), ])

        if not request.user.survey_set.all().count():
            return redirect('surveys_create')

        self.last_seen_surveys = request.user.get_profile().last_seen_surveys
        request.user.get_profile().last_seen_surveys = now()
        request.user.get_profile().save()

        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(IndexView, self).get_queryset()
        return queryset.by_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        self.survey_list = list(context['object_list'])

        for survey in self.survey_list:
            survey.new_voters_count = survey.get_new_voters_count(
                self.last_seen_surveys)

        context['object_list'] = self.survey_list
        return context


class SettingsBrandingView(FormView):
    template_name = 'surveys/settings_branding.html'
    form_class = BrandingForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs(
            [(_(u'Surveys'), reverse('surveys_index')),
             (self.survey.title, reverse(
                 'questions_index', args=(self.survey.pk, ))), ])

        #TODO: uncomment this to allow package restrictions
#        if not request.user.get_profile().is_permitted_to_enter_branding():
#            messages.error(request, _(u'You have to upgrade your package. See our <a href="%s">pricing</a>.') % reverse('pricing'))
#            try:
#                return redirect(request.META['HTTP_REFERER'])
#            except KeyError:
#                return redirect(reverse('surveys_settings_segments', args=(self.survey.pk, )))

        return super(SettingsBrandingView, self).dispatch(
            request, *args, **kwargs)

    def get_success_url(self):
        return reverse('surveys_settings_branding', args=(self.survey.pk, ))

    def get_context_data(self, **kwargs):
        context = super(SettingsBrandingView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        context['brandingimages'] = BrandingImage.objects.by_user(self.request.user).by_survey(self.survey)
        return context

    def form_valid(self, form):
        self.survey.css = form.cleaned_data['css']
        self.survey.save()
        messages.success(self.request, _(u'CSS code for survey template has been successfully updated.'))
        return super(SettingsBrandingView, self).form_valid(form)


class SettingsBrandingUploadImageView(FormView):
    form_class = BrandingImageForm
    template_name = 'surveys/settings_branding_upload_image.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs(
            [(_(u'Surveys'), reverse('surveys_index')),
             (self.survey.title, reverse(
                 'questions_index', args=(self.survey.pk, ))), ])

        return super(SettingsBrandingUploadImageView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SettingsBrandingUploadImageView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        return context

    def get_success_url(self):
        return reverse('surveys_settings_branding', args=(self.survey.pk, ))

    def form_valid(self, form):
        branding_image = form.save(commit=False)
        branding_image.survey = self.survey
        branding_image.user = self.request.user
        branding_image.save()

        return super(SettingsBrandingUploadImageView, self).form_valid(form)


class SettingsBrandingDeleteImageView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.branding_image = get_object_or_404(BrandingImage, pk=kwargs.get('pk'))

        if self.branding_image.user != request.user:
            return HttpResponseForbidden()

        self.branding_image.delete()
        messages.success(request, _(u'Branding image successfully deleted.'))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('surveys_settings_branding', args=(self.branding_image.survey.pk, ))


class SettingsDeleteSegmentView(View):
    success_url = 'surveys_settings_segments'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.round = get_object_or_404(Round, pk=kwargs.get('pk'))
        self.survey = self.round.survey

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if self.survey.round_set.all().count() == 1:
            messages.error(request, _(u'You have to keep at least one segment!'))
            return redirect(reverse('surveys_settings_segments_update',
                args=(self.survey.id, self.round.id)))
        else:
            self.round.delete()

        messages.success(request, _(u'Segment successfully deleted.'))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('surveys_settings_segments', args=(self.survey.pk, ))


class SurveyCreateView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SurveyCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        survey = Survey.objects.create(
            user=request.user,
            title=_(u'Your new survey')
        )

        #create default round
        Round.objects.create(survey=survey)

        return redirect(reverse('questions_index', args=(survey.pk, )))


class SegmentCreateView(CreateView):
    template_name = 'surveys/create_round.html'
    model = Round
    form_class = SegmentForm
    success_url = 'surveys_settings_segments'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs(
            [
                (_(u'Surveys'), reverse('surveys_index')),
                (self.survey.title, reverse('questions_index', args=(self.survey.pk, ))),
                (_(u'Settings'), reverse('surveys_settings_segments', args=(self.survey.pk, ))),
            ])

        #TODO: uncomment this to allow package restrictions
#        if not request.user.get_profile().is_permitted_to_create_segment():
#            messages.error(request, _(u'You have to upgrade your package. See our <a href="%s">pricing</a>.') % reverse('pricing'))
#            try:
#                return redirect(request.META['HTTP_REFERER'])
#            except KeyError:
#                return redirect(reverse('surveys_settings_segments', args=(self.survey.pk, )))

        return super(SegmentCreateView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(SegmentCreateView, self).get_form(self.form_class)
        form.survey = self.survey
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.survey = self.survey
        self.object.save()

        messages.success(self.request, _(u'Segment successfully created.'))

        return super(SegmentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk,))

    def get_context_data(self, **kwargs):
        context = super(SegmentCreateView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        return context


class SurveyUpdateView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))
        if self.survey.user != request.user:
            return HttpResponseForbidden()
        return super(SurveyUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse('questions_index', args=(self.survey.pk, )))

    def post(self, request, pk):
        if 'title' in request.POST and request.POST.get('title') != '':
            self.survey.title = request.POST.get('title', _('Your new survey'))
        else:
            self.survey.title = _('Your new survey')
        self.survey.save()

        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        return redirect(reverse('questions_index', args=(self.survey.pk, )))


class SurveyDeleteView(View):
    success_url = 'surveys_index'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):        
        survey = get_object_or_404(Survey, pk=kwargs.get('pk'))
        if survey.user != request.user:
            return HttpResponseForbidden()
        survey.delete()
        messages.success(request, _(u'Survey successfully deleted.'))
        return redirect(self.success_url)


class SettingsGeneralView(UpdateView):
    template_name = 'surveys/settings_general.html'
    model = Survey
    form_class = SurveySettingsForm
    success_url = 'surveys_settings_general'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        request.breadcrumbs(
            [(_(u'Surveys'), reverse('surveys_index')),
                (self.survey.title, reverse(
                    'questions_index', args=(self.survey.pk, ))), ])

        return super(SettingsGeneralView, self).dispatch(
            request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _(u'Survey successfully updated.'))
        return super(SettingsGeneralView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk,))


class SettingsSegmentsView(UpdateView):
    template_name = 'surveys/settings_segment_update.html'
    model = Round
    form_class = SegmentForm
    success_url = 'surveys_settings_segments_update'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        self.segments = self.survey.round_set.all()

        if 'pk_segment' in kwargs:
            self.segment = get_object_or_404(Round, pk=kwargs.get('pk_segment'))
        else:
            last_segment = self.survey.get_last_round()

            return redirect(reverse('surveys_settings_segments_update',
                args=(self.survey.pk, last_segment.pk)))

        request.breadcrumbs(
            [(_(u'Surveys'), reverse('surveys_index')),
             (self.survey.title, reverse('questions_index', args=(self.survey.pk, ))), ])

        return super(SettingsSegmentsView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.segment

    def form_valid(self, form):
        messages.success(self.request, _(u'Segment successfully updated.'))
        return super(SettingsSegmentsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SettingsSegmentsView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        return context

    def get_success_url(self):
        return reverse(self.success_url, args=(self.survey.pk, self.segment.pk,))


class ShareView(ListView):
    model = Round
    template_name = 'surveys/share.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk'))
        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if self.survey.title == _('Your new survey'):
            messages.error(
                request, _(u'Please, change the default survey title by clicking on it.'))
            return redirect(reverse(
                'questions_index', args=(self.survey.pk, )))

        if request.user.username == 'demo':
            messages.error(
                request, _(u'This is demo only. If you want to share your surveys, please <a href="%s">register</a>.') % reverse('accounts_logout_register'))
            return redirect(reverse(
                'questions_index', args=(self.survey.pk, )))


        if 'round_pk' in kwargs:
            self.round = Round.objects.get(pk=kwargs.get('round_pk'))
        else:
            self.round = self.survey.get_last_round()

        request.breadcrumbs([(_(u'Surveys'), reverse('surveys_index')), ])

        return super(ShareView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(ShareView, self).get_queryset()
        queryset = queryset.filter(survey=self.survey)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)
        context['survey'] = self.survey
        context['round'] = self.round
        return context


class PrintView(TemplateResponseMixin, View):
    template_name = 'questions/print.html'

    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, pk=kwargs.get('pk', ))

        if self.survey.user != request.user:
            return HttpResponseForbidden()

        if self.survey.title == _('Your new survey'):
            messages.error(
                request, _(u'Please, change the default survey title by clicking on it.'))
            return redirect(reverse(
                'questions_index', args=(self.survey.pk, )))

        self.questions = self.survey.question_set.all()

        request.breadcrumbs([(_(u'Surveys'), reverse('surveys_index')), ])

        return super(PrintView, self).dispatch(request, *args, **kwargs)

    def render_to_pdf(self, template_src, context_dict):
        import cStringIO as StringIO
        import ho.pisa as pisa

        from django.template.loader import get_template
        from django.template import Context
        from django.http import HttpResponse
        from cgi import escape

        template = get_template(template_src)
        context = Context(context_dict)
        html  = template.render(context)
        result = StringIO.StringIO()

        pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), mimetype='application/pdf')
        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

#    def get(self, request, pk):
#        return self.render_to_pdf(self.template_name, {
#            'survey': self.survey,
#            'questions': self.questions,
#        })

    def get(self, request, pk):
        return self.render_to_response({
            'survey': self.survey,
            'questions': self.questions,
        })
