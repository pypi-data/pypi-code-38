# -*- coding: utf-8 -*-
from django.db.models import Q, Manager
import json
import networkx as nx
from networkx import json_graph

from . import models, choices


class WorkflowManager(Manager):

    def combined_task_instances(self, obj):
        wf_instances = []

        combined_task_instances = models.TaskInstance.objects

        if obj.parent is None:
            wf_instances.extend(obj.get_all_children())
        else:
            wf_instances.extend(obj.parent.get_all_children())
        combined_task_instances = combined_task_instances.filter(workflow_instance__in=wf_instances)

        return combined_task_instances

    def combined_current_status(self, obj):

        pending = getattr(choices.STATUS, 'PENDING')
        workflow_complete = getattr(choices.WORKFLOW_STATE, 'COMPLETE')
        current_status = []
        combined_task_instances = obj.__class__.objects.combined_task_instances(obj)

        if obj.state != workflow_complete:
            current_status = combined_task_instances.filter(status=pending)

        return current_status

    def get_combined_graph(self, obj):

        G = nx.DiGraph()
        combined_task_instances = obj.__class__.objects.combined_task_instances(obj)

        for task_instance in combined_task_instances:

            previous_tasks = task_instance.task.previous.all()

            for previous in previous_tasks:
                # find previous in task instances if exists
                # if (task_instance.task.id == previous.id):
                if combined_task_instances.filter(task__id=previous.id):
                    previous_task_instances = combined_task_instances.filter(task__id=previous.id)
                    # also check to make sure the two instance workflows are directly related
                    if task_instance.workflow_instance.parent is not None:
                        task_filter = Q(workflow_instance=task_instance.workflow_instance.parent)
                        task_filter |= Q(workflow_instance=task_instance.workflow_instance)
                        previous_task_instances = previous_task_instances.filter(task_filter)

                    for pti in previous_task_instances:
                        # add the previous instance and its edge to graph
                        G.add_node(
                            task_instance.id,
                            status=task_instance.get_status_display(),
                            label=task_instance.task.label,
                            group=str(task_instance.workflow_instance),
                        )

                        G.add_node(
                            pti.id,
                            status=pti.get_status_display(),
                            label=pti.task.label,
                            group=str(pti.workflow_instance),
                        )

                        G.add_edge(pti.id, task_instance.id)
        return G

    def get_combined_graph_json(self, obj):
        G = obj.__class__.objects.get_combined_graph(obj)
        graph = json.dumps(json_graph.node_link_data(G), indent=2)
        return graph

    def combined_topological_sort(self, obj):
        G = obj.__class__.objects.get_combined_graph(obj)
        sorted = list(nx.topological_sort(G))
        return sorted


class TaskManager(Manager):

    def combined_previous_task_instances(self, obj):
        previous_instances = []
        related_wf_instance_ids = obj.workflow_instance.all_related_workflow_instance_ids()
        all_related_task_instances = models.TaskInstance.objects.filter(
            workflow_instance__id__in=related_wf_instance_ids
        )

        # Find all previous from workflows other than it's own:
        for ti in all_related_task_instances:
            # check if the task is one of previous ones:
            if ti.task in obj.task.previous.all():
                previous_i = all_related_task_instances.filter(id=ti.id).first()
                # add the previous instance to the list
                previous_instances.append(previous_i)
        # Now add previous task from it's own workflow too:
        previous_instances.extend(obj.previous_task_instances())
        return previous_instances

    def combined_next_task_instances(self, obj):
        next_instances = []
        related_wf_instance_ids = obj.workflow_instance.all_related_workflow_instance_ids()
        all_related_task_instances = models.TaskInstance.objects.filter(
            workflow_instance__id__in=related_wf_instance_ids
        )

        # Find all nexts from workflows other than it's own:
        for ti in all_related_task_instances:
            # check if the task is one of next ones:
            if ti.task in obj.task.next_tasks.all():
                next_i = all_related_task_instances.filter(id=ti.id).first()
                # add the next instance to the list
                next_instances.append(next_i)
        # Add next task from it's own workflow too:
        next_instances.extend(obj.next_task_instances())
        return next_instances

    def combined_previous_is_complete(self, obj):
        """
        Check combined previous task instances to see if all completed or skipped
        """
        result = True
        complete = getattr(choices.STATUS, 'COMPLETE')
        skip = getattr(choices.STATUS, 'SKIP')

        combined_previous = obj.__class__.objects.combined_previous_task_instances(obj)

        for task in combined_previous:
            if task.status not in (complete, skip):
                result = False

        return result
