import os
import logging
import pika
import time
import threading
import json
from logging.handlers import RotatingFileHandler
from jsonschema import validate
from .namegen import random_name
from functools import wraps
this_dir, this_filename = os.path.split(__file__)

LOG_APP = 'app'
LOG_PERF = 'perf'
LOG_OTHERS = 'others'

LOG = logging.getLogger(LOG_APP)
PLOG = logging.getLogger(LOG_PERF)

def track_uuid():
    # return uuid.uuid1().int >> 64
    # return uuid.uuid1().hex
    return random_name()


def sorted_dir(folder, rev=False):
    def getmtime(name):
        path = os.path.join(folder, name)
        return os.path.getmtime(path)
    return sorted(os.listdir(folder), key=getmtime, reverse=rev)


def get_latest_checked(folder, suffix):
    content = sorted_dir(folder, rev=True)
    for f in content:
        if not f.endswith(suffix):
            continue
        basename = os.path.splitext(f)[0]
        full_name = os.path.join(folder, basename + '.json')
        if os.path.exists(full_name):
            return full_name, basename
    return None, None

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))



def perf(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        t1 = time.time()
        rt = f(*args, **kwargs)
        PLOG.debug("{}() {:.4f} ms.".format(f.__name__,(time.time() - t1) * 1000.0))
        return rt
    return decorated

def setup_log_env():
    loglevel_app = 'INFO'
    loglevel_perf = 'INFO'
    loglevel_others = 'WARNING'

    if 'LOG_LEVEL' in os.environ:
        levels = os.environ['LOG_LEVEL'].split(',')
        if len(levels) > 0:
            loglevel_app = levels[0]
        if len(levels) > 1:
            loglevel_perf = levels[1]
        if len(levels) > 2:
            loglevel_others = levels[2]
    conf = {
        "log" : {
            "app" : loglevel_app,
            "perf": loglevel_perf,
            "others": loglevel_others,
        }
    }
    setup_log(conf,just_console=True)


def setup_log(conf, just_console = False):
    if just_console:
        olog = logging.StreamHandler()
    else:
        olog = RotatingFileHandler( os.path.join( conf['log']['logdir'],conf['log']['logfileprefix']+'.'+ LOG_OTHERS+'.log' ),
                                    maxBytes=conf['log']['logmaxbytes'], backupCount=conf['log']['logcount'])
    olog.setLevel( conf['log'][LOG_OTHERS])
    olog.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s %(message)s'))
    logroot = logging.getLogger()
    logroot.setLevel(conf['log'][LOG_OTHERS])
    logroot.addHandler(olog)

    if just_console:
        ch = logging.StreamHandler()
    else:
        ch = RotatingFileHandler( os.path.join( conf['log']['logdir'],conf['log']['logfileprefix']+'.'+ LOG_APP+'.log' ),
                                maxBytes=conf['log']['logmaxbytes'], backupCount=conf['log']['logcount'])

    ch.setLevel(conf['log'][LOG_APP])
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s %(message)s'))
    alog = logging.getLogger(LOG_APP)
    alog.setLevel(conf['log'][LOG_APP])
    alog.addHandler(ch)

    if just_console:
        perf = logging.StreamHandler()
    else:
        perf = RotatingFileHandler( os.path.join( conf['log']['logdir'],conf['log']['logfileprefix']+'.'+ LOG_PERF+'.log' ),
                                maxBytes=conf['log']['logmaxbytes'], backupCount=conf['log']['logcount'])

    perf.setLevel(conf['log'][LOG_PERF])
    perf.setFormatter(logging.Formatter('%(asctime)s - PERF - %(filename)s.%(funcName)s %(message)s'))
    plog = logging.getLogger(LOG_PERF)
    plog.setLevel(conf['log'][LOG_PERF])
    plog.addHandler(perf)


MAX_CONNECTION_RETRIES = 100
ENV_MQ_HOST = 'RABBITMQ_HOST'
ENV_MQ_USER = 'RABBITMQ_USER'
ENV_MQ_PASS = 'RABBITMQ_PASS'

def create_mq_connection( max_connection_retries = MAX_CONNECTION_RETRIES):
    LOG.debug('Creating mq connection')
    host = None if not ENV_MQ_HOST in os.environ else os.environ[ENV_MQ_HOST]
    user = 'guest' if not ENV_MQ_USER in os.environ else os.environ[ENV_MQ_USER]
    password = 'guest' if not ENV_MQ_PASS in os.environ else os.environ[ENV_MQ_PASS]
    cred = pika.credentials.PlainCredentials(
        user, password)
    ret = None
    connected = False
    retry = 0
    while not connected:
        try:
            retry += 1
            ret = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, credentials=cred))
            connected = True
        except Exception as e:
            if retry > max_connection_retries:
                LOG.error('Something is terribly wrong')
                return None
            LOG.warning(e)
            LOG.warning('Trying to reconnect to {} {}'.format(host,user))
            time.sleep(2)
    return ret

def close_mq_connection(connection):
    LOG.debug('Closing mq connection')
    try:
        connection.close()
    except Exception as e:
        LOG.error(e, exc_info=True)


schema_loading_lock = threading.Lock()
schema_loaded = None

def get_job_schema():
    global schema_loading_lock, schema_loaded
    if not schema_loaded:
        try:
            schema_loading_lock.acquire()
            schema = os.path.join(this_dir,'job.schema.json')
            with open(schema, 'r') as f:
                schema_loaded = json.load(f)
        finally:
            schema_loading_lock.release()
    return schema_loaded


def validate_job_schema(json_data):
    validate(json_data, get_job_schema())