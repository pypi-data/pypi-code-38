#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_course'

urlpatterns = [
    url(r'^$', views.CourseRedirectView.as_view(), name='index'),
    url(r'^test$', views.test, name='test'),
    # 偏好设置
    url(r'^preference$', views.set_preference, name='preference'),

    # =======课程========
    url(r'^courseList$', views.CourseList.as_view(), name='course_list'),
    url(r'^course/detail/(?P<pk>[0-9]+)$', views.CourseDetail.as_view(), name='course_detail'),
    url(r'^course/add/$', views.CourseCreate.as_view(), name='course_add'),
    url(r'^course/update/(?P<pk>[0-9]+)/$', views.CourseUpdate.as_view(), name='course_update'),
    url(r'^course/delete/(?P<pk>[0-9]+)/$', views.CourseDelete.as_view(), name='course_delete'),

    # =======课件========
    url(r'^sectionList$', views.SectionList.as_view(), name='section_list'),
    url(r'^section/detail/(?P<pk>[0-9]+)$', views.SectionDetail.as_view(), name='section_detail'),
    url(r'^section/add/$', views.SectionCreate.as_view(), name='section_add'),
    url(r'^section/update/(?P<pk>[0-9]+)/$', views.SectionUpdate.as_view(), name='section_update'),
    url(r'^section/delete/(?P<pk>[0-9]+)/$', views.SectionDelete.as_view(), name='section_delete'),

    # ===== 课程课件======
    url(r'^course/section/add/(?P<course_id>[0-9]+)/$', views.CourseSectionMidCreate.as_view(),
        name='course_section_mid_add'),
    # 修改课程课件mid的字段
    url(r'^course/section/update/(?P<csm_id>\d+)$', views.update_coursesectionmid, name='update_coursesectionmid'),
    # 图片上传
    url(r'^upload_image$', views.upload_image, name='upload_image'),
    # 给课件添加视频
    url(r'^create_section_video/(?P<section_id>\d+)$', views.create_section_video, name='create_section_video'),
    # 删除课件的视频
    url(r'^remove_section_video/(?P<section_video_id>\d+)$', views.remove_section_video,
        name='remove_section_video'),
    # 调整课件视频的排序
    url(r'^section_video/(?P<section_video_id>\d+)/order$', views.update_section_video_order,
        name='update_section_video_order'),
    # 删除课程中的课件
    url(r'delete_courseectionmid/(?P<csm_id>\d+)$', views.delete_courseectionmid, name='delete_courseectionmid'),

    # ========== 课件测试问卷==============
    url(r'^course/section/question/(?P<section_id>[0-9]+)/$', views.SectionQuestionView.as_view(),
        name='section_question'),
    url(r'^course/section/question/list_json/(?P<section_id>[0-9]+)/$', views.SectionQuestionListJson.as_view(),
        name='section_question_list_json'),
    url(r'^course/section/question/add/$', views.SectionQuestionCreate.as_view(), name='section_question_add'),
    url(r'^course/section/question/save/(?P<question_id>[0-9]+)/$', views.SectionQuestionSave.as_view(),
        name='save_section_question'),
    url(r'^course/section/question/delete/(?P<question_id>[0-9]+)/$', views.SectionQuestionDelete.as_view(),
        name='section_question_delete'),
    url(r'^course/section/option/add/(?P<question_id>[0-9]+)/$', views.SectionQuestionOptionCreate.as_view(),
        name='question_option_add'),
    url(r'^course/section/option/delete/(?P<option_id>[0-9]+)/$', views.SectionQuestionOptionDelete.as_view(),
        name='question_option_delete'),
    url(r'^course/section/question/answer/(?P<user_section_id>[0-9]+)/$', views.SectionQuestionAnswer.as_view(),
        name='question_answer'),
    url(r'^user/question/answer/record/(?P<user_section_id>[0-9]+)/$', views.UserQuestionAnswerRecordList.as_view(),
        name='user_question_answer'),
    url(r'^user/question/answer/record/detail/(?P<pk>[0-9]+)/$', views.UserQuestionAnswerRecordDetail.as_view(),
        name='user_question_answer_detail'),

    # ===== 视频 ======
    url(r'^video/list/$', views.VideoList.as_view(), name='video_list'),
    url(r'^video/detail/(?P<pk>[0-9]+)/$', views.VideoDetail.as_view(), name='video_detail'),
    url(r'^video/update/(?P<pk>[0-9]+)/$', views.VideoUpdate.as_view(), name='video_update'),
    url(r'^video/upload/$', views.VideoUpload.as_view(), name='video_upload'),
    url(r'^video/upload_to_qiniu$', views.VideoUploadToQiniu.as_view(), name='video_upload_to_qiniu'),
    # 1.选取文件后,获取video信息
    url(r'^cc/video/info/add/$', views.CCVideoInfoCreate.as_view(), name='cc_video_info_add'),
    # 2.上传完成后，记录video信息到数据库
    url(r'^cc/video/upload/done/$', views.cc_video_upload_done, name='cc_video_upload_done'),
    # 3.转码完成后cc的回调
    url(r'^cc/video/callback/', views.cc_video_callback, name='cc_video_callback'),
    # url(r'^vodio/play/$', views.play_video, name='play_video'),

    # 获取七牛云上传token
    url(r'^uptoken$', views.uptoken, name='uptoken'),
    url(r'^add_qiniu_video_to_video$', views.add_qiniu_video_to_video, name='add_qiniu_video_to_video'),

    # ===== 录播 ======
    url(r'^live/list/(?P<user_id>[0-9]+)/$', views.LiveList.as_view(), name='live_list'),
    # url(r'^live/list/(?P<user_id>[0-9]+)/$', views.UserLiveList.as_view(), name='user_live_list'),
    # 查看录播视频页
    url(r'^live/video/(?P<live_video_id>(.)+)/$', views.live_video_detail, name='live_video_detail'),
    # 用户查看录播视频
    url(r'^user/live/(?P<live_video_id>(.)+)/$', views.user_live_video_detail, name='user_live_video_detail'),
    # 编辑录播评论
    url(r'^user_live/comment/(?P<user_live_comment_id>\d+)/edit$', views.edit_user_live_comment,
        name='edit_user_live_comment'),
    # 删除录播评论
    url(r'^user_live/comment/(?P<user_live_comment_id>\d+)/delete$', views.delete_user_live_comment,
        name='delete_user_live_comment'),
    # 直播/录播 结束回调 2
    url(r'^live_end_callback$', views.cc_live_end_callback, name='user_live_end_callback'),
    # 直播 完成回调 103
    url(r'^live_finished_callback$', views.cc_live_finished_callback, name='user_live_finished_callback'),
    url(r'^live_play_logs', views.LivePlayLogs.as_view(), name='play_logs'),

    # 删除直播
    url(r'^delete_user_live/(?P<user_live_id>\d+)$', views.delete_user_live, name='delete_user_live'),

    # 用户课程表
    url(r'^user_course/(?P<user_id>\d+)$', views.UserCourseSectionList.as_view(), name='user_course'),
    # 用户学习的某一课程详情
    url(r'^user_course_detail/(?P<user_course_id>\d+)$', views.UserCourseDetail.as_view(),
        name='user_course_detail'),
    # 管理用户某一课程的列表
    url(r'^manage_user_course_section_list/(?P<user_course_id>\d+)$', views.manage_user_course_section_list,
        name='manage_user_course_section_list'),
    # 用户查看课程
    url(r'^view_courses$', views.view_courses, name='view_courses'),
    # 用户查看课程章节
    url(r'^user_course_section_detail/(?P<pk>\d+)$', views.UserCourseSectionDetail.as_view(),
        name='user_course_section_detail'),

    # 查看用户列表
    url(r'^users$', views.user_list, name='users'),
    # 管理查看用户课程
    url(r'^manage_user_course/(?P<user_id>\d+)$', views.manage_user_course, name='manage_user_course'),
    # 给用户分配课程
    url(r'^choose_user_course/(?P<user_id>\d+)$', views.choose_user_course, name='choose_user_course'),
    # 删除用户课程
    url(r'^delete_user_course/(?P<user_course_id>\d+)$', views.delete_user_course, name='delete_user_course'),
    # 查看用户待评分作业列表
    url(r'^manage_assignments$', views.manage_user_assignments, name='manage_user_assignments'),
    # 提醒助教
    url(r'^user_(?P<user_id>\d+)/notify_mentor$', views.notify_mentor, name='notify_mentor'),
    # 申请客服
    url(r'^user_(?P<user_id>\d+)/notify_agent$', views.notify_agent, name='notify_agent'),
    # 查看指定用户所有作业
    url(r'^manage/user/(?P<user_id>\d+)/assignments$', views.manage_user_assignment_list,
        name='manage_user_assignment_list'),

    # 用户写作业的页面
    url(r'^user_assignment/(?P<ucs_id>\d+)$', views.user_assignment, name='user_assignment'),

    # 助教查看用户作业
    url(r'^manage_user_assignment/(?P<ucs_id>\d+)$', views.manage_user_assignment, name='manage_user_assignment'),

    # 用户提交作业图片
    url(r'^user_assignment_image_upload/(?P<ucs_id>\d+)$', views.user_assignment_image_upload,
        name='user_assignment_image_upload'),
    # 用户保存作业
    url(r'^save_user_assignment/(?P<ucs_id>\d+)$', views.save_user_assignment, name='save_user_assignment'),
    # 用户提交作业
    url(r'^submit_user_assignment/(?P<ucs_id>\d+)$', views.submit_user_assignment, name='submit_user_assignment'),

    # 给作业评分
    url(r'^review_user_assignment/(?P<ucs_id>\d+)/(?P<level>\d+)$', views.review_user_assignment,
        name='review_user_assignment'),

    # 手动开启课件
    url(r'^manage_open_user_course_section/(?P<ucs_id>\d+)$', views.open_user_course_section,
        name='open_user_course_section'),
    # 手动通过课件
    url(r'^manage_pass_user_course_section/(?P<ucs_id>\d+)$', views.pass_user_course_section,
        name='pass_user_course_section'),
    # 手动关闭课件
    url(r'^manage_close_user_course_section/(?P<ucs_id>\d+)$', views.close_user_course_section,
        name='close_user_course_section'),

    # 用户通过答题状态记录
    url(r'^ucs_question_passed/(?P<ucs_id>\d+)$',
        views.ucs_question_passed, name='ucs_question_passed'),

    # 微信小程序接口
    url(r'weixin_user_course_index$', views.weixin_user_course_index, name='weixin_user_course_index'),
    url(r'weixin_ucs_detail/(?P<ucs_id>\d+)$', views.weixin_ucs_detail, name='weixin_ucs_detail'),

    url(r'test_video$', views.test_video, name='test_video'),
    url(r'uptoken$', views.uptoken, name='uptoken'),
]
