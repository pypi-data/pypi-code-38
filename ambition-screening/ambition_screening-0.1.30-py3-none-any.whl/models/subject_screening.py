import re

from dateutil.relativedelta import relativedelta
from django.db import models
from edc_constants.choices import (
    GENDER,
    YES_NO,
    YES_NO_NA,
    NORMAL_ABNORMAL,
    PREG_YES_NO_NA,
)
from edc_constants.constants import UUID_PATTERN
from edc_identifier import is_subject_identifier_or_raise
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_reportable import IU_LITER, TEN_X_9_PER_LITER
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow
from uuid import uuid4

from ..subject_screening_eligibility import SubjectScreeningEligibility
from ..identifiers import ScreeningIdentifier


class SubjectScreeningManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, screening_identifier):
        return self.get(screening_identifier=screening_identifier)


class SubjectIdentifierModelMixin(
    NonUniqueSubjectIdentifierModelMixin, SearchSlugModelMixin, models.Model
):
    def update_subject_identifier_on_save(self):
        """Overridden to not create a new study-allocated subject identifier on save.

        Instead just set subject_identifier to a UUID for uniqueness
        from subject_identifier_as_pk.

        The subject_identifier will be set upon consent.
        """
        if not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk.hex
        else:
            # validate it is either a valid subject identifier or a
            # uuid/uuid.hex
            if not re.match(UUID_PATTERN, self.subject_identifier):
                is_subject_identifier_or_raise(
                    self.subject_identifier, reference_obj=self
                )
        return self.subject_identifier

    def make_new_identifier(self):
        return self.subject_identifier_as_pk.hex

    class Meta:
        abstract = True


class SubjectScreening(SubjectIdentifierModelMixin, SiteModelMixin, BaseUuidModel):

    eligibility_cls = SubjectScreeningEligibility

    identifier_cls = ScreeningIdentifier

    reference = models.UUIDField(
        verbose_name="Reference", unique=True, default=uuid4, editable=False
    )

    screening_identifier = models.CharField(
        verbose_name="Screening ID",
        max_length=50,
        blank=True,
        unique=True,
        editable=False,
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )

    gender = models.CharField(choices=GENDER, max_length=10)

    age_in_years = models.IntegerField()

    meningitis_dx = models.CharField(
        verbose_name="First episode cryptococcal meningitis diagnosed by "
        "either: CSF India Ink or CSF cryptococcal antigen "
        "(CRAG)",
        choices=YES_NO,
        max_length=5,
    )

    will_hiv_test = models.CharField(
        verbose_name="Known HIV positive/willing to consent to an HIV test.",
        max_length=5,
        choices=YES_NO,
    )

    mental_status = models.CharField(
        verbose_name="Mental status", max_length=10, choices=NORMAL_ABNORMAL
    )

    consent_ability = models.CharField(
        verbose_name="Participant or legal guardian/representative able and "
        "willing to give informed consent.",
        max_length=5,
        choices=YES_NO,
    )

    pregnancy = models.CharField(
        verbose_name="Is the patient pregnant?", max_length=15, choices=PREG_YES_NO_NA
    )

    preg_test_date = models.DateTimeField(
        verbose_name="Pregnancy test (Urine or serum βhCG) date", blank=True, null=True
    )

    breast_feeding = models.CharField(
        verbose_name="Is the patient breasfeeding?", max_length=15, choices=YES_NO_NA
    )

    previous_drug_reaction = models.CharField(
        verbose_name=(
            "Previous Adverse Drug Reaction (ADR) to study drug "
            "(e.g. rash, drug induced blood abnormality)"
        ),
        max_length=5,
        choices=YES_NO,
    )

    contraindicated_meds = models.CharField(
        verbose_name=(
            "Taking concomitant medication that is contra-indicated "
            "with any study drug"
        ),
        max_length=5,
        choices=YES_NO,
        help_text="Contraindicated Meds: Cisapride, Pimozide,"
        "Terfenadine, Quinidine, Astemizole, Erythromycin",
    )

    received_amphotericin = models.CharField(
        verbose_name=(
            "Has received >48 hours of Amphotericin B "
            "(>=0.7mg/kg/day) prior to screening."
        ),
        max_length=5,
        choices=YES_NO,
    )

    received_fluconazole = models.CharField(
        verbose_name=(
            "Has received >48 hours of fluconazole treatment (>= "
            "800mg/day) prior to screening."
        ),
        max_length=5,
        choices=YES_NO,
    )

    alt = models.IntegerField(
        verbose_name="ALT result",
        null=True,
        blank=True,
        help_text=(
            "Leave blank if unknown. Units: 'IU/mL'. " f"Ineligible if > 200 {IU_LITER}"
        ),
    )

    neutrophil = models.DecimalField(
        verbose_name="Neutrophil result",
        decimal_places=2,
        max_digits=4,
        null=True,
        blank=True,
        help_text=(
            f"Leave blank if unknown. Units: '{TEN_X_9_PER_LITER}'. "
            f"Ineligible if < 0.5  {TEN_X_9_PER_LITER}"
        ),
    )

    platelets = models.IntegerField(
        verbose_name="Platelets result",
        null=True,
        blank=True,
        help_text=(
            f"Leave blank if unknown. Units: '{TEN_X_9_PER_LITER}'. "
            f"Ineligible if < 50 {TEN_X_9_PER_LITER}"
        ),
    )

    eligible = models.BooleanField(default=False, editable=False)

    reasons_ineligible = models.TextField(
        verbose_name="Reason not eligible", max_length=150, null=True, editable=False
    )

    consented = models.BooleanField(default=False, editable=False)

    unsuitable_for_study = models.CharField(
        verbose_name=(
            "Is there any other reason the patient is "
            "deemed to not be suitable for the study?"
        ),
        max_length=5,
        choices=YES_NO,
        help_text="If YES, patient NOT eligible, please give reason below.",
    )

    reasons_unsuitable = models.TextField(
        verbose_name="Reason not eligible", max_length=150, null=True, blank=True
    )

    on_site = CurrentSiteManager()

    objects = SubjectScreeningManager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.screening_identifier} {self.gender} {self.age_in_years}"

    def save(self, *args, **kwargs):
        eligibility_obj = self.eligibility_cls(model_obj=self, allow_none=True)
        self.eligible = eligibility_obj.eligible
        if not self.eligible:
            reasons_ineligible = [
                v for v in eligibility_obj.reasons_ineligible.values() if v
            ]
            reasons_ineligible.sort()
            self.reasons_ineligible = "|".join(reasons_ineligible)
        else:
            self.reasons_ineligible = None
        if not self.id:
            self.screening_identifier = self.identifier_cls().identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.screening_identifier,)

    def get_search_slug_fields(self):
        return ["screening_identifier", "subject_identifier", "reference"]

    @property
    def estimated_dob(self):
        return get_utcnow().date() - relativedelta(years=self.age_in_years)
