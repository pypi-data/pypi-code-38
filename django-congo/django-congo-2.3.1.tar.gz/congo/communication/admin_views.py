# -*- coding: utf-8 -*-
from congo.communication.admin_forms import SimpleEmailMessageForm
from congo.communication.classes import SimpleEmailMessage
from congo.utils.decorators import staff_required, secure_allowed
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
import logging
import sys

@secure_allowed
@staff_required
def test_mail(request):
    title = _(u"E-mail testowy")
    logger = logging.getLogger('system.test_mail')

    extra = {
        'user': request.user,
        'extra_info': {}
    }

    initial = {
        'subject': 'Lorem ipsum dolor sit amet',
        'sender_email': 'sender@example.com',
        'sender_email': settings.DEFAULT_FROM_EMAIL or "",
        'sender_name': settings.CONGO_DEFAULT_FROM_EMAIL_NAME or "",
        'recipient_email': 'johny.bravo@example.com',
        'recipient_name': 'Johny Bravo',
        'message': """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\nUt enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.""",
        'html_mimetype': True,
    }

    if request.method == 'POST':
        form = SimpleEmailMessageForm(request.POST)
        if form.is_valid():
            email_kwargs = {}

            for key in initial.keys():
                value = form.cleaned_data[key]
                if value:
                    email_kwargs[key] = value

            data_dict = {
                'email': email_kwargs.pop('message'),
            }

            extra['extra_info'].update(email_kwargs)

            try:
                del email_kwargs['html_mimetype']
                email_kwargs['mimetype'] = 'html'
            except KeyError:
                email_kwargs['mimetype'] = 'text'

            email_kwargs['template'] = 'test'

            try:
                email_message = SimpleEmailMessage(data_dict = data_dict, **email_kwargs)
                email_message.send()

                logger.info(title, extra = extra)

                messages.success(request, _(u"E-mail testowy został wysłany!"))
            except:
                exc_info = sys.exc_info()
                logger.error(title, exc_info = exc_info, extra = extra)

                messages.error(request, _(u"Wysyłanie wiadomości testowej nie powiodło się."))

    else:
        form = SimpleEmailMessageForm(initial = initial)

    extra_context = {
        'title': title,
        'has_permission': True,
        'site_url': '/',

        'form': form,
    }

    return render(request, 'congo/admin/communication/test_mail.html', extra_context)
