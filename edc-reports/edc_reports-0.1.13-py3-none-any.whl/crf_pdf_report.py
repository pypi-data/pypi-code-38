from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import get_static_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import TableStyle, Paragraph
from reportlab.lib.utils import ImageReader

from .report import Report
from reportlab.platypus.tables import Table
from reportlab.platypus.flowables import Spacer, KeepTogether


class CrfPdfReport(Report):

    default_page = dict(
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.5 * cm,
        pagesize=A4,
    )

    confidential = True

    logo_data = {
        "app_label": "edc_reports",
        "filename": "clinicedc_logo.jpg",
        "first_page": (0.83 * cm, 0.83 * cm),
        "later_pages": (0.625 * cm, 0.625 * cm),
    }

    model_attr = "object"

    def __init__(self, **kwargs):
        self._logo = None
        super().__init__(**kwargs)
        self.user_model_cls = get_user_model()
        self.bg_cmd = ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey)

    @property
    def logo(self):
        if not self._logo:
            path = get_static_file(
                self.logo_data["app_label"], self.logo_data["filename"]
            )
            self._logo = ImageReader(path)
        return self._logo

    @property
    def title(self):
        verbose_name = getattr(self, self.model_attr).verbose_name.upper()
        subject_identifier = getattr(self, self.model_attr).subject_identifier
        return f"{verbose_name} FOR {subject_identifier}"

    def draw_end_of_report(self, story):
        story.append(Paragraph(f"- End of report -", self.styles["line_label_center"]))

    def get_user(self, obj, field=None):
        field = field or "user_created"
        try:
            user = self.user_model_cls.objects.get(username=getattr(obj, field))
        except ObjectDoesNotExist:
            user_created = getattr(obj, field)
        else:
            user_created = f"{user.first_name} {user.last_name}"
        return user_created

    def on_first_page(self, canvas, doc):
        super().on_first_page(canvas, doc)
        width, height = A4
        canvas.drawImage(
            self.logo, 35, height - 50, *self.logo_data["first_page"], mask="auto"
        )
        if self.confidential:
            canvas.setFont("Helvetica", 10)
            canvas.drawRightString(width - 35, height - 50, "CONFIDENTIAL")

        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(width - 35, height - 40, self.title)

    def on_later_pages(self, canvas, doc):
        super().on_later_pages(canvas, doc)
        width, height = A4
        canvas.drawImage(
            self.logo, 35, height - 40, *self.logo_data["later_pages"], mask="auto"
        )
        if self.confidential:
            canvas.setFont("Helvetica", 10)
            canvas.drawRightString(width - 35, height - 45, "CONFIDENTIAL")
        if self.title:
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(width - 35, height - 35, self.title)

    def set_table_style(self, t, bg_cmd=None):
        cmds = [
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ]
        if bg_cmd:
            cmds.append(bg_cmd)
        t.setStyle(TableStyle(cmds))
        t.hAlign = "LEFT"
        return t

    def history_change_message(self, obj):
        LogEntry = django_apps.get_model("admin.logentry")
        log_entry = (
            LogEntry.objects.filter(
                action_time__gte=obj.modified, object_id=str(obj.id)
            )
            .order_by("action_time")
            .first()
        )
        try:
            return log_entry.get_change_message()
        except AttributeError:
            return "--"

    def draw_narrative(self, story, title=None, text=None):
        t = Table([[title]], (18 * cm))
        self.set_table_style(t, bg_cmd=self.bg_cmd)
        p = Paragraph(text, self.styles["line_data_large"])
        p.hAlign = "LEFT"
        story.append(KeepTogether([t, Spacer(0.1 * cm, 0.5 * cm), p]))
