# -*- coding: utf-8
from django.contrib import admin
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin
import json

from . import models


class NextTaskInline(admin.TabularInline):
    model = models.Task.previous.through
    fk_name = 'to_task'
    verbose_name = u"Next"
    verbose_name_plural = u"Nexts"


class TaskAdmin(admin.ModelAdmin):
    model = models.Task
    list_display = ('id', 'label', 'get_all_previous')
    inlines = [
        NextTaskInline
    ]
    filter_horizontal = ('previous',)


class WorkflowAdmin(admin.ModelAdmin):
    model = models.Workflow
    list_display = ('id', 'label', 'version')
    filter_horizontal = ('task',)


class WorkflowInstanceAdmin(VersionAdmin):
    model = models.WorkflowInstance
    list_display = ('id', 'workflow', 'content_type', 'object_id',)
    readonly_fields = (
        '_children',
        '_all_related',
        '_current_status',
        '_combined_current_status',
        '_graph_diagram',
        '_topological_sort',
        '_combined_topological_sort',
        '_combined_graph_diagram',
        '_graph_json',
        '_combined_graph_json',
    )
    raw_id_fields = ('parent',)

    class Media:
        css = {
            "all": ('css/graph.css',)
        }
        js = ('https://d3js.org/d3.v5.js',
              'js/dagre-d3.js',
              'js/graph.js',)

    def _children(self, obj):
        return obj.get_all_children()

    def _all_related(self, obj):
        return obj.all_related_workflow_instance_ids()

    def _current_status(self, obj):
        return obj.current_status()

    def _combined_current_status(self, obj):
        return self.model.objects.combined_current_status(obj)

    def _topological_sort(self, obj):
        return obj.topological_sort()

    def _combined_topological_sort(self, obj):
        return self.model.objects.combined_topological_sort(obj)

    def _graph_diagram(self, obj):
        json_string = "'" + json.dumps(obj.get_graph_json()) + "'"
        result = u'<svg class="graph1" width="1200" height="400" data=%s ></svg>' % json_string
        return mark_safe(result)

    def _graph_json(self, obj):
        json_string = obj.get_graph_json()
        result = u'<pre>%s</pre>' % json_string
        return mark_safe(result)

    def _combined_graph_diagram(self, obj):
        json_string = "'" + json.dumps(self.model.objects.get_combined_graph_json(obj)) + "'"
        result = u'<svg class="graph2" width="1200" height="500" data=%s ></svg>' % json_string
        return mark_safe(result)

    def _combined_graph_json(self, obj):
        json_string = self.model.objects.get_combined_graph_json(obj)
        result = u'<pre>%s</pre>' % json_string
        return mark_safe(result)


class TaskInstanceAdmin(VersionAdmin):
    model = models.TaskInstance
    list_display = ('id', 'task', 'workflow_instance', 'status', '_previous',)
    readonly_fields = ('_previous', '_combined_previous', '_next', '_combined_next')
    raw_id_fields = ('workflow_instance',)

    def _previous(self, obj):
        return "\n".join([str(ti) for ti in obj.previous_task_instances()])

    def _combined_previous(self, obj):
        return "\n".join([str(ti) for ti in self.model.objects.combined_previous_task_instances(obj)])

    def _next(self, obj):
        return "\n".join([str(ti) for ti in obj.next_task_instances()])

    def _combined_next(self, obj):
        return "\n".join([str(ti) for ti in self.model.objects.combined_next_task_instances(obj)])


class ReferenceAdmin(admin.ModelAdmin):
    model = models.Reference
    list_display = ('id', 'workflow_category', 'content_type', 'object_id', 'workflow')


admin.site.register(models.Reference, ReferenceAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskInstance, TaskInstanceAdmin)
admin.site.register(models.Workflow, WorkflowAdmin)
admin.site.register(models.WorkflowInstance, WorkflowInstanceAdmin)
