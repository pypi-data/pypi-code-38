from django.db import models
from django.contrib.postgres.fields import JSONField
#from django.contrib.auth.models import User


# Create your models here.



class OrganisationGrafana(models.Model):
    object_project_id = models.IntegerField(default=0)
    organisation_id = models.IntegerField(default=0)


class DashboardGrafana(models.Model):
    organisation = models.ForeignKey(OrganisationGrafana, default=None, blank=True, null=True,
                                     related_name='organisation_dashboard_grafana',on_delete=models.CASCADE)
    object_project_id = models.IntegerField(default=0)
    title = models.CharField(default='', max_length=100)
    dashboard_uid = models.CharField(max_length=15, default='')
    dashboard_id = models.IntegerField(default=0)
    dashboard_content = JSONField(default={})

class FolderGrafana(models.Model):
    object_project_id = models.IntegerField(default=0)
    folder_id = models.IntegerField(default=0)
    folder_uid =models.CharField(max_length=15, default='')
    name = models.CharField(max_length=255,default='')

class PanelGrafana(models.Model):
    object_project_id = models.IntegerField(default=0)
    # dashboard = models.ForeignKey(DashboardGrafana, default=None, blank=True, null=True,
    #                               related_name='panel_dashboard_grafana')
    panel_id = models.IntegerField(default=0)
    panel_content = JSONField(default={})

class DashboardPanelsGrafana(models.Model):
    dashboard = models.ForeignKey(DashboardGrafana, default=None, blank=True, null=True,
                                  related_name='dashboard_panel_dashboard_grafana',on_delete=models.CASCADE)
    panel = models.ForeignKey(PanelGrafana, default=None, blank=True, null=True,
                              related_name='dashboard_panel_panel_grafana',on_delete=models.CASCADE)

class RowsDashboardGrafana(models.Model):
    object_project_id = models.IntegerField(default=0)
    dashboard = models.ForeignKey(DashboardGrafana, default=None, blank=True, null=True,
                                  related_name='row_dashboard_grafana',on_delete=models.CASCADE)
    title = models.CharField(default='', max_length=100)
    panels = models.ManyToManyField(PanelGrafana, related_name='paneles_by_rows_grafana_dashboard', default=None,
                                    blank=True)
    row_content = JSONField(default={})

class DjangoGrafanaUser(models.Model):
    user_project_id = models.IntegerField(default=0)
    grafana_user_id = models.IntegerField(default=0)
