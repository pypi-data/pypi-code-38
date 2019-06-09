from django.contrib.admin.sites import AdminSite


class EdcReferenceAdminSite(AdminSite):
    site_header = "Edc Reference"
    site_title = "Edc Reference"
    index_title = "Edc Reference"
    site_url = "/administration/"


edc_reference_admin = EdcReferenceAdminSite(name="edc_reference_admin")
edc_reference_admin.disable_action("delete_selected")
