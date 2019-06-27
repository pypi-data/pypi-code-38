from ambition_permissions import TMG
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from edc_action_item import action_fieldset_tuple
from edc_model_admin import audit_fieldset_tuple, SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_utils import convert_php_dateformat

from ..admin_site import ambition_ae_admin
from ..choices import AE_CLASSIFICATION
from ..forms import AeTmgForm
from ..models import AeTmg, AeInitial
from .modeladmin_mixins import NonAeInitialModelAdminMixin


@admin.register(AeTmg, site=ambition_ae_admin)
class AeTmgAdmin(
    ModelAdminSubjectDashboardMixin, NonAeInitialModelAdminMixin, SimpleHistoryAdmin
):

    form = AeTmgForm

    additional_instructions = "For completion by TMG Investigators Only"

    list_display = [
        "subject_identifier",
        "dashboard",
        "status",
        "ae_initial",
        "report_datetime",
        "officials_notified",
        "report_closed_datetime",
    ]

    list_filter = ("report_datetime", "report_status")

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "ae_initial__action_identifier",
        "ae_initial__tracking_identifier",
        "tracking_identifier",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "ae_initial",
                    "report_datetime",
                    "ae_received_datetime",
                    "clinical_review_datetime",
                    "ae_description",
                    "investigator_comments",
                    "ae_classification",
                    # 'ae_classification_other',
                    "original_report_agreed",
                    "narrative",
                    "officials_notified",
                    "report_status",
                    "report_closed_datetime",
                )
            },
        ),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "report_status": admin.VERTICAL,
        "original_report_agreed": admin.VERTICAL,
    }

    def status(self, obj=None):
        return obj.report_status.title()

    def get_queryset(self, request):
        """Returns for the current user only if in the TMG group.
        """
        try:
            request.user.groups.get(name=TMG)
        except ObjectDoesNotExist:
            return super().get_queryset(request)
        return super().get_queryset(request).filter(user_created=request.user)

    def get_changeform_initial_data(self, request):
        """Updates initial data with the description of the
        original AE.
        """
        initial = super().get_changeform_initial_data(request)
        try:
            ae_initial = AeInitial.objects.get(pk=request.GET.get("ae_initial"))
        except ObjectDoesNotExist:
            pass
        else:
            ae_classification = [
                y for x, y in AE_CLASSIFICATION if x == ae_initial.ae_classification
            ]
            ae_classification.append(ae_initial.ae_classification_other or "")
            ae_classification = " ".join(ae_classification).rstrip()
            report_datetime = ae_initial.report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            initial.update(
                ae_classification=ae_classification,
                ae_description=(
                    f"{ae_initial.ae_description} (reported: {report_datetime})"
                ),
            )
        return initial
