from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.dispatch import receiver

from votebase.core.questions.models import Question, Option


@receiver(pre_save, sender=Question)
def question_pre_save(sender, instance, **kwargs):
    try:
        old = Question.objects.get(pk=instance.pk)
        remove_old_image(old, instance)
    except ObjectDoesNotExist:
        pass


@receiver(pre_save, sender=Option)
def option_pre_save(sender, instance, **kwargs):
    try:
        old = Option.objects.get(pk=instance.pk)
        remove_old_image(old, instance)
    except ObjectDoesNotExist:
        pass


def remove_old_image(old_object, instance):
    try:
        old_image = old_object.image
        new_image = instance.image.name

        if new_image != old_image and new_image != '':
            old_object.delete_image()

    except ValueError:
        pass
    except IOError:
        pass
