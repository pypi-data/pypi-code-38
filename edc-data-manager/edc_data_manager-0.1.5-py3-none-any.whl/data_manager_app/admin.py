from django.contrib import admin
from edc_model_admin.dashboard import (
    ModelAdminCrfDashboardMixin,
    ModelAdminSubjectDashboardMixin,
)

from .admin_site import data_manager_app_admin
from .models import (
    CrfFive,
    CrfFour,
    CrfOne,
    CrfThree,
    CrfTwo,
    CrfSix,
    SubjectConsent,
    SubjectRequisition,
    SubjectVisit,
    OnSchedule,
    OffSchedule,
)


@admin.register(OnSchedule, site=data_manager_app_admin)
class OnScheduleAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    pass


@admin.register(OffSchedule, site=data_manager_app_admin)
class OffScheduleAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    pass


@admin.register(SubjectConsent, site=data_manager_app_admin)
class SubjectConsentAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    pass


@admin.register(SubjectVisit, site=data_manager_app_admin)
class SubjectVisitAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    pass


@admin.register(CrfOne, site=data_manager_app_admin)
class CrfOneAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True


@admin.register(CrfTwo, site=data_manager_app_admin)
class CrfTwoAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True


@admin.register(CrfThree, site=data_manager_app_admin)
class CrfThreeAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    pass


@admin.register(SubjectRequisition, site=data_manager_app_admin)
class SubjectRequisitionAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True


@admin.register(CrfFour, site=data_manager_app_admin)
class CrfFourAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True


@admin.register(CrfFive, site=data_manager_app_admin)
class CrfFiveAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True


@admin.register(CrfSix, site=data_manager_app_admin)
class CrfSixAdmin(ModelAdminCrfDashboardMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True
