from django.contrib.admin import AdminSite


class DashboardAppAdminSite(AdminSite):
    site_header = "DashboardApp"
    site_title = "DashboardApp"
    index_title = "DashboardApp Administration"
    site_url = "/administration/"


data_manager_app_admin = DashboardAppAdminSite(name="data_manager_app_admin")
# data_manager_app_admin.disable_action("delete")
