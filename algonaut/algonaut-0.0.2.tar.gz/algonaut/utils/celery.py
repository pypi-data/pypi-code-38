import logging
import datetime

from celery import Celery, __version__ as celery_version
from celery.schedules import crontab
from kombu import Queue

from .helpers.celery import config_mapping_3_4

logger = logging.getLogger(__name__)

def make_celery(settings):
    """
    Creates a new celery object which can be used to define tasks.
    """
    celery_settings = settings.get('worker',{})
    celery_config = celery_settings.get('config',{}).copy()
    celery_obj = Celery("algonaut", broker=celery_config['broker_url'])

    #we convert the queues
    queues = []
    for queue in celery_config.get('task_queues',[]):
        queues.append(Queue(**queue))
    celery_config['task_queues'] = queues

    #we parse the celerybeat task schedule
    celerybeat_schedule = celery_settings.get('schedule', {})

    new_schedule = {}
    for task, params in celerybeat_schedule.items():
        params = params.copy()
        if not 'schedule' in params:
            logger.warning("No schedule for task {}, skipping...".format(task))
            continue
        schedule = params.get('schedule', {})
        if 'timedelta' in schedule:
            params['schedule'] = datetime.timedelta(**schedule['timedelta'])
        elif 'crontab' in schedule:
            params['schedule'] = crontab(**schedule['crontab'])
        else:
            logger.error("Unknown schedule format for task {}, skipping...".format(task))
            continue
        new_schedule[task] = params

    celery_config['beat_schedule'] = new_schedule

    #if we use Celery 3, we map the config parameter names to the old format
    if celery_version.startswith('3.'):
        for key, value in celery_config.items():
            if key in config_mapping_3_4:
                del celery_config[key]
                celery_config[config_mapping_3_4[key]] = value

    celery_obj.conf.update(**celery_config)

    return celery_obj
