from ambition_prn.admin_site import ambition_prn_admin
from ambition_prn.models import DeathReport
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_action_item import action_fieldset_tuple
from edc_constants.constants import OTHER, YES, DEAD
from edc_model_admin import audit_fieldset_tuple, SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_utils import convert_php_dateformat

from ..admin_site import ambition_ae_admin
from ..forms import AeInitialForm
from ..models import AeInitial, AeFollowup


@admin.register(AeInitial, site=ambition_ae_admin)
class AeInitialAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    form = AeInitialForm
    email_contact = settings.EMAIL_CONTACTS.get("ae_reports")
    additional_instructions = mark_safe(
        "Complete the initial AE report and forward to the TMG. "
        f'Email to <a href="mailto:{email_contact}">{email_contact}</a>'
    )

    fieldsets = (
        (
            "Part 1:",
            {
                "fields": (
                    "subject_identifier",
                    "ae_classification",
                    "ae_classification_other",
                    "report_datetime",
                    "ae_description",
                    "ae_awareness_date",
                    "ae_start_date",
                    "ae_grade",
                    "ae_study_relation_possibility",
                )
            },
        ),
        (
            "Part 2: Relationship to study drug",
            {
                "fields": (
                    "fluconazole_relation",
                    "flucytosine_relation",
                    "amphotericin_relation",
                )
            },
        ),
        (
            "Part 3:",
            {
                "fields": (
                    "ae_cause",
                    "ae_cause_other",
                    "ae_treatment",
                    "ae_cm_recurrence",
                )
            },
        ),
        ("Part 4:", {"fields": ("sae", "sae_reason", "susar", "susar_reported")}),
        action_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "ae_cause": admin.VERTICAL,
        "ae_classification": admin.VERTICAL,
        "ae_cm_recurrence": admin.VERTICAL,
        "ae_grade": admin.VERTICAL,
        "ae_study_relation_possibility": admin.VERTICAL,
        # 'ambisome_relation': admin.VERTICAL,
        # 'amphotericin_b_relation': admin.VERTICAL,
        "amphotericin_relation": admin.VERTICAL,
        "fluconazole_relation": admin.VERTICAL,
        "flucytosine_relation": admin.VERTICAL,
        "sae": admin.VERTICAL,
        "sae_reason": admin.VERTICAL,
        "susar": admin.VERTICAL,
        "susar_reported": admin.VERTICAL,
    }

    ordering = ["-tracking_identifier"]

    list_display = [
        "identifier",
        "dashboard",
        "follow_up_reports",
        "description",
        "if_sae_reason",
        "user",
    ]

    list_filter = [
        "ae_awareness_date",
        "ae_grade",
        "ae_classification",
        "sae",
        "sae_reason",
        "susar",
        "susar_reported",
    ]

    search_fields = ["subject_identifier", "action_identifier", "tracking_identifier"]

    def user(self, obj):
        """Returns formatted user names and creation/modification dates.
        """
        return mark_safe(
            "<BR>".join(
                [
                    obj.user_created,
                    obj.created.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    ),
                    obj.user_modified,
                    obj.modified.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    ),
                ]
            )
        )

    def if_sae_reason(self, obj):
        """Returns the SAE reason.

        If DEATH, adds link to the death report.
        """
        if obj.sae_reason == DEAD:
            try:
                death_report = DeathReport.objects.get(
                    subject_identifier=obj.subject_identifier
                )
            except ObjectDoesNotExist:
                link = '<font color="red">Death report pending</font>'
            else:
                url_name = "ambition_prn_deathreport"
                namespace = ambition_prn_admin.name
                url = reverse(f"{namespace}:{url_name}_changelist")
                link = (
                    f'See report <a title="go to Death report"'
                    f'href="{url}?q={death_report.subject_identifier}">'
                    f"<span nowrap>{death_report.identifier}</span></a>"
                )
            return mark_safe(f"{obj.get_sae_reason_display()}.<BR>{link}.")
        return obj.get_sae_reason_display()

    if_sae_reason.short_description = "If SAE, reason"

    def description(self, obj):
        """Returns a formatted comprehensive description of the SAE
        combining multiple fields.
        """
        ae_awareness_date = obj.ae_awareness_date.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )
        classification = (
            f"Other: {obj.ae_classification_other}"
            if obj.ae_classification == OTHER
            else obj.get_ae_classification_display()
        )
        susar_reported = (
            "Reported"
            if obj.susar_reported == YES
            else '<font color="red">Not reported</font>'
        )
        susar = (
            f"Yes. {susar_reported}" if obj.susar == YES else obj.get_susar_display()
        )
        return mark_safe(
            ".<BR>".join(
                [
                    f"<b>Site aware:</b> {ae_awareness_date}",
                    f"<b>Grade:</b> {obj.get_ae_grade_display()}",
                    f"<b>Classification:</b> {classification}",
                    f"<b>SAE?:</b> {obj.get_sae_display()}",
                    f"<b>SUSAR?:</b> {susar}",
                    "<b>Description:</b>",
                    obj.ae_description,
                ]
            )
        )

    def follow_up_reports(self, obj):
        """Returns a formatted list of links to AE Follow up reports.
        """
        followups = []
        for ae_followup in AeFollowup.objects.filter(
            related_action_item=obj.action_item
        ):
            url_name = "_".join(ae_followup._meta.label_lower.split("."))
            namespace = ambition_ae_admin.name
            url = reverse(f"{namespace}:{url_name}_changelist")
            report_datetime = ae_followup.report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            followups.append(
                f'<a title="go to AE follow up report for '
                f'{report_datetime}" '
                f'href="{url}?q={obj.action_identifier}">'
                f"<span nowrap>{ae_followup.identifier}</span></a>"
            )
        if followups:
            return mark_safe("<BR>".join(followups))
        return None
