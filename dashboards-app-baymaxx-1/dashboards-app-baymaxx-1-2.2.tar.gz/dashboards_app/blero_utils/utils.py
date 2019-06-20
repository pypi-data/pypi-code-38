

import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)


def set_up_dashboard_tree(active_dashboard):
    author = active_dashboard.author


    logger.logger.debug(author)

    try:
        file_name = 'resources/user_logs/' + str(author).replace(" ", "") + active_dashboard.slug + str(
            active_dashboard.id) + ".log"
        if os.path.isfile(file_name) == False:

            logger.debug(os.path.abspath(os.curdir))
            f = open(file_name, "w")
            f.close()
            logger.debug('Log file created in ' + file_name)
        else:
            logger.debug('log file already created')
    except Exception as e:
        logger.exception("Error file not created")

    # create dashboard python modules Tree
    directory = 'resources/dashboards/' + active_dashboard.slug + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # create dashboard js modules Tree
    directory = 'static/js/dashboards/' + active_dashboard.slug + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create ajax_functionsfile
    file_name = 'static/js/dashboards/' + active_dashboard.slug + '/ajax_functions' + active_dashboard.slug + '.js'
    if os.path.isfile(file_name) == False:
        f = open(file_name, 'w')
        f.write("//this file should hold the ajax functions for interaction in form_addon, dont delete")
        f.close()
        logger.debug('Form Functions ajax created')

    # make them python directories
    file_name = 'resources/dashboards/' + active_dashboard.slug + '/__init__.py'
    if os.path.isfile(file_name) == False:
        f = open(file_name, 'w')
        f.close()
        logger.debug('Dashboard Module Created')

    file_name = 'resources/dashboards/' + active_dashboard.slug + '/FormFunctions.py'
    if os.path.isfile(file_name) == False:
        f = open(file_name, 'w')
        f.write(
            "#this file should hold the functions that can be selected in each dashboard, do not delete or rename this file")
        f.close()
        logger.debug('Form Functions Module Created')

    # initialize all dashboards functions
    file_name = 'resources/dashboards/__init__.py'
    if os.path.isfile(file_name) == False:
        f = open(file_name, 'w')
        f.close()
        logger.debug('Dashboard  Created')

