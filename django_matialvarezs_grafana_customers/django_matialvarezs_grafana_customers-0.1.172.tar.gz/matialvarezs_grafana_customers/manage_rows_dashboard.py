from . import base_row_dashboard,models,utils
from ohm2_handlers_light import utils as ohm2_handlers_light_utils


def create_row_dashboard(title, dashboard_uid, object_project_id, object_project_panel_list):
    dashboard = models.DashboardGrafana.objects.get(dashboard_uid=dashboard_uid)
    random_row_id = ohm2_handlers_light_utils.get_random_string_number(3)
    json_row = base_row_dashboard.get_base_row(title, random_row_id)

    panles_row = list()
    row = utils.get_or_none_rows_dashboard(dashboard=dashboard, object_project_id=object_project_id)
    if not row:
        row = models.RowsDashboardGrafana(dashboard=dashboard, object_project_id=object_project_id, title=title,
                                          row_content=json_row)
        row.save()
        json_row['panels'] = []

        for obj in object_project_panel_list:
            grafana_panel = models.PanelGrafana.objects.get(object_project_id=obj.id)
            json_row['panels'].append(grafana_panel.panel_content)
            panles_row.append(grafana_panel.panel_content)
            row.panels.add(grafana_panel.id)
        # json_row['panels'] = panles_row
        row.row_content = json_row
        row.save()
