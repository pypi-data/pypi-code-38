from django.conf.urls import url

from exports.views import (
    AttendeeAccommExport, AttendeeBadgeExport, ChildCareExport, FoodExport,
    TalksExport, SpecialDietExport, BursaryExport,
)

urlpatterns = [
    url(r'^attendees/admin/export/accomm/$', AttendeeAccommExport.as_view(),
        name='attendee_admin_export_accomm'),
    url(r'^attendees/admin/export/badges/$', AttendeeBadgeExport.as_view(),
        name='attendee_admin_export_badges'),
    url(r'^attendees/admin/export/food/$', FoodExport.as_view(),
       name='attendee_admin_export_food'),
    url(r'^attendees/admin/export/special_diets/'
        r'(?P<date>[0-9-]+)/(?P<meal>[a-z]+)/$', SpecialDietExport.as_view()),
    url(r'^attendees/admin/export/child_care/$', ChildCareExport.as_view(),
        name='attendee_admin_export_childcare'),
    url(r'^attendees/admin/export/bursaries/$', BursaryExport.as_view(),
       name='attendee_admin_export_bursaries'),
    url(r'^talks/admin/export/$', TalksExport.as_view(),
        name='talks_admin_export'),
]

exports = [{'url': u.name, 'name': u.callback.view_class.name} for u in urlpatterns if u.name]
