from django.contrib.admin import AdminSite


class DashboardAppAdminSite(AdminSite):
    site_header = "DashboardApp"
    site_title = "DashboardApp"
    index_title = "DashboardApp Administration"
    site_url = "/administration/"


dashboard_app_admin = DashboardAppAdminSite(name="dashboard_app_admin")
# dashboard_app_admin.disable_action("delete")
