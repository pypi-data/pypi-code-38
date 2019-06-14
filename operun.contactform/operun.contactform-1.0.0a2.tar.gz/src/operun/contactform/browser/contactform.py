# -*- coding: utf-8 -*-

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from operun.contactform import _
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import logging
import re


logger = logging.getLogger('operun.contactform')


class ContactFormView(BrowserView):

    template = ViewPageTemplateFile('templates/contactform.pt')
    template_success = ViewPageTemplateFile('templates/contactform_success.pt')

    # The "form_fields" list serves a few functions...
    # 1. It controls what fields and values are allowed
    #    to be passed to the E-Mail templates.
    # 2. It acts as a required list, where the boolean operand denotes
    #    the status of a field.

    form_fields = [
        ('title', False),
        ('name', True),
        ('company', False),
        ('phone', False),
        ('email', True),
        ('subject', True),
        ('message', True),
        ('dsgvo', True),
    ]

    def __call__(self):
        self.errors = list()
        self.fields = [field for field, required in self.form_fields]
        self.required = [
            field for field, required in self.form_fields if required
        ]
        self.form = self.request.form
        if self.form.get('form.buttons.submit', ''):
            if self._validate_form():
                if self._send_mail():
                    return self.template_success()
        return self.template()

    def _validate_form(self):
        """
        Validate the form fields.
        """
        for field in self.fields:
            field_value = self.form.get(field, '')
            # If the field has a value, validate it
            if field_value:
                if field == 'email':
                    if not re.match('[^@]+@[^@]+\.[^@]+', field_value):
                        self.errors.append(field)
            # Else, field has no value, so check if it is required instead
            elif field in self.required:
                self.errors.append(field)
        if self.errors:
            self.show_validate_error_message()
            return False
        return True

    def _send_mail(self):
        """
        Send E-Mails to admin and user.
        """
        form_data = dict()
        # Create a dictionary of form values to be
        # passed to the E-Mail templates.
        # We DO NOT pass "self.form" directly, as it could contain unwanted
        # fields or submitted data.
        for field in self.fields:
            form_data[field] = self.form.get(field, '')
        # Assign some default values
        portal_address = api.portal.get_registry_record(
            'plone.email_from_address'
        )
        form_address = self.form.get('email', '')
        form_subject = self.form.get('subject', '')
        # We create a list of recipients with their associated E-Mail
        # template, and "send_email" configuration.
        mailing_list = {
            'admin': {
                'template': '@@mailto_admin',
                'subject': form_subject,
                'sender': form_address,
                'recipient': portal_address,
            },
            'user': {
                'template': '@@mailto_user',
                'subject': u'operun contact confirmation',
                'sender': portal_address,
                'recipient': form_address,
            },
        }
        for user in mailing_list:
            try:
                # We fetch the registered E-Mail template...
                mail_view = self.context.restrictedTraverse(
                    mailing_list[user]['template']
                )
                # We parse it with our "form_data" values...
                mail_body = mail_view(
                    self.context,
                    header=mailing_list[user]['subject'],
                    **form_data
                ).encode('utf-8')
                # We use MIMEMultipart to create an HTML
                # Content-Disposition header.
                # See: https://docs.plone.org/develop/plone.api/docs/portal.html#send-e-mail  # noqa: 501
                message = MIMEMultipart('alternative')
                part = MIMEText(mail_body, 'html', 'utf-8')
                message.attach(part)
                # We attempt to send the E-Mail
                api.portal.send_email(
                    immediate=True,
                    body=message.as_string(),
                    subject=mailing_list[user]['subject'],
                    sender=mailing_list[user]['sender'],
                    recipient=mailing_list[user]['recipient'],
                )
            except Exception as err:
                logger.error(err)
                self.errors.append('mail_{0}'.format(user))
        if self.errors:
            self.show_send_error_message()
            return False
        return True

    def get_classname(self, field='', classname=''):
        """
        Return additional classname if there is an error.
        """
        # If field in "self.required", append classname...
        if field in self.required:
            classname = '{0} required'.format(classname)
        # If field in "self.errors", append classname...
        if field in self.errors:
            return '{0} error'.format(classname)
        # Else return the default classname
        return classname

    def show_send_error_message(self):
        """
        Set portal send error message.
        """
        api.portal.show_message(
            _(
                u'contact_sendmail_error',
                default=(
                    u'Something went wrong, please '
                    u'contact the site administrator.'
                ),
            ),
            self.request,
            'error',
        )

    def show_validate_error_message(self):
        """
        Set portal validate error message.
        """
        api.portal.show_message(
            _(
                u'contact_validation_error',
                default=u'Something went wrong, please check the input!',
            ),
            self.request,
            'error',
        )
