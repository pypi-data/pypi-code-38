

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import *
from django.db import transaction


import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger
from dashboards_app.blero_utils.client_utils.client_to_server import request_plugin_render


cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)


@plugin_pool.register_plugin
class ShowLogClient(CMSPluginBase):

    model = LogTerminal
    name = "Blero Log Terminal "
    render_template = "log_terminal_client/display_log.html"



    def render(self, context, instance, placeholder):

        try:
            logger.info("TEST")
            get_author = context['object'].author

            get_dashboard = context['dashboard']

            file_name = 'resources/user_logs/' + str(get_author).replace(" ", "") + get_dashboard.slug + str(
                get_dashboard.id) + ".log"

            context = super(ShowLogClient, self).render(context, instance, placeholder)

            model_name = instance._meta.model_name
            app_label = instance._meta.app_label
            context.update({
                'model_name': model_name,
                'app_label': app_label,
                'instance':instance
            })

            with open(file_name, 'r') as f:
                lines = f.read().splitlines()
                if len(lines) > 0:
                    last_line = lines[-1]
                    logfile = last_line
                else:
                    logfile = 'No logs found!'

            server_fields = self.get_server_fields(instance)
            context.update(server_fields)


            context.update({
                'logfile': logfile,
                'dashboard': str(get_dashboard.slug) + str(get_dashboard.id),
                'author': str(get_author).replace(" ", ""),

                'file_name': file_name
            })
            transaction.commit()
        except Exception as e:
            logger.exception("test")

        return context


    def get_server_fields(self,instance):
        """
               API Request to get the render parameters of the plugin
               :param instance:
               :return:
               """

        try:
            server_fields = request_plugin_render(instance)

        except:
            server_fields=[]
            logger.debug('error requesting to server')

        return server_fields


