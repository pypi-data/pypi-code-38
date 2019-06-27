from django.core.management.base import BaseCommand
from CTUtil.email import send_cingta_email, BaseEmail, EmailTypes


def test_send_email(email: str):
    send_cingta_email(title='测试', to_email=[email], msg='测试发送邮件')


def test_send_nomal_model(email: str):
    send_cingta_email(title='测试', to_email=[email], model=EmailTypes.BUG)


def test_send_trd_model(email: str):
    send_cingta_email(title='测试', to_email=[email], model=SendTestEmail)


class SendTestEmail(BaseEmail):
    template: str = 'test.html'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-n', dest='name')
        parser.add_argument(
            '-t', dest='test', action='store_true', default=False)
        parser.add_argument(
            '-m', dest='model', action='store_true', default=False)

    def handle(self, *args, **options):
        name: str = options.setdefault('name', '')
        if not name:
            raise ValueError('Not email to send')
        if options.setdefault('test'):
            if options.setdefault('model'):
                test_send_nomal_model(name)
            else:
                test_send_trd_model(name)
        else:
            test_send_email(name)