from django.db import models


class GiosgappInstallationBaseModel(models.Model):
    """
    Store for persistent bot token, and any (protocol-specific) app-installation-specific data
    """
    installed_org_uuid = models.UUIDField()
    persistent_bot_token = models.TextField()
    persistent_token_prefix = models.CharField(max_length=255)

    class Meta:
        abstract = True
