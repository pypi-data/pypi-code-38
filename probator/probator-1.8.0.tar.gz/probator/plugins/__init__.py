import json
import logging
from abc import abstractmethod, ABC
from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum

from flask import current_app, make_response
from flask_restful import Resource, reqparse
from flask_script import Command
from pkg_resources import EntryPoint
from probator import PROBATOR_PLUGINS
from probator.config import dbconfig
from probator.constants import HTTP, UNAUTH_MESSAGE
from probator.database import db
from probator.json_utils import ProbatorJSONEncoder
from probator.schema import SchedulerBatch, LogEvent

Worker = namedtuple('Worker', ('name', 'interval', 'entry_point'))


class CollectorType(Enum):
    GLOBAL = 1
    AWS_REGION = 2
    AWS_ACCOUNT = 3


class BasePlugin(object):
    options = ()
    dbconfig = dbconfig

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__module__)

    @property
    @abstractmethod
    def name(self):
        """Human friendly name of the Plugin"""


class BootstrappedBasePlugin(BasePlugin, ABC):
    bootstrapped = False

    @staticmethod
    def bootstrap():
        """Bootstrapping method for the plugin"""


class BaseAuditor(BootstrappedBasePlugin, ABC):
    start_delay = 30

    @classmethod
    def enabled(cls):
        return dbconfig.get('enabled', cls.ns, False)

    @property
    @abstractmethod
    def ns(self):
        """Namespace prefix for configuration settings"""

    @property
    @abstractmethod
    def interval(self):
        """Interval, in minutes, of how frequently the auditor executus"""

    @abstractmethod
    def run(self, *args, **kwargs):
        """Main worker entry point for the auditor"""


class BaseAuthPlugin(BasePlugin, ABC):
    # region Methods
    def bootstrap(self):
        """Default bootstrapping method, auth plugin's can do initialization tasks here, will only be run on startup
        of the API server.

        Returns:
            `None`
        """

    def _is_active_auth_system(self):
        """Return `True` if the current system is the active auth system, otherwise `False`

        Returns:
            `bool`
        """
        return current_app.active_auth_system == self.__class__.ns
    # endregion

    # region Properties
    @property
    @abstractmethod
    def ns(self):
        pass

    @property
    @abstractmethod
    def views(self):
        pass

    @property
    @abstractmethod
    def readonly(self):
        pass

    @property
    @abstractmethod
    def login(self):
        pass

    @property
    @abstractmethod
    def logout(self):
        pass
    # endregion


class BaseCollector(BasePlugin, ABC):
    @classmethod
    def enabled(cls):
        return dbconfig.get('enabled', cls.ns, False)

    @property
    @abstractmethod
    def interval(self): pass

    @property
    @abstractmethod
    def ns(self): pass

    @property
    @abstractmethod
    def type(self): pass

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError('Collector has not implemented the run method')

    def process_resources(self, *, resource_class, account_id, location, new_resources, existing_resources):
        """

        Args:
            resource_class (`class`): A reference to the Resource class
            account_id (`int`): ID of the account the resource is in
            location (`str`, `None`): Location of the resource. Optional
            new_resources (`dict` of `str`: :obj:`NewResource`): A dict of resources from the API
            existing_resources (`dict` of `str`: :obj:`BaseResource`): A dict containing all existing resources of the given type

        Returns:
            `None`
        """

        for resource_id, data in new_resources.items():
            if resource_id in existing_resources:
                resource = existing_resources[resource_id]
                if resource.update_resource(properties=data.properties, tags=data.tags):
                    self.log.debug(f'Changed detected for {resource_class.resource_name} {resource}')
                    db.session.add(resource.resource)

            else:
                resource = resource_class.create(
                    resource_id=resource_id,
                    account_id=account_id,
                    location=location,
                    properties=data.properties,
                    tags=data.tags
                )
                if data.parent:
                    data.parent.add_child(resource)
                    db.session.add(data.parent.resource)

                db.session.add(resource.resource)

                self.log.debug(f'Created {resource_class.resource_name} {resource}')

        db.session.commit()

        existing_keys = set(existing_resources.keys())
        current_keys = set(new_resources.keys())

        for resource_id in existing_keys - current_keys:
            eks = existing_resources[resource_id]
            self.log.debug(f'Deleted {eks.resource_name} {eks}')
            eks.delete()

        db.session.commit()


class BaseCommand(BasePlugin, Command, ABC):
    pass


class BaseNotifier(BasePlugin, ABC):
    @classmethod
    def enabled(cls):
        return dbconfig.get('enabled', cls.ns, False)

    @property
    @abstractmethod
    def ns(self): pass


class BaseScheduler(BasePlugin, ABC):
    def __init__(self):
        super().__init__()

        self.auditors = []
        self.collectors = {}

    @staticmethod
    def get_class_from_ep(entry_point):
        return EntryPoint(**entry_point).resolve()

    def load_plugins(self):
        """Refresh the list of available collectors and auditors

        Returns:
            `None`
        """
        for entry_point in PROBATOR_PLUGINS['probator.plugins.collectors']['plugins']:
            cls = entry_point.load()
            if cls.enabled():
                self.log.debug(f'Collector loaded: {cls.__name__} in module {cls.__module__}')
                self.collectors.setdefault(cls.type, []).append(Worker(
                    cls.name,
                    cls.interval,
                    {
                        'name': entry_point.name,
                        'module_name': entry_point.module_name,
                        'attrs': entry_point.attrs
                    }
                ))
            else:
                self.log.debug(f'Collector disabled: {cls.__name__} in module {cls.__module__}')

        for entry_point in PROBATOR_PLUGINS['probator.plugins.auditors']['plugins']:
            cls = entry_point.load()
            if cls.enabled():
                self.log.debug(f'Auditor loaded: {cls.__name__} in module {cls.__module__}')
                self.auditors.append(Worker(
                    cls.name,
                    cls.interval,
                    {
                        'name': entry_point.name,
                        'module_name': entry_point.module_name,
                        'attrs': entry_point.attrs
                    }
                ))
            else:
                self.log.debug(f'Auditor disabled: {cls.__name__} in module {cls.__module__}')

        collector_count = sum(len(x) for x in self.collectors.values())
        auditor_count = len(self.auditors)

        if collector_count + auditor_count == 0:
            raise Exception('No auditors or collectors loaded, aborting scheduler')

        self.log.info(f'Scheduler loaded {collector_count} collectors and {auditor_count} auditors')

    def cleanup(self):
        self.log.info('Running cleanup tasks')
        try:
            log_retention_days = dbconfig.get('log_keep_days', 'log', default=31)
            log_purge_date = datetime.now() - timedelta(days=log_retention_days)
            deleted_logs = db.LogEvent.find(LogEvent.timestamp < log_purge_date)
            deleted_batches = db.SchedulerBatch.filter(SchedulerBatch.started < (datetime.now() - timedelta(days=14))).delete()

            db.session.commit()
            self.log.info(f'Expired {deleted_logs} log entries and {deleted_batches} scheduler batches')
        finally:
            db.session.rollback()

    @abstractmethod
    def execute_scheduler(self):
        """Entry point to execute the scheduler

        The scheduler should execute as a daemon, which will ensure that the worker threads will get scheduled
        until the process is stopped"""

    @abstractmethod
    def execute_worker(self):
        """Main worker execution entry point

        Each execution of the worker thread should handle a single request from the scheduler and exit, to allow for
        manual/stepped execution of the jobs. The command line worker utility will handle running schedulers in daemon
        mode, unless the user explicitly requests single a execution"""


class BaseView(BasePlugin, Resource):
    enabled = True
    URLS = []
    name = 'view'

    def __init__(self):
        super().__init__()
        self.reqparse = reqparse.RequestParser()

        # Monkey patch parse_args to return a munch so we can use object notation instead of slices/keys
        self.reqparse._org_parse_args = self.reqparse.parse_args
        self.reqparse.parse_args = lambda *args, **kwargs: self.reqparse._org_parse_args(*args, **kwargs)

    @staticmethod
    def make_response(data, code=HTTP.OK, content_type='application/json'):
        if isinstance(data, str):
            data = {'message': data}

        else:
            if 'message' not in data:
                data['message'] = None

        resp = make_response(json.dumps(data, sort_keys=False, cls=ProbatorJSONEncoder), code)
        resp.mimetype = content_type

        return resp

    @staticmethod
    def make_unauth_response():
        return BaseView.make_response(UNAUTH_MESSAGE, HTTP.UNAUTHORIZED)
