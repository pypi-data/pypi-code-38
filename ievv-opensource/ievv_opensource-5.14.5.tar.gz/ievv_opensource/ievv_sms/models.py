from django.db import models


class DebugSmsMessage(models.Model):

    phone_number = models.CharField(max_length=50, db_index=True)

    message = models.TextField()

    send_as = models.CharField(max_length=50, null=False, blank=True, default='')

    created_datetime = models.DateTimeField(auto_now_add=True)
