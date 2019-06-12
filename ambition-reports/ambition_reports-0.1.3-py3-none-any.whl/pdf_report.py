from ambition_permissions.group_names import RANDO
from ambition_rando.models import RandomizationList
from edc_registration.models import RegisteredSubject
from edc_reports.crf_pdf_report import CrfPdfReport
from edc_utils import formatted_age
from reportlab.lib.units import cm
from reportlab.platypus import Table
from textwrap import fill


class AmbitionCrfPdfReport(CrfPdfReport):

    logo_data = {
        "app_label": "ambition_edc",
        "filename": "ambition_logo.png",
        "first_page": (4.0 * cm, 0.83 * cm),
        "later_pages": (3.0 * cm, 0.625 * cm),
    }

    def __init__(self, subject_identifier=None, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = subject_identifier
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.drug_assignment = RandomizationList.objects.get(
            subject_identifier=self.subject_identifier
        ).get_drug_assignment_display()

    @property
    def age(self):
        model_obj = getattr(self, self.model_attr)
        return formatted_age(
            self.registered_subject.dob, reference_dt=model_obj.report_datetime
        )

    def draw_demographics(self, story, **kwargs):

        assignment = "*****************"
        if self.request.user.groups.filter(name=RANDO).exists():
            assignment = fill(self.drug_assignment, width=80)
        rows = [
            ["Subject:", self.subject_identifier],
            [
                "Gender/Age:",
                f"{self.registered_subject.get_gender_display()} {self.age}",
            ],
            [
                "Study site:",
                f"{self.registered_subject.site.id}: "
                f"{self.registered_subject.site.name.title()}",
            ],
            [
                "Randomization date:",
                self.registered_subject.randomization_datetime.strftime(
                    "%Y-%m-%d %H:%M"
                ),
            ],
            ["Assignment:", assignment],
        ]

        t = Table(rows, (4 * cm, 14 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        t.hAlign = "LEFT"
        story.append(t)
