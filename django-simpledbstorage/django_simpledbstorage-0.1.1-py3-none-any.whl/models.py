from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.urls import reverse
from django.db.models.signals import post_delete
from django.utils.crypto import get_random_string
import os

from django.db import models, IntegrityError

class DbFile(models.Model):
    name = models.CharField("File name", max_length=255, unique=True)
    size = models.PositiveIntegerField("File size")
    data = models.BinaryField("Content")
    media_type = models.CharField("MIME Type", max_length=127)
    created = models.DateTimeField("Creation date", auto_now_add=True)
