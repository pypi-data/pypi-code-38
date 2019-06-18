# encoding=UTF-8
from email.message import Message as stdlib_Message
import os

import mock
import pytest
import tms

import mailsend


@pytest.fixture
def environ(request):
    def fin():
        for k in list(os.environ.keys()):
            if k.startswith('MAILSEND_'):
                del os.environ[k]
    request.addfinalizer(fin)
    return os.environ


def test_it_creates_a_connection_from_url():
    c = mailsend.Mail('smtp://server.example.org/')
    assert c.port == 25
    assert c.hostname == 'server.example.org'
    assert c.username is None
    assert c.password is None
    assert c.ssl is False
    assert c.tls is False


def test_it_creates_an_SSL_connection_from_url():
    c = mailsend.Mail('smtps://')
    assert c.port == 465
    assert c.ssl is True
    assert c.tls is False


def test_it_creates_an_TLS_connection_from_url():
    c = mailsend.Mail('smtp+tls://')
    assert c.port == 25
    assert c.ssl is False
    assert c.tls is True


def test_it_sets_the_port_number_from_url():
    c = mailsend.Mail('smtp://localhost:2525/')
    assert c.port == 2525


def test_it_sets_auth_credentials_from_url():
    c = mailsend.Mail('smtp://user:pass@localhost:2525/')
    assert c.username == 'user'
    assert c.password == 'pass'


def test_env_url_takes_priority(environ):
    environ['MAILSEND_URL'] = 'smtp://server.example.org/'
    environ['MAILSEND_SERVER'] = 'another.example.org'
    c = mailsend.Mail()
    assert c.hostname == 'server.example.org'


def test_it_sets_options_from_env(environ):
    environ['MAILSEND_SERVER'] = 'server.example.org'
    environ['MAILSEND_PORT'] = '2525'
    environ['MAILSEND_USERNAME'] = 'user'
    environ['MAILSEND_PASSWORD'] = 'pass'
    environ['MAILSEND_TLS'] = '1'
    environ['MAILSEND_SSL'] = '0'
    c = mailsend.Mail()
    assert c.hostname == 'server.example.org'
    assert c.port == 2525
    assert c.username == 'user'
    assert c.password == 'pass'
    assert c.tls is True
    assert c.ssl is False


def test_it_creates_a_session():
    c = mailsend.Mail('smtp://user:pass@localhost:2525/')

    with mock.patch('mailsend.smtplib') as mocksmtplib:
        with c.connect() as conn:
            assert mocksmtplib.SMTP.call_args == mock.call('localhost', 2525)
            assert conn._smtp is mocksmtplib.SMTP()


def test_it_rewrites_recipients():
    c = mailsend.Mail(rewrite_to={'alice@example.com', 'bob@example.com'})

    with mock.patch('mailsend.smtplib') as mocksmtplib:
        c.send(sender='arthur@example.com',
               recipients=['barbara@example.com', 'charlie@example.com'],
               body='test',
               subject='test')

        assert mocksmtplib.SMTP().sendmail.call_args == \
            mock.call('arthur@example.com',
                      {'alice@example.com', 'bob@example.com'},
                      tms.Anything(),
                      mail_options=[])


def test_it_bccs_recipients():
    c = mailsend.Mail(bcc={'alice@example.com', 'bob@example.com'})

    with mock.patch('mailsend.smtplib') as mocksmtplib:
        c.send(sender='arthur@example.com',
               recipients=['bob@example.com', 'charlie@example.com'],
               body='test',
               subject='test')

        assert mocksmtplib.SMTP().sendmail.call_args == \
            mock.call('arthur@example.com',
                      {'alice@example.com',
                       'bob@example.com',
                       'charlie@example.com'},
                      tms.Anything(),
                      mail_options=[])


def test_it_uses_smtputf8():
    c = mailsend.Mail()
    with mock.patch('mailsend.smtplib') as mocksmtplib:
        with mock.patch('mailsend.SMTPUTF8', 'SMTPUTF8'):
            c.send(sender='café@example.com',
                recipients=['bob@example.com'],
                body='test',
                subject='test')

            assert mocksmtplib.SMTP().sendmail.call_args == \
                mock.call('café@example.com',
                          {'bob@example.com'},
                          tms.Anything(),
                          mail_options=['SMTPUTF8'])


def test_it_suppresses_send():
    c = mailsend.Mail(suppress_send=True)

    with mock.patch('mailsend.smtplib') as mocksmtplib:
        c.send(sender='arthur@example.com',
            recipients=['bob@example.com'],
            body='test',
            subject='test')

        assert mocksmtplib.SMTP.call_args is None


def test_subscribe_sends_to_outbox_only():
    c = mailsend.Mail()
    with mock.patch('mailsend.smtplib') as mocksmtplib:
        with c.subscribe() as inbox:
            c.send(sender='arthur@example.com',
                    body='test', subject='test')

            assert len(inbox) == 1
            assert inbox[0].sender == 'arthur@example.com'

        # Subscribe a second time to make sure we get a fresh
        # inbox each time
        with c.subscribe() as inbox:
            c.send(sender='fenchurch@example.com',
                    body='test', subject='test')

            assert len(inbox) == 1
            assert inbox[0].sender == 'fenchurch@example.com'

        assert mocksmtplib.SMTP.call_args is None


def test_subscribe_allows_sending():
    c = mailsend.Mail()
    with mock.patch('mailsend.smtplib') as mocksmtplib:
        with c.subscribe(supress_send=False) as inbox:
            c.send(sender='arthur@example.com',
                   recipients=['alice@example.com'],
                    body='test', subject='test')
            assert len(inbox) == 1

        assert mocksmtplib.SMTP().sendmail.call_args == \
            mock.call('arthur@example.com',
                      {'alice@example.com'},
                      tms.Anything(),
                      mail_options=[])


def test_message_detects_utf8_addresses():
    utf8email = 'café@example.com'
    asciiemail = 'cafe@example.com'

    M = mailsend.Message
    assert M(asciiemail, '').has_utf8_addresses() is False
    assert M(utf8email, '').has_utf8_addresses() is True
    assert M(asciiemail, '', [asciiemail]).has_utf8_addresses() is False
    assert M(asciiemail, '', [utf8email]).has_utf8_addresses() is True
    assert M(asciiemail, '', cc=[asciiemail]).has_utf8_addresses() is False
    assert M(asciiemail, '', cc=[utf8email]).has_utf8_addresses() is True
    assert M(asciiemail, '', bcc=[asciiemail]).has_utf8_addresses() is False
    assert M(asciiemail, '', bcc=[utf8email]).has_utf8_addresses() is True
    assert M(asciiemail, '', reply_to=asciiemail).has_utf8_addresses() is False
    assert M(asciiemail, '', reply_to=utf8email).has_utf8_addresses() is True


def test_message_adds_message_id():
    m = mailsend.Message('test@example.com', '')
    assert m.as_message()['Message-Id'] is not None


def test_message_doesnt_add_duplicate_message_ids():
    m = mailsend.Message(
        'test@example.com',
        '',
        extra_headers={'Message-Id': 'foo'}
    )
    assert m.as_string().lower().count('message-id') == 1
    assert 'Message-Id: foo\n' in m.as_string()


def test_it_sends_stdlib_messages():
    c = mailsend.Mail()
    message = stdlib_Message()
    message.set_payload('hello world!')
    message['From'] = 'arthur@example.com'
    message['To'] = 'zaphod@example.com, ford@example.com'
    with mock.patch('mailsend.smtplib') as mocksmtplib:
        with c.subscribe(supress_send=False) as inbox:
            c.send(message)
            assert len(inbox) == 1

        assert mocksmtplib.SMTP().sendmail.call_args == \
            mock.call('arthur@example.com',
                      ['zaphod@example.com', 'ford@example.com'],
                      tms.Anything(),
                      mail_options=[])
