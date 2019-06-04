#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views,apis

app_name = 'bee_django_course_simple'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.CourseList.as_view(), name='index'),
    # =======课程========
    url(r'^course/list$', views.CourseList.as_view(), name='course_list'),
    url(r'^course/detail/(?P<pk>[0-9]+)$', views.CourseDetail.as_view(), name='course_detail'),
    url(r'^course/add$', views.CourseCreate.as_view(), name='course_add'),
    url(r'^course/update/(?P<pk>[0-9]+)$', views.CourseUpdate.as_view(), name='course_update'),
    url(r'^course/delete/(?P<pk>[0-9]+)$', views.CourseDelete.as_view(), name='course_delete'),

    # =======课件========
    url(r'^section/list$', views.SectionList.as_view(), name='section_list'),
    url(r'^section/detail/(?P<pk>\d+)$', views.SectionDetail.as_view(), name='section_detail'),
    url(r'^section/add/(?P<course_id>[0-9]+)$', views.SectionCreate.as_view(), name='section_add'),
    url(r'^section/update/(?P<pk>[0-9]+)$', views.SectionUpdate.as_view(), name='section_update'),
    url(r'^section/delete/(?P<pk>[0-9]+)$', views.SectionDelete.as_view(), name='section_delete'),

    # =======小节========
    url(r'^part/list$', views.PartList.as_view(), name='part_list'),
    url(r'^part/detail/(?P<pk>[0-9]+)$', views.PartDetail.as_view(), name='part_detail'),
    url(r'^part/add/(?P<section_id>[0-9]+)$', views.PartCreate.as_view(), name='part_add'),
    url(r'^part/update/(?P<pk>[0-9]+)$', views.PartUpdate.as_view(), name='part_update'),
    url(r'^part/delete/(?P<pk>[0-9]+)$', views.PartDelete.as_view(), name='part_delete'),

    # =======视频========
    url(r'^uptoken$', views.uptoken, name='uptoken'),
    url(r'^parts/(?P<part_id>\d+)/add_video$', views.add_video_to_part, name='add_video_to_part'),
    url(r'^video/(?P<video_id>\d+)/edit$', views.edit_video_content, name='edit_video_content'),
    url(r'^video/(?P<video_id>\d+)/delete$', views.delete_video, name='delete_video'),
    url(r'^video/(?P<video_id>\d+)$', views.video_detail, name='video_detail'),
    url(r'^upload_image$', views.upload_image, name='upload_image'),

    # ========== 选择题 ==============
    url(r'^question/list$', views.QuestionList.as_view(), name='question_list'),
    url(r'^question/detail/(?P<pk>[0-9]+)$', views.QuestionDetail.as_view(), name='question_detail'),
    url(r'^question/record/detail/(?P<pk>[0-9]+)$', views.QuestionRecordDetail.as_view(), name='question_record_detail'),
    url(r'^question/add/(?P<part_id>[0-9]+)$', views.QuestionCreate.as_view(), name='question_add'),
    url(r'^question/update/(?P<pk>[0-9]+)$', views.QuestionUpdate.as_view(), name='question_update'),
    url(r'^question/delete/(?P<pk>[0-9]+)$', views.QuestionDelete.as_view(), name='question_delete'),
    url(r'^option/add/(?P<question_id>[0-9]+)$', views.OptionCreate.as_view(), name='option_add'),
    url(r'^option/update/(?P<pk>[0-9]+)$', views.OptionUpdate.as_view(), name='option_update'),
    url(r'^option/delete/(?P<pk>[0-9]+)$', views.OptionDelete.as_view(), name='option_delete'),


    # ========== 用户课件 ==============
    url(r'^user/course/add/(?P<user_id>[0-9]+)$', views.UserCourseCreate.as_view(), name='user_course_add'),
    url(r'^user/course/delete/(?P<pk>[0-9]+)$', views.UserCourseDelete.as_view(), name='user_course_delete'),
    url(r'^user/section/list/(?P<user_id>[0-9]+)/(?P<user_course_id>[0-9]+)$', views.UserSectionList.as_view(), name='user_section_list'),
    url(r'^user/section/detail/(?P<pk>[0-9]+)$', views.UserSectionDetail.as_view(), name='user_section_detail'),
    url(r'^user/section/update/(?P<user_section_id>[0-9]+)/(?P<type>(.)+)$', views.UserSectionUpdate.as_view(), name='user_section_update'),
    url(r'^user/part/update/(?P<user_part_id>[0-9]+)$', apis.UserPartUpdate.as_view(), name='user_part_update'),

    # ========== 用户前台 ==============
    url(r'^custom_user/section/redirect/(?P<page_type>(.)+)/(?P<user_id>[0-9]+)/(?P<section_type>[0-9]+)/$', views.CustomUserSectionRedirect.as_view(), name='custom_user_section_redirect'),
    url(r'^custom_user/section/list/(?P<section_type>[0-9]+)/(?P<user_id>[0-9]+)/(?P<user_course_id>[0-9]+)$', views.CustomUserSectionList.as_view(), name='custom_user_section_list'),
    url(r'^custom_user/section/detail/(?P<section_type>[0-9]+)/(?P<pk>[0-9]+)$', views.CustomUserSectionDetail.as_view(), name='custom_user_section_detail'),
    url(r'^custom_user/section/empty$', views.CustomUserSectionEmpty.as_view(template_name="bee_django_course_simple/section/custom_user_section_empty.html"), name='custom_user_section_empty'),
    url(r'^custom_user/part/detail/video/(?P<pk>[0-9]+)$', views.CustomUserPartDetailVideo.as_view(), name='custom_user_part_detail_video'),
    url(r'^custom_user/part/detail/question/(?P<pk>[0-9]+)$', views.CustomUserPartDetailQuestion.as_view(), name='custom_user_part_detail_question'),


    # ============ VUE JS ===============
    # url(r'^vue_user_section/(?P<user_section_id>\d+)$', apis.VueUserSection.as_view(), name='vue_user_section'),
]
