from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    username = models.CharField("Name of User", max_length=30, unique=True)
    email = models.EmailField("email address", max_length=100, unique=True)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=
        "Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts."
        ,
    )
    dateJoined = models.DateTimeField("date joined", auto_now_add=True)
    role = models.CharField(max_length=255, verbose_name="用户角色")
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]


class UserGroup(models.Model):
    group_id = models.IntegerField(default=0)  # 对应于hac_id
    name = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, default="ACTIVE", choices=(
            ("ACTIVE", "启用"),
            ("DELETED", "删除"),
            ("PAUSED", "停用"),
        )
    )
    created = models.DateTimeField("创建时间", auto_now_add=True)
    updated = models.DateTimeField("更新时间", auto_now=True)
    creator_id = models.IntegerField("创建者", default=1)
