from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.managers import (
    ActionIdentifierSiteManager,
    ActionIdentifierManager,
)
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model.models import BaseUuidModel, ReportStatusModelMixin
from edc_model.validators import datetime_not_future
from edc_model_fields.fields import OtherCharField
from edc_search.model_mixins import SearchSlugModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from ..constants import AE_TMG_ACTION
from .ae_initial import AeInitial


class AeTmg(
    ActionModelMixin,
    TrackingModelMixin,
    ReportStatusModelMixin,
    SearchSlugModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    action_name = AE_TMG_ACTION

    tracking_identifier_prefix = "AT"

    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=get_utcnow,
    )

    ae_received_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time AE form received:",
    )

    clinical_review_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time of clinical review: ",
    )

    ae_description = models.TextField(
        blank=True, null=True, verbose_name="Description of AE:"
    )

    investigator_comments = models.TextField(
        blank=True, null=True, verbose_name="Investigator comments:"
    )

    ae_classification = models.CharField(max_length=150, blank=True, null=True)

    ae_classification_other = OtherCharField(
        max_length=250, blank=True, null=True, editable=False
    )

    original_report_agreed = models.CharField(
        verbose_name="Does the TMG investigator agree with the original AE report?",
        max_length=15,
        choices=YES_NO,
        blank=False,
        null=True,
        help_text="If No, explain in the narrative below",
    )

    narrative = models.TextField(verbose_name="Narrative", blank=True, null=True)

    officials_notified = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name="Date and time regulatory authorities notified (SUSARs)",
    )

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)

    def get_action_item_reason(self):
        return self.ae_initial.ae_description

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.append("subject_identifier")
        fields.append("report_status")
        return fields

    class Meta:
        verbose_name = "AE TMG Report"
        indexes = [
            models.Index(
                fields=["subject_identifier", "action_identifier", "site", "id"]
            )
        ]
