from ambition_prn.action_items import DEATH_REPORT_TMG_ACTION
from ambition_prn.models import DeathReportTmg
from django.core.exceptions import ObjectDoesNotExist
from edc_action_item.models import ActionItem
from edc_model_wrapper import ModelWrapper

from .death_report_tmg_model_wrapper import DeathReportTmgModelWrapper


class DeathReportModelWrapper(ModelWrapper):
    next_url_name = "tmg_death_listboard_url"
    model = "ambition_prn.deathreport"
    next_url_attrs = ["subject_identifier"]

    @property
    def pk(self):
        return str(self.object.pk)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def tmg_death_reports(self):
        objs = []
        for action_item in ActionItem.objects.filter(
            related_action_item=self.object.action_item,
            action_type__name=DEATH_REPORT_TMG_ACTION,
        ):
            try:
                objs.append(
                    DeathReportTmgModelWrapper(
                        model_obj=DeathReportTmg.objects.get(
                            action_identifier=action_item.action_identifier
                        )
                    )
                )
            except ObjectDoesNotExist:
                objs.append(
                    DeathReportTmgModelWrapper(
                        model_obj=DeathReportTmg(
                            death_report=self.object,
                            subject_identifier=self.object.subject_identifier,
                            action_identifier=action_item.action_identifier,
                            parent_action_item=action_item.parent_action_item,
                            related_action_item=action_item.related_action_item,
                        )
                    )
                )
        return objs
