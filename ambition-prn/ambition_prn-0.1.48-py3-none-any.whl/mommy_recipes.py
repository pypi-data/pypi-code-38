from edc_constants.constants import YES, NO
from faker import Faker
from model_mommy.recipe import Recipe

from .constants import CRYTOCOCCAL_MENINGITIS
from .models import (
    DeathReport,
    StudyTerminationConclusion,
    StudyTerminationConclusionW10,
)
from .models import ProtocolDeviationViolation, DeathReportTmg

fake = Faker()

deathreport = Recipe(
    DeathReport,
    study_day=1,
    death_as_inpatient=YES,
    cause_of_death=CRYTOCOCCAL_MENINGITIS,
    cause_of_death_other=None,
    action_identifier=None,
    tracking_identifier=None,
)
#     tb_site='meningitis',
#     narrative=(
#         'adverse event resulted in death due to cryptococcal meningitis'))

studyterminationconclusion = Recipe(
    StudyTerminationConclusion,
    action_identifier=None,
    tracking_identifier=None,
    protocol_exclusion_criterion=NO,
)

studyterminationconclusionw10 = Recipe(
    StudyTerminationConclusionW10, action_identifier=None, tracking_identifier=None
)

protocoldeviationviolation = Recipe(
    ProtocolDeviationViolation, action_identifier=None, tracking_identifier=None
)

deathreporttmg = Recipe(
    DeathReportTmg,
    action_identifier=None,
    cause_of_death=CRYTOCOCCAL_MENINGITIS,
    cause_of_death_agreed=YES,
    tracking_identifier=None,
)
