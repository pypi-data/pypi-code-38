from djangohelper.db import models


class FriendLink(models.Model):
    site_name = models.CharField(max_length=32)
    url = models.URLField()
    show_flag = models.BooleanField(default=True)
    date_start = models.DateField(auto_created=True)
    date_end = models.DateField(default='9999-12-31', blank=True, null=True)
    logo = models.ImageField(default=None, null=True, blank=True)
