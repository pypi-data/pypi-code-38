from register.dates import parse_date
from register.forms.accommodation import AccommodationForm
from register.models.accommodation import Accomm, AccommNight
from register.views.core import RegisterStep


class AccommodationView(RegisterStep):
    template_name = 'register/page/accommodation.html'
    title = 'Accommodation'
    form_class = AccommodationForm

    def get_initial(self):
        user = self.request.user
        initial = {}

        try:
            accomm = user.attendee.accomm
        except Accomm.DoesNotExist:
            return initial

        for field in accomm._meta.get_fields():
            if field.is_relation:
                continue
            initial[field.name] = getattr(accomm, field.name)

        initial['accomm'] = True
        initial['nights'] = [night.form_name for night in accomm.nights.all()]

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['attendee'] = self.request.user.attendee
        return kwargs

    def form_valid(self, form):
        attendee = self.request.user.attendee
        data = form.cleaned_data.copy()

        nights = data.pop('nights')
        if not data.pop('accomm'):
            Accomm.objects.filter(attendee=attendee).delete()
            return super().form_valid(form)

        accomm, created = Accomm.objects.update_or_create(
            attendee=attendee, defaults=data)
        attendee.accomm = accomm

        stored_nights = set(accomm.nights.all())
        requested_nights = set()
        for night in nights:
            date = parse_date(night.split('_')[1])
            requested_nights.add(AccommNight.objects.get(date=date))

        accomm.nights.remove(*(stored_nights - requested_nights))
        accomm.nights.add(*(requested_nights - stored_nights))

        return super().form_valid(form)
