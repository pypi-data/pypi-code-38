from . import base_dashboard, api, models, utils
import json

def create_dashboard(title, object_organisation_project_id, organisation_id, **options):
    object_project_dashboard_id = options.get("object_project_dashboard_id", 0)
    object_project_folder_id = options.get("object_project_folder_id", 0)
    folder_id = 0
    folder = utils.get_or_none_folder_grafana(object_project_id=object_project_folder_id)
    if folder:
        folder_id = folder.folder_id
    json_dashboard = base_dashboard.get_dashboard()
    json_dashboard['title'] = title
    # dashboard['panels'] = panels
    # base['panels'] = panels
    # for panel in panels:
    #     dashboard['panels'].append(panel)
    # organisation = models.OrganisationGrafana.objects.get(object_project_id=object_organisation_project_id,
    #                                                       organisation_id=organisation_id)
    organisation = utils.get_or_none_organisation_grafana(object_project_id=object_organisation_project_id,
                                                          organisation_id=organisation_id)
    dashboard = models.DashboardGrafana(organisation=organisation, title=title,
                                        object_project_id=object_project_dashboard_id,
                                        dashboard_content=json_dashboard)
    dashboard.save()
    # print("DASHBOARD COMPLETO:   ", dashboard.dashboard_content)
    res_data = api.create_dashboard(dashboard=dashboard, folder_id=folder_id)
    if res_data:
        dashboard.dashboard_uid = res_data['uid']
        dashboard.dashboard_id = res_data['id']
        dashboard.save()
        return dashboard
    else:
        return None


# def update_dashboard(dashboard, panel):
#     # dashboard = models.DashboardGrafana.objects.get(object_project=object_project_id)
#     json_dashboard = dashboard.dashboard_content
#     json_dashboard['uid'] = dashboard.dashboard_uid
#     json_dashboard['id'] = dashboard.dashboard_id
#     # for panel in panels:
#     json_dashboard['panels'].append(panel)
#     api.update_dashboard(json_dashboard, dashboard)


def update_dashboard(dashboard_uid, **options):
    dashboard = models.DashboardGrafana.objects.get(dashboard_uid=dashboard_uid)
    # print("dashboard.title", dashboard.title)
    object_project_folder_id = options.get("object_project_folder_id", 0)
    folder_id = 0
    folder = utils.get_or_none_folder_grafana(object_project_id=object_project_folder_id)
    if folder:
        folder_id = folder.folder_id
    json_dashboard = base_dashboard.get_dashboard()
    json_dashboard['title'] = dashboard.title
    dashboard_with_rows = options.get('rows', False)
    # print("dashboard_with_rows", dashboard_with_rows)
    if dashboard_with_rows:
        print("DASHBARD CON ROWS")
        json_dashboard['panels'] = []
        row_list = list()
        rows = models.RowsDashboardGrafana.objects.filter(dashboard__dashboard_uid=dashboard_uid)
        # rows = models.PanelsByRowDashboardGrafana.objects.all()
        # print("rows", rows)
        for row in rows:
            # json_dashboard['uid'] = dashboard.dashboard_uid
            # json_dashboard['id'] = dashboard.dashboard_id
            # for panel in panels:
            json_dashboard['panels'].append(row.row_content)
            # row_list.append(row.row_content)
            # json_dashboard['rows'] = json.dumps(row_list)
    else:
        print("DASHBOARD SIN ROWS")
        # dashboard = models.DashboardGrafana.objects.get(object_project=object_project_id)
        json_dashboard['panels'] = []
        dashboard_panels = models.DashboardPanelsGrafana.objects.filter(dashboard=dashboard)
        # print("CANTIDAD DE PANELS UPDATE DASHBOARD ROWS FALSE",dashboard_panels,dashboard_panels.count())
        for obj in dashboard_panels:
            # print("panel.panel",obj.panel)
            # json_dashboard['uid'] = dashboard.dashboard_uid
            # json_dashboard['id'] = dashboard.dashboard_id
            # for panel in panels:
            json_dashboard['panels'].append(obj.panel.panel_content)
    print("json.dumps(json_dashboard)",json.dumps(json_dashboard))
    dashboard.dashboard_content = json_dashboard
    dashboard.save()
    api.update_dashboard(json_dashboard, folder_id)


def delete_dashboard(dashboard_uid):
    return api.delete_dashboard(dashboard_uid)
