# -*- coding: utf-8 -*-

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from dashboards_app.models import Dashboard



from importlib import import_module
from dashboards_app.blero_utils.client_utils.client_to_server import request_plugin_render


from .models import *
import pandas as pd
import sqlite3


import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__name__))



def CreateHTMLTable(df, id):
    try:
        records = len(df.index)
        html = ''

        html += '<table id="db-data-table-' + str(id) + '" class="display compact data-table-display" width="100%" >'

        html += '<thead><tr>'
        for col in df.columns:
            html += '<th>' + col + '</th>'

        html += '</tr></thead><tbody>'

        for row in range(records):
            html += '<tr id=' + str(row) + '>'
            for col in df.columns:
                html += '<td>' + str(df[col].iloc[row]) + '</td>'
            html += '</tr>'

        html += '</tbody></table>'
    except Exception as e:
        logger.exception('Error Creting Table')

    return html

class DBPlugin_individualClient(CMSPluginBase):
    model = DBPlugin_individual
    name = "Blero Daatabase -child"
    render_template = "db_addon_client/detail_dbplugin.html"

    def render(self, context, instance, placeholder):

        model_name = instance._meta.model_name
        app_label=instance._meta.app_label
        context.update({
            'model_name': model_name,
            'app_label': app_label
        })


        logger.info('Connecting to DB ...')

        try:

            # Include DB
            try:
                database_name = instance.database_name

                try:
                    table_name = instance.database_table_name
                except:
                    logger.exception("DB couldnt find table with name "+ instance.database_table_name)
            except:
                logger.exception("DB not found "+ instance.database_table_name)

            database = os.path.join(BASE_DIR, 'resources/DB/' + database_name + '.db')

            conn = sqlite3.connect(database)
            logger.info("Connected To Database " +database_name)
            c = conn.cursor()

            c.execute('SELECT * FROM {tn}'. \
                      format(tn=table_name, ))
            all_rows = c.fetchall()
            c.execute('PRAGMA table_info({tn})'. \
                      format(tn=table_name, ))

            list_col = c.fetchall()
            col_names = [col[1] for col in list_col]
            query_df = pd.DataFrame(all_rows, columns=col_names)
            conn.close()

            logger.logger.info("Data Extracted and Transformed by %s", instance.database_py_function)

            try:
                # ToDo Transform Queried DF using the desired python function
                active_plugin = CMSPlugin.objects.get(pk=instance.cmsplugin_ptr_id)
                dashboard = Dashboard.objects.get(sidebar_content_id=active_plugin.placeholder_id)
                dash_slug = dashboard.slug
                dash_author = dashboard.author
                dash_author = dash_author.name.replace(" ", "")

                try:

                    py_module = import_module('resources.dashboards.' + dash_slug + '.FormFunctions')
                    py_function = instance.database_py_function
                    method = getattr(py_module, py_function)
                    modified_df = method(query_df.copy(), dash_author, dashboard.id)

                    logger.info("Database filtered by function")
                except Exception as e:
                    logger.exception('Couldnt import module')
                    modified_df = query_df

                # sort by column

                try:
                    filter = instance.database_filter_column
                    modified_df = modified_df.sort_values(filter)

                    filtered_column = modified_df.columns.get_indexer([filter])
                    logger.logger.info("DataBase sorted by "+ str(filter))
                    logger.debug(filtered_column)
                except Exception as e:
                    logger.exception("Couldnt find column"+str(filter)+" to sort")
                    filtered_column = []


            except:
                logger.exception("Data Frame couldnt be transformed to Data Table ")

            sc = CreateHTMLTable(modified_df, instance.cmsplugin_ptr_id)
            logger.info("DataBase %s read succesfully "+ database)

        except Exception as e:
            logger.logger.exception("DataBase %s was not read", database)
            sc = []
            filtered_column = []
            query_df = pd.DataFrame()


        context.update({
            'instance': instance,
            'data_table': sc,
            'filtered_column': filtered_column,
            'total_columns': len(query_df.columns),
        })

        self.get_server_fields(instance)
        return context

    def get_server_fields(self, instance):
        """

        :param instance:
        :return:
        """

        try:
            server_fields=request_plugin_render(instance)

        except:
            logger.debug('error requesting to server')

        return server_fields


class DBPluginClient(CMSPluginBase):
    model = DBPlugin
    name = 'Blero Databases'
    render_template = "db_addon_client/base_dbplugin.html"
    allow_children = True
    child_classes = ['DBPlugin_individualClient']

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,

        })

        return context


plugin_pool.register_plugin(DBPluginClient)
plugin_pool.register_plugin(DBPlugin_individualClient)
