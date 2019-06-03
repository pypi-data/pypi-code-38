# -*- coding: utf-8 -*-
import json
import networkx as nx
from networkx import json_graph
from django.conf import settings
from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from . import managers
from .choices import STATUS, WORKFLOW_STATE


class Task(TimeStampedModel):
    """Model for Individual Tasks"""

    version = models.FloatField(validators=[MinValueValidator(0.0)])
    label = models.CharField(max_length=100, unique=True)
    previous = models.ManyToManyField('self', related_name='next_tasks', symmetrical=False, blank=True)

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self):
        return '{0}'.format(self.label)

    def get_all_previous(self):
        return " --- ".join([n.label for n in self.previous.all()])


class Workflow(TimeStampedModel):
    """Model for Workflow"""

    version = models.FloatField(validators=[MinValueValidator(0.0)])
    label = models.CharField(max_length=100)
    task = models.ManyToManyField('Task', related_name='tasks')
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Workflow')
        verbose_name_plural = _('Workflows')

    def __str__(self):
        return '{0} v{1}'.format(self.label, self.version)

    def save(self, *args, **kwargs):
        if Workflow.objects.filter(label=self.label).exists() and not self.pk and self.active:
            raise ValidationError('There can only be one Active workflow with the same label.')
        return super(Workflow, self).save(*args, **kwargs)


class WorkflowInstance(TimeStampedModel):
    """Model for an Instance of a Workflow"""

    # The workflow that was initially used to fill the graph:
    workflow = models.ForeignKey('Workflow', related_name='workflow_instances', on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(choices=WORKFLOW_STATE, default=1)

    # Mandatory fields for generic relation
    # See: https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.CASCADE)

    objects = managers.WorkflowManager()

    class Meta:
        verbose_name = _('Workflow Instance')
        verbose_name_plural = _('Workflow Instances')

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.content_type, self.object_id, self.workflow)

    def current_status(self):
        pending = getattr(STATUS, 'PENDING')
        complete = getattr(STATUS, 'COMPLETE')
        skip = getattr(STATUS, 'SKIP')

        r = self.task_instances.filter(status=pending)

        # sometimes there is no pending task due to other related workflows's status
        # we need to find the last completed, skipped task instead
        if not r:
            sorted_ids = reversed(self.topological_sort())
            for i in sorted_ids:
                x = self.task_instances.filter(
                    Q(pk=i),
                    Q(status=complete) | Q(status=skip)
                )
                if x:
                    r = x
                    break
        return r

    def all_tasks_completed(self):
        result = False
        complete = getattr(STATUS, 'COMPLETE')
        skip = getattr(STATUS, 'SKIP')
        all_task_status = list(self.task_instances.values_list('status', flat=True).distinct())

        if all_task_status == [complete, skip] \
            or all_task_status == [skip, complete] \
                or all_task_status == [complete]:
            result = True
        return result

    def all_related_workflow_instance_ids(self):
        r = []
        if self.parent:
            r.append(self.parent.id)
        if self.children.all():
            r.extend(self.children.all().values_list('id', flat=True))
        return r

    def get_graph(self):
        G = nx.DiGraph()
        task_instances = self.task_instances.all()
        for task_instance in task_instances:
            for previous in task_instance.task.previous.all():
                # find previous in task instances if exists
                if self.task_instances.filter(task__id=previous.id):
                    previous_instance = self.task_instances.filter(task__id=previous.id).first()
                    # add the previous instance and its edge to graph
                    G.add_node(task_instance.id,
                               status=task_instance.get_status_display(),
                               label=task_instance.task.label,
                               group=str(task_instance.workflow_instance),
                               )
                    G.add_node(previous_instance.id,
                               status=previous_instance.get_status_display(),
                               label=previous_instance.task.label,
                               group=str(previous_instance.workflow_instance),
                               )
                    G.add_edge(previous_instance.id, task_instance.id)
        return G

    def get_graph_json(self):
        graph = json.dumps(json_graph.node_link_data(self.get_graph()), indent=2)
        return graph

    def get_all_children(self):
        children = [self]
        try:
            child_list = self.children.all()
        except AttributeError:
            return children
        for child in child_list:
            children.extend(child.get_all_children())
        return children

    def topological_sort(self):
        G = self.get_graph()
        sorted = list(nx.topological_sort(G))
        return sorted


class TaskInstance(TimeStampedModel):
    """Model for Task Instances"""

    task = models.ForeignKey('Task', related_name='task_instances', on_delete=models.CASCADE)
    workflow_instance = models.ForeignKey('WorkflowInstance',
                                          related_name='task_instances',
                                          on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS, null=True, blank=True, default=None)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="task_instances",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    objects = managers.TaskManager()

    class Meta:
        verbose_name = _('Task Instance')
        verbose_name_plural = _('Task Instances')
        unique_together = ['task', 'workflow_instance']

    def __str__(self):
        return '{0} : {1}'.format(self.task, self.workflow_instance)

    def previous_task_instances(self):
        previous_instances = []
        wi = self.workflow_instance
        for previous in self.task.previous.all():
            # check if a task instance exists in the wf instance
            if wi.task_instances.filter(task__id=previous.id):
                pi = wi.task_instances.filter(task__id=previous.id).first()
                # add the previous instance to the list
                previous_instances.append(pi)
        return previous_instances

    def next_task_instances(self):
        next_instances = []
        wi = self.workflow_instance
        for next in self.task.next_tasks.all():
            if wi.task_instances.filter(task__id=next.id):
                pi = wi.task_instances.filter(task__id=next.id).first()
                next_instances.append(pi)
        return next_instances


class Reference(TimeStampedModel):
    """
    Model for storing references to lookup workflows based on generic
    foreign keys. Each object should have a unique workflow that it
    can point to if matched.
    """
    workflow_category = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    workflow = models.ForeignKey('Workflow', related_name='references', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Reference')
        verbose_name_plural = _('References')
        unique_together = ['content_type', 'object_id', 'workflow']

    def __str__(self):
        return '{0}-{1} {2}'.format(self.content_type, self.object_id, self.workflow)
