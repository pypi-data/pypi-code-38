from . import models, utils, base_target
from ohm2_handlers_light import utils as ohm2_handlers_light_utils


def create_and_save_panel_database(dashboard_uid, object_project_panel_id, panel_content, **options):
    panel_id = options.get("panel_id", ohm2_handlers_light_utils.get_random_string_number(3))
    panel_content['id'] = panel_id
    dashboard = models.DashboardGrafana.objects.get(dashboard_uid=dashboard_uid)
    panel = utils.get_or_none_panel_grafana(object_project_id=object_project_panel_id)
    if not panel:
        # print("EN EL IF DE CREAR PANELS")
        panel = models.PanelGrafana(object_project_id=object_project_panel_id, panel_id=panel_id,
                                    panel_content=panel_content)
        panel.save()

        dashboard_panel = models.DashboardPanelsGrafana(dashboard=dashboard, panel=panel)
        dashboard_panel.save()
    else:
        # print("EN EL ELSE DE CREAR PANELS")
        # dashboard = models.DashboardGrafana.objects.get(dashboard_uid=dashboard_uid)
        # panel = utils.get_or_none_panel_grafana(object_project_id=object_project_panel_id)
        dashboard_panel = utils.get_or_none_dashboard_panel_grafana(dashboard=dashboard, panel=panel)
        # print("dashboard_panel EN EL ELSE DE CREAR PANELS",dashboard_panel)
        if not dashboard_panel:
            dashboard_panel = models.DashboardPanelsGrafana(dashboard=dashboard, panel=panel)
            dashboard_panel.save()
            # print("dashboard_panel save() en el else")
            # manage_dashboard.update_dashboard(dashboard)
            # manage_dashboard.update_dashboard(dashboard, panel.panel_content)


def copy_target_to_pannel_one_to_one_target(**options):
    query = options.get("query", None)
    object_project_panel_id = options.get("object_project_panel_id", None)
    if query and object_project_panel_id:
        target = base_target.get_target_panel(query)
        panel = utils.get_or_none_panel_grafana(object_project_id=object_project_panel_id)
        if panel:
            panel.panel_content['targets'].append(target)
            panel.save()

    object_project_id_source_panel = options.get("object_project_id_source_panel", None)
    object_project_id_dest_panel = options.get("object_project_id_dest_panel", None)
    if object_project_id_source_panel and object_project_id_dest_panel:
        source_panel = utils.get_or_none_panel_grafana(object_project_id=object_project_id_source_panel)
        dest_panel = utils.get_or_none_panel_grafana(object_project_id=object_project_id_dest_panel)
        #print("add_target_to_pannel ===> panel", dest_panel)
        if object_project_id_source_panel and object_project_id_dest_panel:

            #print("source_panel.panel_content['targets']",source_panel.panel_content['targets'][0])
            #print(source_panel.panel_content)
            #print("##########################")

            dest_panel.panel_content['targets'].append(source_panel.panel_content['targets'][0])
            #print(dest_panel.panel_content)
            dest_panel.save()
