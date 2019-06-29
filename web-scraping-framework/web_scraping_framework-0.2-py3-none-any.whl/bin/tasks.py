import sys

from celery import Celery  # default Celery App Class
from celery.exceptions import Ignore
from celery.signals import after_setup_logger

sys.path.append("..")
from bin.CustomApp import CustomBackendCalls

import logging


app_name = 'default_custom_task'
app = Celery(app_name)

@after_setup_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    """
    This will initialise logger for celery tasks.
    :param logger: logger object
    :param args:
    :param kwargs:
    :return:
    """
    file_handler = logging.FileHandler("{0}/{1}.log".format('/home/ubuntu/', 'xfinapi'))
    formating_string = '[%(asctime)s: %(levelname)s-%(processName)s] %(message)s'
    file_handler.setFormatter(logging.Formatter(formating_string))
    logger.addHandler(file_handler)


@app.task(bind=True, base=CustomBackendCalls)
def defaultTask(self):
    raise Ignore
