import logging

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import requests

from register.forms.attendee import ContactInformationForm
from register.models.attendee import Attendee
from register.views.core import RegisterStep

log = logging.getLogger(__name__)


class ContactInformationView(RegisterStep):
    title = 'Contact Information'
    form_class = ContactInformationForm

    def get_initial(self):
        user = self.request.user
        initial = {
            'name': user.get_full_name(),
            'nametag_3': user.username,
            'email': user.email,
            'phone': user.userprofile.contact_number,
        }

        try:
            attendee = user.attendee
            for field in attendee._meta.get_fields():
                if field.is_relation:
                    continue
                initial[field.name] = getattr(attendee, field.name)
        except ObjectDoesNotExist:
            pass

        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data.copy()

        name = data.pop('name')
        if user.get_full_name() != name:
            names = name.split(None, 1)
            if len(names) == 1:
                names.append('')
            user.first_name, user.last_name = names

        email_changed = user.email != data['email']
        user.email = data.pop('email')

        user.save()

        user.userprofile.contact_number = data.pop('phone')
        user.userprofile.save()

        if not settings.SANDBOX:
            self.subscribe_to_lists(data, email_changed)

        user.attendee, created = Attendee.objects.update_or_create(
            user=user, defaults=data)

        return super().form_valid(form)

    def subscribe_to_lists(self, data, email_changed):
        user = self.request.user
        try:
            attendee = user.attendee
        except Attendee.DoesNotExist:
            attendee = Attendee()

        subscribe = []
        for list_ in ('announce', 'discuss'):
            key = 'register_{}'.format(list_)
            request_subscription = data[key]
            already_registered = getattr(attendee, key)
            if request_subscription and (
                    email_changed or not already_registered):
                subscribe.append('debconf-{}'.format(list_))
        if subscribe:
            requests.post(
                'https://lists.debian.org/cgi-bin/subscribe.pl',
                data={
                    'user_email': user.email,
                    'subscribe': subscribe,
                })
            log.info('Subscribed %s to %r', user.email, subscribe)
