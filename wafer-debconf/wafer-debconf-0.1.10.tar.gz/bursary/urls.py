from django.conf.urls import url

from bursary.views import (
    BursaryMassUpdate, BursaryRefereeAdd, BursaryRefereeExport,
    BursaryRequestExport, BursaryUpdate,
)

urlpatterns = [
    url(r'^admin/export/requests/$', BursaryRequestExport.as_view(),
        name='bursaries_admin_export_requests'),
    url(r'^admin/export/referees/$', BursaryRefereeExport.as_view(),
        name='bursaries_admin_export_referees'),
    url(r'^admin/add_referees/$', BursaryRefereeAdd.as_view(),
        name='bursaries_admin_add_referees'),
    url(r'^admin/update_requests/$', BursaryMassUpdate.as_view(),
        name='bursaries_admin_update_requests'),
    url(r'^$', BursaryUpdate.as_view(), name='bursary_update'),
]
