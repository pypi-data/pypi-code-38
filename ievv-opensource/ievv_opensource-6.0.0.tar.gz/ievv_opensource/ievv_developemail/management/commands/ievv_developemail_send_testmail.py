# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send a test email.'

    def add_arguments(self, parser):
        parser.add_argument('--from', dest='from_email', default=settings.DEFAULT_FROM_EMAIL,
                            help='From email - defaults to DEFAULT_FROM_EMAIL setting.')
        parser.add_argument('--to', dest='to_email', required=True,
                            action='append',
                            help='To email address(es). Can be repeated to send to multiple emails.')
        parser.add_argument('--html', dest='html',
                            required=False, action='store_true', default=False,
                            help='Send html email.')
        parser.add_argument('--message-html', dest='message_html', default='',
                            help='Can be used with --html to override the HTML email message. If not '
                                 'specified, we use a lorem ipsum message.')
        parser.add_argument('--message-plain', dest='message_plain', default='',
                            help='Can be override the plain text email message. If not '
                                 'specified, we use a lorem ipsum message.')
        parser.add_argument('--use-cradmin-email', dest='use_cradmin_email',
                            required=False, action='store_true',
                            help='Use django_cradmin.apps.cradmin_email.emailutils.AbstractEmail '
                                 'instead of just the send_mail() function.')

    def get_plaintext_message(self):
        if self.options['message_plain']:
            return self.options['message_plain']
        return 'Maecenas faucibus mollis interdum. Cum sociis ' \
               'natoque penatibus et magnis dis parturient montes, ' \
               'nascetur ridiculus mus. Praesent commodo cursus magna, ' \
               'vel scelerisque nisl consectetur et. Fusce dapibus, ' \
               'tellus ac cursus commodo, tortor mauris condimentum ' \
               'nibh, ut fermentum massa justo sit amet risus. Etiam ' \
               'porta sem malesuada magna mollis euismod. Cras mattis ' \
               'consectetur purus sit amet fermentum. Donec ullamcorper ' \
               'nulla non metus auctor fringilla.' \
               '\n\n' \
               'Duis mollis, est non commodo luctus, nisi erat porttitor ' \
               'ligula, eget lacinia odio sem nec elit. Maecenas sed diam ' \
               'eget risus varius blandit sit amet non magna. Vivamus ' \
               'sagittis lacus vel augue laoreet rutrum faucibus dolor ' \
               'auctor. Maecenas sed diam eget risus varius blandit sit ' \
               'amet non magna. Curabitur blandit tempus porttitor. ' \
               'Etiam porta sem malesuada magna mollis euismod. Vestibulum ' \
               'id ligula porta felis euismod semper.'

    def get_html_message(self):
        if self.options['message_html']:
            return self.options['message_html']
        return 'Maecenas <strong>faucibus</strong> mollis interdum. Cum sociis ' \
               'natoque penatibus et magnis dis parturient montes, ' \
               'nascetur ridiculus mus. Praesent commodo cursus magna, ' \
               'vel scelerisque nisl consectetur et. Fusce dapibus, ' \
               'tellus ac cursus commodo, tortor mauris condimentum ' \
               'nibh, ut fermentum massa justo sit amet risus. Etiam ' \
               'porta sem malesuada magna mollis euismod. Cras mattis ' \
               'consectetur purus sit amet fermentum. Donec ullamcorper ' \
               'nulla non metus auctor fringilla.' \
               '<br><br>' \
               '<em>Duis mollis</em>, est non commodo luctus, nisi erat porttitor ' \
               'ligula, eget lacinia odio sem nec elit. Maecenas sed diam ' \
               'eget risus varius blandit sit amet non magna. Vivamus ' \
               'sagittis lacus vel augue laoreet rutrum faucibus dolor ' \
               'auctor. <a href="http://example.com">Maecenas sed</a> ' \
               'diam eget risus varius blandit sit ' \
               'amet non magna. Curabitur blandit tempus porttitor. ' \
               'Etiam porta sem malesuada magna mollis euismod. Vestibulum ' \
               'id ligula porta felis euismod semper.'

    def get_email_kwargs(self):
        kwargs = {
            'subject': 'Test email',
            'message': self.get_plaintext_message(),
            'from_email': self.options['from_email'],
            'recipient_list': self.options['to_email']
        }
        if self.options['html']:
            kwargs['html_message'] = self.get_html_message()
        return kwargs

    def make_cradmin_email(self):
        from django_cradmin.apps.cradmin_email import emailutils

        class CradminEmail(emailutils.AbstractEmail):
            html_message_template = 'ievv_developemail/cradmin_email/html_message.django.html'

            def __init__(self, subject, html_message=None, **kwargs):
                self.subject = subject
                extra_context_data = kwargs.pop('extra_context_data', None) or {}
                extra_context_data['html_message'] = html_message
                kwargs['extra_context_data'] = extra_context_data
                super().__init__(**kwargs)

            def render_subject(self):
                return self.subject

        email_kwargs = self.get_email_kwargs()
        return CradminEmail(subject=email_kwargs['subject'],
                            from_email=email_kwargs['from_email'],
                            recipient_list=email_kwargs['recipient_list'],
                            html_message=email_kwargs['html_message'])

    def handle(self, *args, **options):
        self.options = options
        use_cradmin_email = options['use_cradmin_email']
        if use_cradmin_email and not options['html']:
            self.stderr.write('--use-cradmin-email requires --html')
            raise SystemExit()
        if use_cradmin_email:
            self.make_cradmin_email().send()
        else:
            send_mail(**self.get_email_kwargs())
