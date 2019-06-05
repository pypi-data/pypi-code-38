from ohm2_handlers_light import utils as ohm2_handlers_light_utils
from . import models


def get_or_none_organisation_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.OrganisationGrafana, **kwargs)


def create_organisation_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_create(models.OrganisationGrafana, **kwargs)


def get_or_none_dashboard_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.DashboardGrafana, **kwargs)


def get_or_none_panel_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.PanelGrafana, **kwargs)


def get_or_none_dashboard_panel_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.DashboardPanelsGrafana, **kwargs)


def get_or_none_folder_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.FolderGrafana, **kwargs)


def get_or_none_rows_dashboard(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.RowsDashboardGrafana, **kwargs)


def get_or_none_user_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(models.DjangoGrafanaUser, **kwargs)
