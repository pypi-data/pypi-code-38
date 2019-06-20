import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from register.models.attendee import Attendee
from bursary.models import Bursary


class RegisterStep(LoginRequiredMixin, FormView):
    template_name = 'register/form.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.WAFER_REGISTRATION_OPEN:
            return redirect('register-closed')
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @cached_property
    def register_step(self):
        from register.views import STEPS
        return STEPS.index(self.__class__)

    @cached_property
    def completed_register_steps(self):
        try:
            return self.request.user.attendee.completed_register_steps
        except ObjectDoesNotExist:
            return 0

    def get_context_data(self, **kwargs):
        from register.views import STEPS

        count = len(STEPS)
        context = super().get_context_data(**kwargs)
        steps = {
            'count': count,
            'percentage': 100 * (self.register_step + 1) / count,
            'step0': self.register_step,
            'step1': self.register_step + 1,
            'links': [],
        }
        for i, step in enumerate(STEPS):
            steps['links'].append({
                'accessible': self.completed_register_steps >= i,
                'current': i == self.register_step,
                'index': i,
                'title': step.title,
                'url': reverse('register-step-{}'.format(i)),
            })

        if self.register_step > 0:
            steps['prev'] = self.register_step - 1

        context['register'] = {
            'steps': steps,
            'title': self.title,
        }
        return context

    def get_success_url(self):
        if self.completed_register_steps < self.register_step > 0:
            attendee = self.request.user.attendee
            attendee.completed_register_steps = self.register_step
            attendee.save()

        next_step = self.register_step + 1

        wizard_goto_step = self.request.POST.get('wizard_goto_step')
        if wizard_goto_step:
            next_step = int(wizard_goto_step)

        return reverse('register-step-{}'.format(next_step))

    def form_valid(self, form):
        log = logging.getLogger('register.step')
        log.debug('Form received: user=%s step=%s data=%s',
                  self.request.user.username, self.register_step,
                  json.dumps(form.cleaned_data, cls=DjangoJSONEncoder))
        return super().form_valid(form)


class ClosedView(TemplateView):
    template_name = 'register/closed.html'


class UnRegisterView(LoginRequiredMixin, TemplateView):
    template_name = 'register/unregister.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'registered': Attendee.objects.filter(user=user).exists(),
            'bursary': Bursary.objects.filter(user=user).exists(),
        })
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.attendee.delete()

        Bursary.objects.filter(user=user).update(
            request_accommodation=False,
            request_food=False,
            request_travel=False)

        return self.get(request, *args, **kwargs)
