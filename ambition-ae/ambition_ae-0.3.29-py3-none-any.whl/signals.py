from ambition_permissions.group_names import TMG
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch.dispatcher import receiver
from edc_constants.constants import YES, NO
from edc_notification.models import Notification
from edc_utils import get_utcnow

from .constants import AE_TMG_ACTION
from .models import AeSusar, AeInitial


@receiver(m2m_changed, weak=False, dispatch_uid="update_ae_notifications_for_tmg_group")
def update_ae_notifications_for_tmg_group(
    action, instance, reverse, model, pk_set, using, **kwargs
):

    try:
        instance.userprofile
    except AttributeError:
        pass
    else:
        try:
            tmg_ae_notification = Notification.objects.get(name=AE_TMG_ACTION)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                with transaction.atomic():
                    instance.groups.get(name=TMG)
            except ObjectDoesNotExist:
                instance.userprofile.email_notifications.remove(tmg_ae_notification)
            else:
                instance.userprofile.email_notifications.add(tmg_ae_notification)


@receiver(post_save, weak=False, dispatch_uid="update_ae_initial_for_susar")
def update_ae_initial_for_susar(sender, instance, raw, **kwargs):

    if not raw:
        if issubclass(sender, AeSusar):
            if instance.submitted_datetime:
                if instance.ae_initial.susar_reported != YES:
                    instance.ae_initial.susar_reported = YES
                    instance.ae_initial.save(update_fields=["susar_reported"])
            elif instance.ae_initial.susar_reported != NO:
                instance.ae_initial.susar_reported = NO
                instance.ae_initial.save(update_fields=["susar_reported"])


@receiver(post_save, weak=False, dispatch_uid="update_ae_initial_susar_reported")
def update_ae_initial_susar_reported(sender, instance, raw, update_fields, **kwargs):
    if not raw and not update_fields:
        if issubclass(sender, AeInitial):
            if instance.susar_reported == YES:
                try:
                    with transaction.atomic():
                        AeSusar.objects.get(ae_initial=instance)
                except ObjectDoesNotExist:
                    AeSusar.objects.create(
                        ae_initial=instance, submitted_datetime=get_utcnow()
                    )


@receiver(post_delete, weak=False, dispatch_uid="post_delete_ae_susar")
def post_delete_ae_susar(instance, **kwargs):
    if isinstance(instance, AeSusar):
        if instance.ae_initial.susar_reported != NO:
            instance.ae_initial.susar_reported = NO
            instance.ae_initial.save()
