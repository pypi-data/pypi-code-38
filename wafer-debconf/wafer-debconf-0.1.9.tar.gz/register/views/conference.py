from register.dates import (
    ARRIVE_ON_OR_AFTER, ORGA_ARRIVE_ON_OR_AFTER, LEAVE_ON_OR_BEFORE
)
from register.forms.conference import ConferenceRegistrationForm
from register.models.attendee import Attendee
from register.views.core import RegisterStep


class ConferenceRegistrationView(RegisterStep):
    template_name = 'register/page/conference.html'
    title = 'Conference Registration'
    form_class = ConferenceRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['ARRIVE_ON_OR_AFTER'] = ORGA_ARRIVE_ON_OR_AFTER
        else:
            context['ARRIVE_ON_OR_AFTER'] = ARRIVE_ON_OR_AFTER
        context['LEAVE_ON_OR_BEFORE'] = LEAVE_ON_OR_BEFORE
        return context

    def get_initial(self):
        user = self.request.user
        initial = {}

        attendee = user.attendee
        for field in attendee._meta.get_fields():
            if field.is_relation:
                continue
            initial[field.name] = getattr(attendee, field.name)

        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data

        user.attendee  # We should never be creating, here
        user.attendee, created = Attendee.objects.update_or_create(
            user=user, defaults=data)
        return super().form_valid(form)
