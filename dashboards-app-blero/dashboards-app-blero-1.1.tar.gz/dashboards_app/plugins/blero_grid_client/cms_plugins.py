# -*- coding: utf-8 -*-

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from dashboards_app.blero_utils.client_utils.client_to_server import request_plugin_render

from .models import *



import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)






class BleroGridClientPlugin(CMSPluginBase):
    model = BleroGrid
    name = 'Blero Grid'
    render_template = "blero_grid_client/grid_base.html"


    def render(self, context, instance, placeholder):


        try:

            model_name=instance._meta.model_name
            app_label=instance._meta.app_label
            context.update({
                'model_name': model_name,
                'app_label': app_label
            })

            context.update({
                'instance': instance


            })
            active_grid = BleroGrid.objects.get(pk=instance.pk)
            grid_values = GridCells.objects.all().filter(model=active_grid)
            row_values=GridRows.objects.all().filter(model=active_grid)

            cell_data = {}
            for cell in grid_values:
                cell_data[cell.row_number] = {'column_number': cell.column_number, 'cell_content': cell.cell_content}
            context.update({
                'cell_data': cell_data

            })

            row_data={}
            for row in row_values:
                row_data[int(row.row_number)]=row.row_content

            row_content=[]
            for value in sorted(row_data.keys()):
                row_content.append(row_data[value])

            context.update({
                'row_data':row_content
            })



            server_fields=self.get_server_fields(instance)
            context.update(server_fields)

        except Exception as e:
            logger.exception("error")


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





plugin_pool.register_plugin(BleroGridClientPlugin)
