from django.http import JsonResponse

import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)


def log_checker(request):
    dashboard = request.POST['dashboard']
    author = request.POST['author']

    file_name = 'resources/user_logs/' + author + dashboard + ".log"
    # logger.info(file_name)

    with open(file_name, 'r') as f:
        lines = f.read().splitlines()
        if len(lines) > 0:
            # TODO: Use the model to display the number of desired lines
            last_line = lines[-100:]
            logs = ''
            for i in last_line:
                logs += i + '\n'
            logfile = logs


        else:
            logfile = 'No logs found!'

    return JsonResponse({'logfile': logfile, 'id': author + dashboard})


def delete_log_content(request):
    dashboard = request.POST['dashboard']
    author = request.POST['author']

    file_name = 'resources/user_logs/' + author + dashboard + ".log"
    try:
        with open(file_name, "w"):
            result = True
            pass
    except:
        result = False

    return JsonResponse({'result': result})
