
# -*- coding: utf-8 -*-

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from .models import *
#TODO: Modify to bleor_grid_client
from dashboards_app.plugins.blero_grid_client.cms_plugins import BleroGridClientPlugin
from dashboards_app.plugins.blero_grid_client.models import GridCells
from dashboards_app.plugins.blero_grid_client.models import PluginPosition as BGPluginPosition


from dashboards_app.blero_utils.client_utils.client_to_server import  request_plugin_render


import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)



class FormInputsInlineClient(admin.StackedInline):
    model = FormInputs
    fk_name = 'id_fr'


class BleroGridFormPluginClient(BleroGridClientPlugin):
    """
    Child class of the BleroGrid, this class allows to obtaine values from the grid as a DataFrame when form is submitted
    """
    model=BleroGridFormClient
    name="Form Grid"
    import dashboards_app
    render_template = dashboards_app.__path__[0] + "/plugins/blero_grid_client/templates/blero_grid_client/grid_base.html"

    def render(self, context, instance, placeholder):
        data = []

        active_grid = BleroGridClientPlugin.objects.get(pk=instance.pk)
        grid_values = GridCells.objects.all().filter(model=active_grid)

        cell_data = {}

        for cell in grid_values:
            cell_data[cell.row_number] = {'column_number': cell.column_number, 'cell_content': cell.cell_content}

        columns = int(instance.grid_columns)
        rows=int(instance.grid_rows)
        position = BGPluginPosition.objects.filter(model=instance).first()
        context.update({
            'instance': instance,
            'cell_data': cell_data,
            'position': position,
            'columns': [i for i in range(columns)],
            'rows': [i for i in range(rows)],
        })

        return context

class FormsPluginClient(CMSPluginBase):
    model = FormPlugin
    name = "Form Addon"
    render_template = "form_addon_client/create_form.html"
    inlines = (FormInputsInlineClient,)

    allow_children = True
    child_classes = ['BleroGridFormClientPlugin']

    # Class plug in should be modified to have two more fields
    # a boolean field that says if it should load a saved model or not
    # text field with a dropdown for the names of the models saved,
    #
    # if the boolean is selected then the full form will be overwriten and rendered with the saved model values.
    # name=savedmode.model.name
    # pyfunction=savedmodel.model.pyfunction
    # ETC, so all the fields of the form pluse the selected securities and dates should be  saved and loaded.

    def __init__(self, model=None, admin_site=None):
        super(FormsPluginClient, self).__init__(model=model,
                                          admin_site=admin_site)
        for inline in self.inlines:
            inline.placeholder = self.placeholder
            inline.page = self.page

    def render(self, context, instance, placeholder):
        context = super(FormsPluginClient, self).render(context, instance, placeholder)

        model_name=instance._meta.model_name
        app_label=instance._meta.app_label
        context.update({
            'model_name': model_name,
            'app_label': app_label
        })





        #Get fields instances
        try:

            new_items = []
            items = FormInputs.objects.filter(id_fr=instance).select_related('inp_position').select_related(
                'label_position')

            fields=FormInputs.objects.filter(id_fr=instance)

            field_list = []
            if items.count() > 0:

                for item in items:
                    item.app_label = item._meta.app_label
                    item.model_name = item._meta.model_name
                    new_items.append(item)


                for field in fields:
                    field_attributes={}
                    for attribute in field._meta.get_fields():
                        try:
                            field_attributes.update({attribute.name: getattr(field, attribute.name)})
                        except:
                            pass


                    try:
                        label_position = field_attributes['label_position']
                        field_attributes['label_position'] = {attribute.name: getattr(label_position, attribute.name) for
                                                              attribute in
                                                              label_position._meta.get_fields()}
                        inp_position = field_attributes['inp_position']
                        field_attributes['inp_position'] = {attribute.name: getattr(inp_position, attribute.name) for
                                                            attribute in
                                                            inp_position._meta.get_fields()}

                        field_attributes['inp_position'].pop('model')
                        field_attributes['label_position'].pop('model')



                    except ObjectDoesNotExist:
                        pass
                    except KeyError:
                        pass

                    field_attributes.pop('id_fr')
                    field_list.append(field_attributes)


            try:
                instance.btn_position.app_label = instance.btn_position._meta.app_label
                instance.btn_position.model_name = instance.btn_position._meta.model_name
            except ObjectDoesNotExist:

                btn_position, created = FormBtnPluginPosition.objects.get_or_create(model=instance)
                instance.btn_position = btn_position
                instance.btn_position.app_label = instance.btn_position._meta.app_label
                instance.btn_position.model_name = instance.btn_position._meta.model_name
        except:
            logger.exception('Error rendering fields')


        context.update({
            'instance': instance,
            'inputs': new_items

        })


        instance_to_server=instance
        instance_to_server.related_objects=field_list

        server_fields = self.get_server_fields(instance_to_server)
        context.update(server_fields)


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
            logger.debug('error requesting to server')

        return server_fields


plugin_pool.register_plugin(FormsPluginClient)
plugin_pool.register_plugin(BleroGridFormPluginClient)
