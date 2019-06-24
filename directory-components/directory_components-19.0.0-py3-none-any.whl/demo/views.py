from django.shortcuts import Http404
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from directory_components.mixins import (
    CountryDisplayMixin, EnableTranslationsMixin
)

from demo import forms


class BasePageView(TemplateView):

    @property
    def template_name(self):
        return self.kwargs.get('template_name')


class InternationalHeaderView(
    CountryDisplayMixin, EnableTranslationsMixin, BasePageView
):
    pass


class InvestHeaderView(
    CountryDisplayMixin, EnableTranslationsMixin, BasePageView
):
    pass


class BreadcrumbsDemoPageView(BasePageView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['page'] = {
            'title': 'Breadcrumbs demo page',
            'url': '',
        }
        context['home_link'] = '/'
        context['home_label'] = 'Home'
        return context


class DemoStatsView(BasePageView):
    statistics = [
        {
            'heading': 'Ease of doing business',
            'number': '36',
            'smallprint': 'World Bank Ease of Doing Business ranking'
        },
        {
            'heading': 'Currency',
            'number': 'Euro',
            'smallprint': ''
        },
        {
            'heading': 'Business languages',
            'number': 'Dutch, English',
            'smallprint': ''
        },
        {
            'heading': 'GDP per capita',
            'number': '48,223.16 USD',
            'smallprint': 'UK GDP per capita is 39,800.3 USD'
        },
        {
            'heading': 'Economic growth',
            'number': '2.9%',
            'smallprint': 'in 2017'
        },
        {
            'heading': 'Time zone',
            'number': 'GMT+1',
            'smallprint': ''
        },
    ]
    num_of_statistics = 6


class DemoFormErrorsView(FormView):
    template_name = 'demo/form-errors.html'
    form_class = forms.DemoFormErrors
    success_url = reverse_lazy('form-errors')


class DemoFormView(TemplateView):
    template_name = 'demo/form-elements.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            text_form=forms.TextBoxForm(),
            checkbox_form=forms.CheckboxForm(),
            multiple_choice_form=forms.MultipleChoiceForm(),
            radio_form=forms.RadioForm(),
            *args, **kwargs
        )


class Trigger404View(View):
    def dispatch(self, request):
        raise Http404()


class Trigger500ErrorView(View):
    def dispatch(self, request):
        raise Exception('triggering a server error')
