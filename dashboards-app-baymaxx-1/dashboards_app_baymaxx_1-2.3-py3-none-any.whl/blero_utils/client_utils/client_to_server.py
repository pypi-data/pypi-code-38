from cms.models.pluginmodel import CMSPlugin, Placeholder
from dashboards_app.models import Dashboard
import requests
from django.core import serializers
from django.apps import apps
import json

from .logging_helpers import log_message_level as ll
from .settings import *

# loggin Details#
import logging
#Start Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create a file handler
handler = logging.FileHandler('client_server_communications.log')
handler.setLevel(logging.DEBUG)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)


def delete_server_plugin(plugin_instance):
    """

    :param plugin_instance: self from model delete override method
    :param user_api_key:
    :param user_server_login:
    :param user_server_password:
    :return:
    this function makes a post request to the already created Api on the server, to update remote dashboard on request.
    """
    # get cms plugin pk
    plugin_type = plugin_instance._meta.model_name
    look_up_field = plugin_instance._meta.app_label + "_" + plugin_instance._meta.model_name
    look_up_params = {look_up_field: plugin_instance}
    cms_plugin = CMSPlugin.objects.get(**look_up_params)

    data_to_post = {'plugin_type': plugin_type,
                    'user_author': USER_TOKEN,
                    'client_pk': cms_plugin.pk,
                    'post_data': "delete",
                    }
    response = requests.post(SERVER_ADDRESS, data=data_to_post,
                             headers={'Authorization': 'Token ' + USER_TOKEN})

    logger.info(ll(0, 'Plugin deleted'))

def check_special_cases(instance,json_data):
    """
    This functions checks special cases of plugins to be serialized accordingly
    :param instance:
    :return: returns json_data with particular fields
    """
    model_name = instance._meta.model_name
    app_label = instance._meta.app_label

    return json_data


SIDE_BAR_PLUGINS=["dbplugin_individual"]

def request_plugin_render(instance):
    """

    :param user_api_key:
    :param user_server_login:
    :param user_server_password:
    :param instance: instance of the blero plugin that is rendering on the cms
    :return:
    """
    level=0
    try:

        model_name=instance._meta.model_name
        app_label=instance._meta.app_label
        RenderingModel = apps.get_model(app_label,model_name )
        logger.debug(model_name)
        if model_name in SIDE_BAR_PLUGINS:
            pass
        else:
            PositionModel= apps.get_model(instance._meta.app_label,'PluginPosition')



        json_data = {}
        if hasattr(instance, 'related_objects'):

            json_data['related_objects']=instance.related_objects

        cms_plugin = CMSPlugin.objects.filter(pk=instance.pk)
        cms_plugin_serialized = serializers.serialize('json', cms_plugin)
        json_data['cms_plugin'] = json.loads(cms_plugin_serialized)[0]
        placeholder_type = Placeholder.objects.filter(id=json_data['cms_plugin']['fields']['placeholder'])[0].slot
        json_data['cms_plugin']['fields']['placeholder_type'] = placeholder_type
        plugin_type = json_data['cms_plugin']['fields']['plugin_type']
        logger.info(ll(level,"initiating request server for "+ plugin_type))
        level=level+1

        local_plugin = RenderingModel.objects.get(pk=instance.pk)
        # get dictionary with the model fields with exception of the csm plugin value

        plugin_fields = {f.name: getattr(local_plugin, f.name) for f in RenderingModel._meta.local_fields if
                         f.name != 'cmsplugin_ptr'}

        json_data['plugin'] = plugin_fields

        logger.debug(plugin_type)
        if model_name in  SIDE_BAR_PLUGINS:

            if model_name=="dbplugin_individual":
                pass


        else: #Plugins that have position

            # special plugins
            if plugin_type=="TaskHolderClientPlugin":
                #remove not serializable objeects

                json_data["plugin"].pop("since_date")

            #if position havnt been created then create it
            plugin_position, created = PositionModel.objects.get_or_create(model=local_plugin)

            position_fields = {f.name: getattr(plugin_position, f.name) for f in
                               PositionModel._meta.local_fields if f.name != 'model'}

            json_data['plugin_position'] = position_fields


        if placeholder_type == 'dashboard_content':

            target_dashboard = Dashboard.objects.filter(content_id=json_data['cms_plugin']['fields']['placeholder'])

        elif placeholder_type == 'dashboard_sidebar_content':

            target_dashboard = Dashboard.objects.filter(
                sidebar_content_id=json_data['cms_plugin']['fields']['placeholder'])

        dashboard_serialized_data = serializers.serialize('json', target_dashboard)

        json_data['dashboard'] = json.loads(dashboard_serialized_data)[0]
        json_data['dashboard']['dashboard-slug'] = target_dashboard[0].slug
        json_data['user'] = {'username': USER_TOKEN}

        logger.debug(json_data["plugin"])
        post_raw_data = json.dumps(json_data)
        # change plugin type to server side
        plugin_type = plugin_type.replace('Client', '')
        data_to_post = {'plugin_type': plugin_type,
                        'user_author': json_data['user']['username'],
                        'client_pk': json_data['cms_plugin']['pk'],
                        'post_data': post_raw_data}



        ########### Start the requestin
        # POST creates plugin in server if not excists if exist updates values
        response = requests.post(SERVER_ADDRESS, data=data_to_post,
                                 headers={'Authorization': 'Token ' + USER_TOKEN})
        plugin_response = response.json()
        # TODO: Can this be optimize to do a POST when new plugin is created for first time, PUT for update and then GET?
        #TODO: get right the authentication
        # Get plugin data


        get_query = SERVER_ADDRESS+'?client_pk=' + str(instance.pk) + '&user_author=' + USER_TOKEN
        logger.debug(get_query)
        response = requests.get(get_query, headers = {'Authorization':'Token '+USER_TOKEN})



        server_fields = json.loads(response.json()[0]['cms_plugin_render'])

        logger.info(ll(level, 'Terminated server request'))

    except Exception as e:
        logger.exception("plugin not serialized")
        server_fields = []

    return server_fields
