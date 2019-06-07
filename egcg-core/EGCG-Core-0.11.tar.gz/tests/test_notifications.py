import pytest
from unittest.mock import Mock, patch
from os import remove
from os.path import join, abspath, dirname
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from egcg_core import notifications as n
from egcg_core.exceptions import EGCGError
from tests import TestEGCG


class FakeSMTP(Mock):
    def __init__(self, host, port):
        super().__init__()
        self.mailhost, self.port = host, port

    @staticmethod
    def send_message(msg, reporter, recipients):
        if 'dodgy' in str(msg):
            raise SMTPException('Oh noes!')
        else:
            pass

    @staticmethod
    def quit():
        pass


class TestNotificationCentre(TestEGCG):
    def setUp(self):
        self.notification_centre = n.NotificationCentre('a_name')

    def test_config_init(self):
        e = self.notification_centre.subscribers['email']
        assert e.email_sender.sender == 'this'
        assert e.email_sender.recipients == ['that', 'other']
        assert e.email_sender.mailhost == 'localhost'
        assert e.email_sender.port == 1337
        assert e.strict is True

        a = self.notification_centre.subscribers['asana']
        assert a.workspace_id == 1337
        assert a.project_id == 1338

    def test_notify(self):
        self.notification_centre.subscribers = {'asana': Mock(), 'email': Mock()}
        self.notification_centre.notify_all('a message')
        for name, s in self.notification_centre.subscribers.items():
            s.notify.assert_called_with('a message')

    @patch.object(n.NotificationCentre, 'critical')
    def test_notify_failure(self, mocked_log):
        self.notification_centre.subscribers = {
            'asana': Mock(notify=Mock(side_effect=EGCGError('Something broke'))),
            'email': Mock(notify=Mock(side_effect=ValueError('Something else broke')))
        }
        with self.assertRaises(EGCGError) as e:
            self.notification_centre.notify('a message', ('asana', 'email'))

        mocked_log.assert_called()
        assert str(e.exception) == (
            'Encountered the following errors during notification: '
            'EGCGError: Something broke, '
            'ValueError: Something else broke'
        )


class TestLogNotification(TestEGCG):
    def setUp(self):
        self.notification_log = join(self.assets_path, 'LogNotification.log')
        self.ntf = n.LogNotification('log_notification', self.notification_log)

    def tearDown(self):
        remove(self.notification_log)

    def test_notify(self):
        self.ntf.notify('message')
        with open(self.notification_log) as open_file:
            assert '[log_notification] message' in open_file.read()

    def _test_notify_with_attachments(self, attachments):
        attachment = join(self.assets_path, 'test_to_upload.txt')
        self.ntf.notify('message', attachments=attachments)
        with open(self.notification_log) as open_file:
            data = open_file.read().split('\n')
            assert '[log_notification] message' in data[0]
            assert '[log_notification] Attachment: %s' % attachment in data[1]

    def test_notify_with_attachment(self):
        self._test_notify_with_attachments([join(self.assets_path, 'test_to_upload.txt')])

    def test_notify_with_attachments(self):
        self._test_notify_with_attachments(join(self.assets_path, 'test_to_upload.txt'))


class TestEmailSender(TestEGCG):
    def setUp(self):
        self.email_sender = n.EmailSender(
            'a_subject', 'localhost', 1337, 'a_sender', ['some', 'recipients'],
            email_template=join(self.etc, 'email_notification.html')
        )

    @patch('egcg_core.notifications.email.EmailSender._logger')
    def test_retries(self, mocked_logger):
        self.email_sender.email_template = None
        with patch('smtplib.SMTP', new=FakeSMTP), patch('egcg_core.notifications.email.sleep'):
            assert self.email_sender._try_send(self.email_sender._build_email(text_message='this is a test')) is True
            assert self.email_sender._try_send(self.email_sender._build_email(text_message='dodgy')) is False
            for i in range(3):
                mocked_logger.warning.assert_any_call(
                    'Encountered a %s exception. %s retries remaining', 'Oh noes!', i
                )

            with pytest.raises(EGCGError) as e:
                self.email_sender.send_email(text_message='dodgy')
                assert 'Failed to send message: dodgy' in str(e)

    def test_build_email(self):
        exp_msg = (
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <meta charset="UTF-8">\n'
            '    <style>\n'
            '        table, th, td {\n'
            '            border: 1px solid black;\n'
            '            border-collapse: collapse;\n'
            '        }\n'
            '    </style>\n'
            '</head>\n'
            '<body>\n'
            '    <h2>a_subject</h2>\n'
            '    <p>a message</p>\n'
            '</body>\n'
            '</html>'
        )

        exp = MIMEText(exp_msg, 'html')
        exp['Subject'] = 'a_subject'
        exp['From'] = 'a_sender'
        exp['To'] = 'some, recipients'
        obs = self.email_sender._build_email(title='a_subject', body='a message')
        assert str(obs) == str(exp)

    def test_build_email_plain_text(self):
        self.email_sender.email_template = None
        exp = MIMEText('a message')
        exp['Subject'] = 'a_subject'
        exp['From'] = 'a_sender'
        exp['To'] = 'some, recipients'
        obs = self.email_sender._build_email(text_message='a message')
        assert str(obs) == str(exp)

    def _test_build_email_attachments(self, attachements):
        attachment = join(self.assets_path, 'test_to_upload.txt')
        self.email_sender.email_template = None
        exp = MIMEMultipart()
        exp['Subject'] = 'a_subject'
        exp['From'] = 'a_sender'
        exp['To'] = 'some, recipients'
        obs = self.email_sender._build_email(text_message='a message', attachments=attachements)
        payload = obs.get_payload()
        assert len(payload) == 2
        assert str(payload[0]) == str(MIMEText('a message'))
        with open(attachment, 'rb') as open_file:
            part = MIMEApplication(
                open_file.read(),
                Name='test_to_upload.txt'
            )
            part['Content-Disposition'] = 'attachment; filename="test_to_upload.txt"'
            assert str(payload[1]) == str(part)

    def test_build_email_attachments(self):
        attachment = join(self.assets_path, 'test_to_upload.txt')
        self._test_build_email_attachments([attachment])

    def test_build_email_attachment(self):
        attachment = join(self.assets_path, 'test_to_upload.txt')
        self._test_build_email_attachments(attachment)


class TestEmailNotification(TestEGCG):
    def setUp(self):
        self.ntf = n.EmailNotification('a_subject', 'localhost', 1337, 'a_sender', ['some', 'recipients'], strict=True)
        self.ntf2 = n.EmailNotification(
            'a_subject', 'localhost', 1337, 'a_sender', ['some', 'recipients'], strict=True,
            email_template=join(dirname(dirname(abspath(__file__))), 'etc', 'email_notification.html')
        )

    @patch.object(n.EmailSender, 'send_email')
    def test_notify(self, mock_send_email):
        self.ntf.notify('a message')
        mock_send_email.assert_called_once_with(text_message='a message', attachments=None)

        mock_send_email.reset_mock()
        self.ntf2.notify('a message')
        mock_send_email.assert_called_once_with(title='a_subject', body='a&nbspmessage', attachments=None)

    @patch.object(n.EmailSender, 'send_email', side_effect=EGCGError)
    def test_notify_fail(self, mock_send_email):
        with pytest.raises(EGCGError) as excinfo:
            self.ntf.notify('a message')
        assert 'Failed to send message: a message' in str(excinfo)


@patch('egcg_core.notifications.email.EmailSender._try_send')
def test_send_plain_text_email(mocked_send):
    n.send_plain_text_email('a message', 'localhost', 1337, 'a_sender', ['some', 'recipients'], 'a subject')
    exp = MIMEText('a message')
    exp['Subject'] = 'a subject'
    exp['From'] = 'a_sender'
    exp['To'] = 'some, recipients'
    assert str(mocked_send.call_args[0][0]) == str(exp)


@patch('egcg_core.notifications.email.EmailSender._try_send')
def test_send_html_email(mocked_send):
    email_template = join(dirname(dirname(abspath(__file__))), 'etc', 'email_notification.html')

    n.send_html_email('localhost', 1337, 'Sender', ['reciptient1', 'reciptient2'], 'Subject',
                      email_template=email_template, title='title', body='body')
    exp_msg = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <style>\n'
        '        table, th, td {\n'
        '            border: 1px solid black;\n'
        '            border-collapse: collapse;\n'
        '        }\n'
        '    </style>\n'
        '</head>\n'
        '<body>\n'
        '    <h2>title</h2>\n'
        '    <p>body</p>\n'
        '</body>\n'
        '</html>'
    )
    exp = MIMEText(exp_msg, 'html')
    exp['Subject'] = 'Subject'
    exp['From'] = 'Sender'
    exp['To'] = 'reciptient1, reciptient2'
    assert str(mocked_send.call_args[0][0]) == str(exp)


@patch('egcg_core.notifications.email.send_plain_text_email')
@patch('egcg_core.notifications.email.send_html_email')
def test_send_email(mocked_html, mocked_plain_text):
    email_template = join(dirname(dirname(abspath(__file__))), 'etc', 'email_notification.html')

    n.send_email('a message', 'localhost', 1337, 'Sender', ['recipient1', 'recipient2'], 'Subject')
    assert mocked_plain_text.call_count == 1
    assert mocked_html.call_count == 0

    n.send_email(None, 'localhost', 1337, 'Sender', ['Recipients'], 'Subject', email_template, a_jinja2='arg')
    mocked_html.assert_called_with('localhost', 1337, 'Sender', ['Recipients'], 'Subject', email_template, None, a_jinja2='arg')

    # Adding message and template means the template is used and the msg is only passed and most likely ignored
    n.send_email('msg', 'localhost', 1337, 'Sender', ['Recipients'], 'Subject', email_template, a_jinja2='arg')
    mocked_html.assert_called_with('localhost', 1337, 'Sender', ['Recipients'], 'Subject', email_template, None, a_jinja2='arg', msg='msg')


class TestAsanaNotification(TestEGCG):
    def setUp(self):
        self.ntf = n.AsanaNotification(
            'another_name',
            workspace_id=1337,
            project_id=1338,
            access_token='an_access_token'
        )
        self.ntf.client = Mock(
            tasks=Mock(
                find_all=Mock(return_value=[{'name': 'this'}]),
                create_in_workspace=Mock(return_value={'id': 1337}),
                find_by_id=Mock(return_value={'name': 'this', 'id': 1337})
            )
        )

    def test_task(self):
        assert self.ntf.task == {'id': 1337, 'name': 'this'}
        self.ntf.client.tasks.find_by_id.assert_called_with(1337)

    def test_add_comment(self):
        self.ntf.notify('a comment')
        self.ntf.client.tasks.add_comment.assert_called_with(1337, text='a comment')

    def _test_add_comment_with_attachments(self, attachments):
        self.ntf.notify('a comment', attachments=attachments)
        self.ntf.client.tasks.add_comment.assert_called_with(1337, text='a comment')
        self.ntf.client.attachments.create_on_task.assert_called_with(
            file_content=b'test content',
            file_name='test_to_upload.txt',
            task_id=1337
        )

    def test_add_comment_with_attachments(self):
        self._test_add_comment_with_attachments([join(self.assets_path, 'test_to_upload.txt')])

    def test_add_comment_with_one_attachment(self):
        self._test_add_comment_with_attachments(join(self.assets_path, 'test_to_upload.txt'))

    def test_get_entity(self):
        collection = [{'name': 'this'}, {'name': 'that'}]
        assert self.ntf._get_entity(collection, 'that') == {'name': 'that'}
        assert self.ntf._get_entity(collection, 'other') is None

    def test_create_task(self):
        assert self.ntf._create_task() == {'id': 1337}
        self.ntf.client.tasks.create_in_workspace.assert_called_with(1337, self.ntf.task_template)
