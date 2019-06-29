
from django.db import models
from django.db.models import Q, Count, Sum
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth import get_user_model
from django.dispatch import receiver


from aparnik.utils.utils import field_with_prefix
User = get_user_model()


class AuditManager(models.Manager):
    def get_queryset(self):
        return super(AuditManager, self).get_queryset()


class Audit(models.Model):

    ACTION_LOGIN = 'li'
    ACTION_LOGOUT = 'lo'
    ACTION_LOGIN_FAILED = 'lf'
    ACTION_CHOICES = (
        (ACTION_LOGIN, _('Action login')),
        (ACTION_LOGOUT, _('Action logout')),
        (ACTION_LOGIN_FAILED, _('Action login failed')),
    )

    action = models.CharField(max_length=64, choices=ACTION_CHOICES, verbose_name=_('Action'))
    ip = models.GenericIPAddressField(null=True, verbose_name=_('IP'))
    user_obj = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('User'))
    extra = models.TextField(null=True, blank=True, verbose_name=_('Extra data'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = AuditManager()

    def __str__(self):
        return '{0} - {1}'.format(self.action, self.ip)

    @staticmethod
    def sort_audit(return_key='audit', prefix='', type=ACTION_LOGIN):
        display = None
        for x in Audit.ACTION_CHOICES:
            if x[0] == type:
                display = x[1]
                break
        if prefix != '':
            field = 'id'
        else:
            field = 'ip'

        sort = {
            return_key + type: {
                'label': display,
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Count(field_with_prefix(field=field, prefix=prefix), filter=Q(**{field_with_prefix(prefix=prefix, field='action'): type}))
                },
                'key_sort': 'sort_count',
            }
        }
        return sort


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    Audit.objects.create(action=Audit.ACTION_LOGIN, ip=ip, user_obj=user)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    Audit.objects.create(action=Audit.ACTION_LOGOUT, ip=ip, user_obj=user)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    username = credentials.get('username', None)
    ip = request.META.get('REMOTE_ADDR')
    user = None
    if username:
        try:
            user = User.objects.get(username=username)
            # در این حالت فقط زمانی که یوزر نیم پیدا نشه لاگ یوزر نیم ثبت میشه و از افزونگی داده جلوگیری می کنه
            username = None
        except:
            pass
    Audit.objects.create(action=Audit.ACTION_LOGIN_FAILED, ip=ip, user_obj=user, extra=username)