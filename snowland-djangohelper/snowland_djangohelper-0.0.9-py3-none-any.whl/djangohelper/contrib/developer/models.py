from django.db import models

from django.contrib.auth.models import AbstractUser as User
# from djangohelper.contrib.auth.models import User


class Application(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    access_key = models.CharField(max_length=256)
    access_secret = models.CharField(max_length=256)
    icon = models.ImageField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, auto_created=True)
    update_time = models.DateTimeField(auto_created=True, auto_now=True)


class ApplicationChangeList(models.Model):
    app_id = models.ForeignKey(Application, on_delete=models.CASCADE)
    access_key_before = models.CharField(max_length=256)
    access_key_after = models.CharField(max_length=256)
    access_secret_before = models.CharField(max_length=256)
    access_secret_after = models.CharField(max_length=256)
    change_time = models.DateTimeField(auto_now_add=True, auto_created=True)


class KeyStore(models.Model):
    app_id = models.ForeignKey(Application, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=256)
    change_time = models.DateTimeField(auto_now_add=True, auto_created=True)
