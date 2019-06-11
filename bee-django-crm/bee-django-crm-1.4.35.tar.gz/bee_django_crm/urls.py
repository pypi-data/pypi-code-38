#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.conf.urls import include, url
from . import views

urlpatterns = [

    # ==Preuser==
    url(r'^test/$', views.test, name='test'),
    url(r'^migrate_to_fee/$', views.migrate_to_fee, name='migrate_to_fee'),
    url(r'^$', views.PreuserList.as_view(), name='index'),
    # url(r'^preuser/custom/reg/$', views.PreuserCustomReg.as_view(), name='preuser_custom_reg'),
    url(r'^preuser/list/$', views.PreuserList.as_view(), name='preuser_list'),
    url(r'^preuser/detail/(?P<pk>[0-9]+)$', views.PreuserDetail.as_view(), name='preuser_detail'),
    url(r'^preuser/add/$', views.PreuserCreate.as_view(), name='preuser_add'),
    url(r'^preuser/update/(?P<pk>[0-9]+)/$', views.update_preuser, name='preuser_update'),
    url(r'^preuser/delete/(?P<pk>[0-9]+)/$', views.PreuserDelete.as_view(), name='preuser_delete'),
    url(r'^preuser/reg/$', views.PreuserReg.as_view(), name='preuser_reg'),
    url(r'^preuser/reg/code', views.PreuserRegCode.as_view(), name='preuser_reg_code'),
    url(r'^preuser/reg_done/$', views.preuser_reg_done, name='preuser_reg_done'),
    # api
    url(r'^preuser/api/get_name/$', views.get_name_with_user, name='get_name_with_user'),

    # =====reg code =====
    url(r'^regcode/check/$', views.RegCodeCheck.as_view(), name='regcode_check'),
    # ==Source==
    url(r'^source/list/$', views.SourceList.as_view(), name='source_list'),
    url(r'^source/detail/(?P<pk>[0-9]+)/$', views.SourceDetail.as_view(), name='source_detail'),
    url(r'^source/update/(?P<pk>[0-9]+)/$', views.SourceUpdate.as_view(), name='source_update'),
    # 二维码图片地址
    url(r'^qrcode/(?P<url>(.)+)$', views.qrcode_img, name='qrcode_img'),
    url(r'^source/qrcode/(?P<qrcode_type>(.)+)/(?P<source_id>[0-9]+)/(?P<landing_id>[0-9]+)/$', views.source_qrcode,
        name='source_qrcode'),

    url(r'^source/add/$', views.SourceCreate.as_view(), name='source_add'),
    # url(r'^source/update/(?P<pk>[0-9]+)/$', views.SourceUpdate.as_view(), name='source_update'),
    # url(r'^source/delete/(?P<pk>[0-9]+)/$', views.SourceDelete.as_view(), name='source_delete'),

    # 海报
    url(r'^poster/detail/(?P<pk>[0-9]+)/$', views.PosterDetail.as_view(), name='poster_detail'),
    url(r'^poster/create/(?P<source_id>[0-9]+)/$', views.PosterCreate.as_view(), name='poster_create'),
    url(r'^poster/update/(?P<pk>[0-9]+)/$', views.PosterUpdate.as_view(), name='poster_update'),
    url(r'^poster/delete/(?P<pk>[0-9]+)/$', views.PosterDelete.as_view(), name='poster_delete'),
    # 用户海报图片地址
    url(r'^user/poster/image/(?P<poster_id>[0-9]+)/(?P<user_id>[0-9]+)/$', views.user_poster_image,
        name='user_poster_image'),

    # ==Preuser Track==
    url(r'^preuser/track/add/(?P<preuser_id>[0-9]+)/$', views.PreuserTrackCreate.as_view(), name='preuser_track_add'),

    # ==Application question==
    url(r'^application/question/list$', views.ApplicationQuestionList.as_view(), name='application_question_list'),
    url(r'^application/question/detail/(?P<pk>[0-9]+)$', views.ApplicationQuestionDetail.as_view(),
        name='application_question_detail'),
    url(r'^application/question/add/$', views.ApplicationQuestionCreate.as_view(), name='application_question_add'),
    url(r'^application/question/update/(?P<pk>[0-9]+)/$', views.ApplicationQuestionUpdate.as_view(),
        name='application_question_update'),
    url(r'^application/question/delete/(?P<pk>[0-9]+)/$', views.ApplicationQuestionDelete.as_view(),
        name='application_question_delete'),

    # ==Application option==
    url(r'^application/option/add/(?P<pk>[0-9]+)$', views.ApplicationOptionCreate.as_view(),
        name='application_option_add'),

    # ==Preuser Application==
    url(r'^preuser/application/add/(?P<preuser_id>[0-9]+)/$', views.PreuserApplicationView.as_view(),
        name='preuser_application_add'),
    url(r'^preuser/application/update_preuser/(?P<pk>[0-9]+)$', views.PreuserApplicationUpdate.as_view(),
        name='preuser_application_update_preuser'),
    url(r'^preuser/application/done/$', views.preuser_application_done, name='preuser_application_done'),

    # ==Contract==
    url(r'^contract/list/$', views.ContractList.as_view(), name='contract_list'),
    url(r'^contract/detail/(?P<pk>[0-9]+)/$', views.ContractDetail.as_view(), name='contract_detail'),
    url(r'^contract/add/$', views.ContractCreate.as_view(), name='contract_add'),
    url(r'^contract/update/(?P<pk>[0-9]+)/$', views.ContractUpdate.as_view(), name='contract_update'),
    url(r'^contract/update/agreement/(?P<pk>[0-9]+)/$', views.ContractUpdateAgreement.as_view(), name='contract_update_agreement'),
    url(r'^contract/delete/(?P<pk>[0-9]+)/$', views.ContractDelete.as_view(), name='contract_delete'),

    # ==Preuser Contract==
    url(r'^preuser/contract/list/(?P<preuser_id>[0-9]+)$', views.PreuserContractList.as_view(),
        name='preuser_contract_list'),
    # 所有学生的合同列表
    # url(r'^preuser/contract/list/$', views.PreuserAllContractList.as_view(),
    #     name='preuser_all_contract_list'),
    url(r'^preuser/contract/detail/(?P<pk>[0-9]+)$', views.PreuserContractDetail.as_view(),
        name='preuser_contract_detail'),
    url(r'^preuser/contract/agreement/(?P<preuser_contract_id>[0-9]+)$', views.PreuserContractAgreement.as_view(),
        name='preuser_contract_agreement'),
    url(r'^preuser/contract/add/(?P<preuser_id>[0-9]+)$', views.PreuserContractCreate.as_view(),
        name='preuser_contract_add'),
    url(r'^preuser/contract/update/(?P<pk>[0-9]+)$', views.PreuserContractUpdate.as_view(),
        name='preuser_contract_update'),

    url(r'^preuser/contract/delete/(?P<pk>[0-9]+)/$', views.PreuserContractDelete.as_view(),
        name='preuser_contract_delete'),

    # 缴费
    url(r'^preuser/fee/list/(?P<preuser_id>[0-9]+)$', views.PreuserFeeList.as_view(),
        name='preuser_fee_list'),
    url(r'^preuser/fee/detail/(?P<pk>[0-9]+)$', views.PreuserFeeDetail.as_view(), name='preuser_fee_detail'),
    url(r'^preuser/fee/add/(?P<preuser_contract_id>[0-9]+)$', views.PreuserFeeCreate.as_view(),
        name='preuser_fee_add'),
    url(r'^preuser/fee/update/check/(?P<pk>[0-9]+)$', views.PreuserFeeUpdateCheck.as_view(),
        name='preuser_fee_update_check'),
    url(r'^preuser/fee/delete/(?P<pk>[0-9]+)/$', views.PreuserFeeDelete.as_view(),
        name='preuser_fee_delete'),
]
