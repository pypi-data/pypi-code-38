from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from votebase.core.accounts.forms import SimpleRegisterForm


class HomeView(TemplateView):
    template_name = 'votebase/home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('surveys_index')

        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['register_form'] = SimpleRegisterForm()
        return context
