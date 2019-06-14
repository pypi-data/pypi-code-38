import logging
import re
from urllib.parse import urlparse

# noinspection PyPackageRequirements
import statsd

from tracuni.misc.select_coroutine import (
    IOLoop,
    PeriodicCallback,
    get_coroutine_decorator,
)
from tracuni.define.type import (
    StatsdOptions,
)
if not IOLoop:
    import asyncio

async_decorator = get_coroutine_decorator()

ERROR_NOT_CONNECTED = "StatsD is not available!"
MSG_REQUEST = '%s.http_request,code=%d,hostname=%s,mean_time=%d'
MSG_EXCEPTION = '%s.exception,code=%d'
MSG_METHOD_APIKEY = '%s.method_apikey,method=%s,code=%d,apikey=%s'
check_http_prefix = re.compile(r'^udp://')

EXCEPTION_COUNT = '%s.%s,class=%s,variant=%s'
HTTP_OUT_TIME = '%s.%s,code=%d,hostname=%s'
HTTP_IN_CODE_COUNT = '%s.%s,code=%s,widget_id=%s,method=%s'
HTTP_IN_METHOD_TIME = '%s.%s,name=%s,widget_id=%s,method=%s'
DB_TIME = '%s.%s,func_name=%s'

def run_later_if_enabled(fn):
    def decorated(self, *args, **kwargs):
        @async_decorator
        def wrapper():
            try:
                fn(self, *args, **kwargs)
            except Exception as e:
                logging.error(e)
            yield

        if self.enable:
            if self.run_later:
                if IOLoop:
                    IOLoop.current().spawn_callback(
                        wrapper
                    )
                else:
                    asyncio.ensure_future(wrapper())
            else:
                return wrapper()
    return decorated


class StatsD:

    def __init__(self, config):
        self.run_later = config.get('run_later', True)
        self.enable = config.get('enable', False)
        self.logging = config.get('logging', False)
        self.config = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', 8125),
            'sample_rate': 1,
            'disabled': not self.enable,
        }
        self.loaded_config = config
        self.name = config.get('prefix', 'svc_api')
        self.hb = None
        self.hb_interval = (config.get('hb_interval', 30) or 30) * 1000

    def connect(self):
        if not self.logging:
            logger_timer = logging.getLogger(
                'statsd.client.Timer'
            )
            logger_timer.propagate = False
            logger_counter = logging.getLogger(
                'statsd.client.Counter'
            )
            logger_counter.propagate = False
            logger_connection = logging.getLogger(
                'statsd.connection.Connection'
            )
            logger_connection.propagate = False
            logger_connection.setLevel(logging.CRITICAL)

        try:
            statsd.Connection.set_defaults(**self.config)
            statsd.Client(name=self.name)
            self.hb = statsd.Counter(self.name)
            if PeriodicCallback:
                PeriodicCallback(
                    callback=self.heartbeat,
                    callback_time=self.hb_interval
                ).start()
            else:
                loop = asyncio.get_event_loop()
                task = asyncio.ensure_future(self.heartbeat())
                loop.call_later(self.hb_interval, task.cancel)
        except Exception as e:
            self.enable = False
            logging.error(e)
            logging.error(ERROR_NOT_CONNECTED)
        return

    @async_decorator
    def heartbeat(self):
        if self.enable:
            name = self.loaded_config['measure_names'].check_count
            self.hb.increment(name)
        yield

    @run_later_if_enabled
    def send_gauge(self, key, value):
        gauge = statsd.Gauge(self.name)
        gauge.send(key, value)

    @run_later_if_enabled
    def exception(self, code):
        statsd.increment(MSG_EXCEPTION % (self.name, code))

    @run_later_if_enabled
    def exception_count_glork(self, xlass, variant):
        statsd.increment(EXCEPTION_COUNT % (
            self.name,
            self.loaded_config['measure_names'].exception_count,
            xlass,
            variant
        ))

    @run_later_if_enabled
    def http_out_time_glork(self, rsp_status, rq_hostname, secundos):
        timer = statsd.Timer('some')
        timer.connection.send({
            HTTP_OUT_TIME % (
                self.name,
                self.loaded_config['measure_names'].http_out_time,
                rsp_status,
                rq_hostname
            ): f"{secundos:d}|ms|@0.9"
        })

    @run_later_if_enabled
    def http_in_method_time_glork(self, app_method, widget_id, json_method, secundos):
        timer = statsd.Timer('some')
        timer.connection.send({
            HTTP_IN_METHOD_TIME % (
                self.name,
                self.loaded_config['measure_names'].http_in_method_time,
                app_method,
                widget_id,
                json_method,
            ): f"{secundos:d}|ms|@0.9"
        })

    @run_later_if_enabled
    def db_time_glork(self, app_method, secundos):
        timer = statsd.Timer('some')
        timer.connection.send({
            DB_TIME % (
                self.name,
                self.loaded_config['measure_names'].db_time,
                app_method,
            ): f"{secundos:d}|ms|@0.9"
        })

    @run_later_if_enabled
    def http_in_code_count_glork(self, code, widget_id, json_method):
        statsd.increment(HTTP_IN_CODE_COUNT % (
            self.name,
            self.loaded_config['measure_names'].http_in_code_count,
            code,
            widget_id,
            json_method
        ))

    @run_later_if_enabled
    def http_request(self, rsp_status, rq_hostname, request_time):
        statsd.increment(MSG_REQUEST % (self.name, rsp_status, rq_hostname, request_time))

    @run_later_if_enabled
    def method_apikey(self, method, code, apikey):
        statsd.increment(MSG_METHOD_APIKEY % (self.name, method, code, apikey))

    def start_timer(self):
        if self.enable:
            timer = statsd.Timer(self.name)
            timer.start()
            return timer

    @run_later_if_enabled
    def stop_timer(self, timer, label):
        if timer:
            timer.stop(label)

    @run_later_if_enabled
    def send_timer(self, name, value):
        timer = statsd.Timer(self.name)
        timer.send(name, value)

    @staticmethod
    def read_statsd_configuration(statsd_conf):
        statsd_enable = bool(statsd_conf.enable)
        statsd_url = statsd_conf.url
        if not check_http_prefix.match(statsd_url):
            return StatsdOptions(**{"enable": False})
        statsd_url = urlparse(
            statsd_url
        )

        statsd_is_configured = bool(statsd_url) and statsd_enable
        if statsd_is_configured and not statsd_url.hostname:
            statsd_is_configured = False
            logging.error('Incorrect statsd url')

        # noinspection PyProtectedMember
        updated_conf = statsd_conf._asdict()
        updated_conf.update({
            'enable': statsd_is_configured,
            'host': statsd_url.hostname,
            'port': statsd_url.port,
        })
        statsd_conf = StatsdOptions(**updated_conf)

        return statsd_conf
