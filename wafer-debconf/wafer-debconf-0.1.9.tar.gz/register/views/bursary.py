from django.conf import settings
from django.contrib import messages

from bursary.models import Bursary
from register.forms.bursary import BursaryForm
from register.models.accommodation import Accomm
from register.views.core import RegisterStep


class BursaryView(RegisterStep):
    template_name = 'register/page/bursary.html'
    title = 'Bursary'
    form_class = BursaryForm

    def get_initial(self):
        user = self.request.user
        initial = {}

        try:
            bursary = user.bursary
        except Bursary.DoesNotExist:
            pass
        else:
            for field in bursary._meta.get_fields():
                if field.is_relation:
                    continue
                initial[field.name] = getattr(bursary, field.name)

        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data

        if not (data['request_food'] or data['request_accommodation']
                or data['request_travel']):
            # Update but don't create:
            Bursary.objects.filter(user=user).update(**data)
        elif settings.BURSARIES_CLOSED:
            # Only decrease existing requests:
            try:
                bursary = Bursary.objects.get(user=user)
            except Bursary.objects.DoesNotExist:
                pass
            else:
                bursary.travel_bursary = min(
                    bursary.travel_bursary or 0,
                    data['travel_bursary'] or 0) or None
                for field in ('request_travel', 'request_food',
                              'request_accommodation'):
                    if getattr(bursary, field) and not data[field]:
                        setattr(bursary, field, data[field])
                bursary.save()
        else:
            user.bursary, created = Bursary.objects.update_or_create(
                user=user, defaults=data)

        if not settings.DEBCONF_PAID_ACCOMMODATION:
            if not data['request_accommodation']:
                try:
                    user.attendee.accomm.delete()
                except Accomm.DoesNotExist:
                    pass
                else:
                    messages.warning(
                        self.request,
                        "Your accommodation registration is now cancelled. "
                        "You'll need to organise your own accommodation.")

        return super().form_valid(form)
