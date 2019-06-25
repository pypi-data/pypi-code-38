from django import test
from django.core.mail import EmailMultiAlternatives

from ievv_opensource.ievv_developemail.email_backend import DevelopEmailBackend
from ievv_opensource.ievv_developemail.models import DevelopEmail


class TestDevelopEmailBackend(test.TestCase):
    def _create_email_object(self, subject, message, from_email, recipient_list,
                             html_message=None):
        mail = EmailMultiAlternatives(subject, message, from_email, recipient_list)
        if html_message:
            mail.attach_alternative(html_message, 'text/html')
        return mail

    def test_send_single_simple_message(self):
        mail = self._create_email_object(subject='Testsubject', message='Testmessage',
                                         from_email='test@example.com',
                                         recipient_list=['recipient@example.com'])
        DevelopEmailBackend().send_messages([mail])
        self.assertEqual(DevelopEmail.objects.count(), 1)
        developemail = DevelopEmail.objects.first()
        self.assertEqual(developemail.subject, 'Testsubject')
        self.assertEqual(developemail.from_email, 'test@example.com')
        self.assertEqual(developemail.to_emails, 'recipient@example.com')
        self.assertEqual(developemail.plaintext_message, 'Testmessage')

    def test_send_messages_html(self):
        mail = self._create_email_object(subject='Testsubject', message='Testmessage',
                                         from_email='test@example.com',
                                         recipient_list=['recipient@example.com'],
                                         html_message='This is a <strong> message')
        DevelopEmailBackend().send_messages([mail])
        self.assertEqual(DevelopEmail.objects.count(), 1)
        developemail = DevelopEmail.objects.first()
        self.assertEqual(developemail.plaintext_message, 'Testmessage')
        self.assertEqual(developemail.html_message, 'This is a <strong> message')

    def test_send_messages_attachments(self):
        mail = self._create_email_object(subject='Testsubject', message='Testmessage',
                                         from_email='test@example.com',
                                         recipient_list=['recipient@example.com'],
                                         html_message='This is a <strong> message')
        mail.attach(filename='test1.txt', content='testcontent1')
        mail.attach(filename='test2.txt', content='testcontent2')
        DevelopEmailBackend().send_messages([mail])
        self.assertEqual(DevelopEmail.objects.count(), 1)
        developemail = DevelopEmail.objects.first()
        self.assertEqual(developemail.plaintext_message, 'Testmessage')
        self.assertEqual(developemail.html_message, 'This is a <strong> message')
        attachments = developemail.get_attachment_dict(include_payload=True)
        self.assertEqual(dict(attachments), {
            'test1.txt': {
                'filename': 'test1.txt',
                'content_type': 'text/plain',
                'payload': b'testcontent1'
            },
            'test2.txt': {
                'filename': 'test2.txt',
                'content_type': 'text/plain',
                'payload': b'testcontent2'
            }
        })
