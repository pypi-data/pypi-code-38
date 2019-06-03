from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from votebase.core.surveys.views import IndexView, SurveyCreateView,\
    SegmentCreateView, SurveyUpdateView, SurveyDeleteView, SettingsGeneralView,\
    SettingsSegmentsView, ShareView, PrintView, SettingsBrandingView,\
    SettingsDeleteSegmentView, SettingsBrandingUploadImageView, \
    SettingsBrandingDeleteImageView


urlpatterns = [
    url(_(r'create/$'), SurveyCreateView.as_view(), name='surveys_create'),
    url(_(r'create/segment/(?P<pk>[-\d]+)/$'), SegmentCreateView.as_view(), name='surveys_create_round'),
    url(_(r'settings/branding/(?P<pk>[-\d]+)/$'), SettingsBrandingView.as_view(), name='surveys_settings_branding'),
    url(_(r'settings/branding/upload-image/(?P<pk>[-\d]+)/$'), SettingsBrandingUploadImageView.as_view(), name='surveys_settings_branding_upload_image'),
    url(_(r'settings/branding/delete-image/(?P<pk>[-\d]+)/$'), SettingsBrandingDeleteImageView.as_view(), name='surveys_settings_branding_delete_image'),
    url(_(r'settings/general/(?P<pk>[-\d]+)/$'), SettingsGeneralView.as_view(), name='surveys_settings_general'),
    url(_(r'settings/segments/(?P<pk>[-\d]+)/$'), SettingsSegmentsView.as_view(), name='surveys_settings_segments'),
    url(_(r'settings/segments/(?P<pk>[-\d]+)/(?P<pk_segment>[-\d]+)/$'), SettingsSegmentsView.as_view(), name='surveys_settings_segments_update'),
    url(_(r'settings/segments/delete/(?P<pk>[-\d]+)/$'), SettingsDeleteSegmentView.as_view(), name='surveys_settings_segments_delete'),
    url(_(r'settings/basic/(?P<pk>[-\d]+)/$'), SurveyUpdateView.as_view(), name='surveys_update'),
    url(_(r'share/(?P<pk>[-\d]+)/$'), ShareView.as_view(), name='surveys_share'),
    url(_(r'share/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), ShareView.as_view(), name='surveys_share_round'),
    url(_(r'delete/(?P<pk>[-\d]+)/$'), SurveyDeleteView.as_view(), name='surveys_delete'),
    url(_(r'print/(?P<pk>[-\d]+)/$'), PrintView.as_view(), name='surveys_print'),
    url(r'$', IndexView.as_view(), name='surveys_index'),
]
