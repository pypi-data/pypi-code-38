from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool


from datetime import datetime
from .models import *


import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger
from dashboards_app.blero_utils.client_utils.client_to_server import request_plugin_render

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)



class TaskHolderClientPlugin(CMSPluginBase):
    model = TaskHolder
    name = 'Blero Task Tracker'
    render_template = "task_tracker_client/tt_base.html"


    def render(self, context, instance, placeholder):


        active_task_holder = TaskHolder.objects.get(pk=instance.pk)
        tasks=TaskDetail.objects.all().filter(model=active_task_holder)
        task_details={}

        for task in tasks:
            if task.is_complete == False:
                days_outstanding = (datetime.now().date() - task.date_created).days
                task_details[task.pk] = {'title': task.task_title, 'task_body': task.task_body,
                                         'is_complete': task.is_complete, 'days_left': days_outstanding}

        if active_task_holder.only_completed == False:

            for task in tasks:
                if task.is_complete == True:
                    days_outstanding = 0
                    task_details[task.pk] = {'title': task.task_title, 'task_body': task.task_body,
                                             'is_complete': task.is_complete, 'days_left': days_outstanding}

        logger.debug(task_details)

        only_completed=instance.only_completed



        model_name=instance._meta.model_name
        app_label=instance._meta.app_label
        context.update({
            'model_name': model_name,
            'app_label': app_label
        })

        context.update({
            'instance': instance,
            'only_completed': only_completed,
            'tasks':task_details,


        })

        server_fields = self.get_server_fields(instance)
        context.update(server_fields)

        return context

    def get_server_fields(self, instance):
        """
        API Request to get the render parameters of the plugin
        :param instance:
        :return:
        """

        try:
            server_fields = request_plugin_render(instance)

        except:
            logger.debug('error requesting to server')

        return server_fields





plugin_pool.register_plugin(TaskHolderClientPlugin)
