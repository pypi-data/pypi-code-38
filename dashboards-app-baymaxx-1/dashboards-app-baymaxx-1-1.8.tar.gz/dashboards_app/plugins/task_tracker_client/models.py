from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from cms.models import CMSPlugin
from django.utils import timezone

from dashboards_app.blero_utils.client_utils.client_to_server import delete_server_plugin



def one_year_before():
    return timezone.now() + timezone.timedelta(days=-365)


@python_2_unicode_compatible
class TaskHolder(CMSPlugin):
    holder_label = models.CharField(
        blank=False,
        max_length=200,
    )

    since_date = models.DateField(default=one_year_before)
    only_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.holder_label

    def delete(self):
        delete_server_plugin(self)

        super(TaskHolder, self).delete()

class TaskDetail(models.Model):
    model = models.ForeignKey(TaskHolder, on_delete=models.CASCADE, related_name='task')
    date_created = models.DateField(default=timezone.now)
    date_completed = models.DateField(null=True)
    is_complete = models.BooleanField(default=False)
    task_title = models.CharField(blank=False, max_length=250, default='New Task')
    task_body = models.TextField()


class PluginPosition(models.Model):
    model = models.ForeignKey(TaskHolder, on_delete=models.CASCADE)
    is_resized = models.BooleanField(default=False)
    width = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=50, null=True)
    top = models.CharField(max_length=50, null=True)
    left = models.CharField(max_length=50, null=True)




