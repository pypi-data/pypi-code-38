# -*- coding: utf-8
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from . import models, choices


@receiver(post_save, sender=models.WorkflowInstance)
def workflow_instance_post_save(sender, instance, created, **kwargs):
    """
    After WorkflowInstance.save is called, we look for all the related tasks in
    the workflow and make a copy of them in the TaskInstance.
    """

    pending = getattr(choices.STATUS, 'PENDING')

    if created:
        # Create an Instance of each Task using the referenced workflow
        for task in instance.workflow.task.all():
            models.TaskInstance.objects.create(task=task,
                                               workflow_instance=instance,
                                               status=None)

        if instance.parent is None:
            first_task_id = next(iter(instance.topological_sort() or []), None)
            if first_task_id:
                task = models.TaskInstance.objects.get(pk=first_task_id)
                if task.status is None:
                    task.status = pending
                    task.save()


@receiver(pre_save, sender=models.TaskInstance)
def task_instance_pre_save(sender, instance, **kwargs):
    """
    After the task is completed, it should set the status of the next
    task instances to PENDING.
    If the task instance was the last one in the workflow, it should set
    the workflow state to COMPLETE.
    """

    complete = getattr(choices.STATUS, 'COMPLETE')
    pending = getattr(choices.STATUS, 'PENDING')
    skip = getattr(choices.STATUS, 'SKIP')
    workflow_active = getattr(choices.WORKFLOW_STATE, 'ACTIVE')
    workflow_complete = getattr(choices.WORKFLOW_STATE, 'COMPLETE')

    # Check if it's an update
    if instance.pk is not None:
        old_instance = models.TaskInstance.objects.get(pk=instance.pk)

        # Only allow change to complete/pending/skip when all previous tasks are complete
        if old_instance.status is None and instance.status in (complete, pending, skip,):
            # Check if it can be completed
            if not instance.__class__.objects.combined_previous_is_complete(instance):
                raise Exception('Can only initiate a task if all previous tasks are completed')

        # If a task completion was rolled back, workflow status should change back to active
        if old_instance.status in (complete, skip) and \
                instance.status not in (complete, skip):
            # prevent roll back if next tasks are already complete
            related_next_instances = instance.__class__.objects.combined_next_task_instances(instance)
            for task in related_next_instances:
                if task.status == complete:
                    raise Exception('Cannot roll back a Task if any of the next tasks have already been completed')
            for task in related_next_instances:
                if task.status == pending:
                    task.status = None
                    task.save()

            workflow = instance.workflow_instance
            if workflow.state == workflow_complete:
                workflow.state = workflow_active
                workflow.save()


@receiver(post_save, sender=models.TaskInstance)
def task_instance_post_save(sender, created, instance, **kwargs):
    """
    After the task is completed, it should set the status of the next
    task instances to PENDING.
    If the task instance was the last one in the workflow, it should set
    the workflow state to COMPLETE.
    """

    complete = getattr(choices.STATUS, 'COMPLETE')
    skip = getattr(choices.STATUS, 'SKIP')
    pending = getattr(choices.STATUS, 'PENDING')
    workflow_complete = getattr(choices.WORKFLOW_STATE, 'COMPLETE')

    workflow = instance.workflow_instance

    if not created:
        # Status: xxx -> Complete
        if (instance.status in (complete, skip)):
            # check if all tasks are completed then change workflow state to complete
            if workflow.all_tasks_completed():
                workflow.state = workflow_complete
                workflow.save()

            combined_next_instances = instance.__class__.objects.combined_next_task_instances(instance)
            for task in combined_next_instances:
                if task.__class__.objects.combined_previous_is_complete(task) and task.status is None:
                    task.status = pending
                    task.save()
