# -*- coding: utf-8 -*-

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import *
from dashboards_app.blero_utils.client_utils.client_to_server import request_plugin_render



import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)

class BleroContainerClientPlugin(CMSPluginBase):

    model = BleroContainer
    name = 'Blero Container'
    render_template = "blero_container_client/base.html"



    def render(self, context, instance, placeholder):


        model_name=instance._meta.model_name
        app_label=instance._meta.app_label

        context.update({
            'instance': instance,
            'model_name':model_name,
            'app_label':app_label


        })


        server_fields=self.get_server_fields(instance)
        context.update(server_fields)

        return context


    def get_server_fields(self,instance):
        """
        API Request to get the render parameters of the plugin
        :param instance:
        :return:
        """

        try:
            server_fields=request_plugin_render(instance)

        except:
            logger.debug('error requesting to server')

        return server_fields







plugin_pool.register_plugin(BleroContainerClientPlugin)
