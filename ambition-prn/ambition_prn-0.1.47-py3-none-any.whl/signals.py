from ambition_permissions.group_names import TMG
from ambition_prn.constants import DEATH_REPORT_TMG_ACTION
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import m2m_changed
from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import YES, NO
from edc_notification.models import Notification
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.subject_schedule import NotOnScheduleError

from .models import StudyTerminationConclusion


@receiver(
    post_save,
    weak=False,
    sender=StudyTerminationConclusion,
    dispatch_uid="study_termination_conclusion_on_post_save",
)
def study_termination_conclusion_on_post_save(sender, instance, raw, created, **kwargs):
    """Enroll to W10 if willing_to_complete_10w == YES.
    """
    if not raw:
        try:
            willing_to_complete_10w = instance.willing_to_complete_10w
        except AttributeError:
            pass
        else:
            _, schedule = site_visit_schedules.get_by_onschedule_model(
                "ambition_prn.onschedulew10"
            )
            if willing_to_complete_10w == YES:
                schedule.put_on_schedule(
                    subject_identifier=instance.subject_identifier,
                    onschedule_datetime=instance.report_datetime,
                )
            elif willing_to_complete_10w == NO:
                try:
                    schedule.take_off_schedule(
                        subject_identifier=instance.subject_identifier,
                        offschedule_datetime=instance.report_datetime,
                    )
                except NotOnScheduleError:
                    pass


@receiver(
    m2m_changed, weak=False, dispatch_uid="update_prn_notifications_for_tmg_group"
)
def update_prn_notifications_for_tmg_group(
    action, instance, reverse, model, pk_set, using, **kwargs
):

    try:
        instance.userprofile
    except AttributeError:
        pass
    else:
        try:
            tmg_death_notification = Notification.objects.get(
                name=DEATH_REPORT_TMG_ACTION
            )
        except ObjectDoesNotExist:
            pass
        else:
            try:
                instance.groups.get(name=TMG)
            except ObjectDoesNotExist:
                instance.userprofile.email_notifications.remove(tmg_death_notification)
            else:
                instance.userprofile.email_notifications.add(tmg_death_notification)
