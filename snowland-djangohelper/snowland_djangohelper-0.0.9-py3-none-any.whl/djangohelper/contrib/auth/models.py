from django.contrib.auth.models import AbstractUser as DAbstractUser
from django.db.models.manager import EmptyManager
from django.db import models


class AbstractUser(DAbstractUser):
    class Meta:
        abstract = True

    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    email = models.EmailField('email address', blank=True, unique=True)
    QQ = models.CharField(max_length=32, default=None, unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=15, unique=True)
    sex = models.CharField(max_length=1, default='F')
    realname = models.CharField(max_length=32, default=None, null=True, blank=True)
    IDcard = models.CharField(max_length=19, default=None, null=True, blank=True, unique=True)
    registertime = models.DateTimeField(auto_now_add=True)
    integrals = models.IntegerField(default=0)
    vip = models.IntegerField(default=0)


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
