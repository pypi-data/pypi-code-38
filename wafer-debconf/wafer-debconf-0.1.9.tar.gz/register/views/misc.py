from register.forms.misc import MiscForm
from register.models.attendee import Attendee
from register.views.core import RegisterStep


class MiscView(RegisterStep):
    title = 'Anything Else?'
    form_class = MiscForm

    def get_initial(self):
        initial = {
            'notes': self.request.user.attendee.notes
        }
        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data

        user.attendee  # We should never be creating, here
        user.attendee, created = Attendee.objects.update_or_create(
            user=user, defaults=data)
        return super().form_valid(form)
