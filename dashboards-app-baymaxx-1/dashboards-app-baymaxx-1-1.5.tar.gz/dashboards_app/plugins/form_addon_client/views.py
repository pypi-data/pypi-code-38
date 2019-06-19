from collections import OrderedDict

from django.http.response import JsonResponse
from urllib.parse import parse_qs

from dateutil.parser import parse
from .models import *

import pandas as pd
from importlib import import_module
from dashboards_app.models import Dashboard
import json



import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)




def is_date(string):
    try:
        int(string)
        print('int')
        return False
    except ValueError:
        try:
            if string.find('.') != -1:
                print(string.find('.'))
                return False
            else:
                try:
                    parse(string)
                    print('parse')
                    return True
                except:
                    return False
        except:
            return False




def form_addon(request):
    logger.info("Starting form_addon request of data")

    grid_exist=False
    #Import function from asset
    logger.debug(request.POST)
    try:
        form_data = parse_qs(request.POST['form'])

        dashboard_id=json.loads(request.POST['dashboard_id'])
        active_dashboard = Dashboard.objects.get(pk=dashboard_id)
        py_module = import_module('resources.dashboards.' + active_dashboard.slug + '.FormFunctions')
        try:
            grid_data=json.loads(request.POST['grid_data'])
            grid_keys=json.loads(request.POST['grid_keys'])

            grid_data_df = pd.DataFrame(index=grid_keys, columns=range(len(grid_data[0])))
            for counter, i in enumerate(grid_data_df.index):
                grid_data_df.loc[i] = grid_data[counter]

            grid_exist=True

        except Exception as e:
            logger.debug("Grid not read")




    except Exception as e:
        logger.exception('Couldnt import module')



    try:

        if form_data['save_calculate'][0] == '1':
            pass


        elif form_data['save_calculate'][0] == '0':


            if 'model_name' in form_data \
                and 'model_comments' in form_data \
                and 'save_calculate' in form_data:
                del form_data['model_name']
                del form_data['model_comments']
                del form_data['save_calculate']

            py_function = form_data['py_function'][0]
            Form_Dict = OrderedDict()

            for key, value in form_data.items():
                Form_Dict[key] = value[0]





            data_1 = json.loads(request.POST['regressors'])
            data_2 = json.loads(request.POST['target'])

            try:
                dashboard_name = json.loads(request.POST['dashboard_name']).strip().lower()
                dashboard_author = json.loads(request.POST['dashboard_author']).strip().replace(' ', '')
                dashboard_id=json.loads(request.POST['dashboard_id'])
                logger.debug("dashboard id: "+ dashboard_id)
                logger.debug("dashboard name is: "+dashboard_name)

                logfile_name = 'resources/user_logs/' + dashboard_author + dashboard_name.replace(' ','-') +dashboard_id+ '.log'
                logger.debug("sending to log file "+logfile_name)


            except Exception as e:
                logger.exception("Error extracting log file in FormAddonViews")
                logfile_name = 'form_addon.log'





            logger.increase_logger_level()
            try:
                ExecutionClass = getattr(py_module, "FormExecution")()

                if grid_exist == True:
                    ExecutionClass.set_grid_data(grid_data_df)


                logger.debug(Form_Dict)
                result = ExecutionClass.delay(py_function, file_name=logfile_name,
                                                    dict_form=Form_Dict,
                                                    data_1=data_1, data_2=data_2)
                resp_json = {
                    'exec_status': 'success',
                    'exec_id': result.task_id,
                    'form_instance': form_data["form_instance"],
                }

                logger.info(py_function+ " Function Sent to Celery")
            except Exception as e:
                logger.exception("Could not initialize class")
                resp_json = {
                    'exec_status': 'error',
                }








            return JsonResponse(json.dumps(resp_json), safe=False)


    except Exception as e:
        logger.exception("error")
