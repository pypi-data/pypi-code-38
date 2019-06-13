import re
import datetime

from onepanel.models.api_json import APIJSON
from onepanel.utilities.time import parse_date, format_timedelta, utcnow
from onepanel.models.machine_type import MachineType
from onepanel.models.volume_type import VolumeType
from onepanel.models.project import Project
from onepanel.models.instance_template import InstanceTemplate
from onepanel.models.dataset_mount import DatasetMount
from onepanel.models.git_source import GitSource


class Instance(APIJSON):
    CREATED = 'created'
    STARTING = 'starting'
    STARTED = 'started'
    READY = 'ready'
    PAUSED = 'paused'
    RESUMING = 'resuming'
    RESUMED = 'resumed'

    def __init__(self):
        self.uid = None
        self.created_at = None
        self.launched_at = None
        self.started_at = None
        self.ready_at = None
        self.last_stopped_at = None
        self.active = False
        self.project = Project()
        self.machine_type = MachineType()
        self.volume_type = VolumeType()
        self.instance_template = InstanceTemplate()
        self.dataset_mounts = []
        self.dataset_mount_claims = []
        self.git_source = None

    @classmethod
    def from_json(cls, dct):
        instance = cls()

        instance.set_uid(dct['uid'])
        instance.created_at = parse_date(dct['createdAt'])

        #LaunchedAt is ommited from API if it is empty 
        if 'launchedAt' in dct:
            instance.launched_at = parse_date(dct['launchedAt'])
        
        instance.started_at = parse_date(dct['startedAt'])
        instance.ready_at = parse_date(dct['readyAt'])
        instance.last_stopped_at = parse_date(dct['lastStoppedAt'])
        instance.active = dct['active']
        instance.project = Project.from_json(dct['project'])
        instance.machine_type = MachineType.from_json(dct['machineType'])
        instance.volume_type = VolumeType.from_json(dct['volumeType'])
        instance.instance_template = InstanceTemplate.from_json(dct['instanceTemplate'])
        instance.git_source = GitSource.from_json(dct['gitSource'])

        return instance

    @classmethod
    def from_simple_json(cls, dct):
        instance = cls()

        instance.set_uid(dct['name'])
        instance.machine_type.uid = dct['machine']
        instance.volume_type.uid = dct['storage']
        instance.instance_template.uid = dct['environment']
        instance.dataset_mount_identifiers = [DatasetMount.from_simple_json(item) for item in dct['datasets']]
        instance.git_source = GitSource.from_string(dct['git'])

        return instance

    def set_uid(self, uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')

        if not pattern.match(uid):
            raise ValueError(
                'Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')

        self.uid = uid

    # TODO document
    def simple_view(self):
        info = self.machine_type.info

        item = {
            'account_uid': self.project.account.uid,
            'project_uid': self.project.uid,
            'uid': self.uid,
            'cpu': info['cpu'],
            'gpu': info['gpu'],
            'ram': info['ram'],
            'hdd': self.volume_type.info['size'],
            'duration_ready': format_timedelta(self.duration_ready()),
            'duration_paused': format_timedelta(self.duration_paused()),
            'age': format_timedelta(self.age()),
            'state': self.state()
        }

        return item

    def state(self):
        if not self.active:
            if self.last_stopped_at is not None:
                return Instance.PAUSED

            return Instance.CREATED

        if self.ready_at is not None:
            return Instance.READY

        if self.started_at is not None:
            if self.last_stopped_at is not None:
                return Instance.RESUMED

            return Instance.STARTED

        if self.last_stopped_at is not None:
            return Instance.RESUMING

        return Instance.STARTING

    def duration_ready(self, when=None):
        """How long the instance has been ready for. This is calculated from the last time it was 
           marked ready to when."""
        if when is None:
            when = utcnow()

        if self.state() != Instance.READY:
            return None

        return when - self.ready_at

    def duration_paused(self, when=None):
        """How long the instance has been paused for, if it is paused. If not paused, returns None"""
        if self.state() != Instance.PAUSED:
            return None

        if when is None:
            when = utcnow()

        return when - self.last_stopped_at

    def age(self, when=None):
        """How long the instance has been created to when"""
        if when is None:
            when = utcnow()

        if self.created_at is None:
            return datetime.timedelta(0)

        return when - self.created_at

    def api_json(self):
        json = {
            'uid': self.uid,
            'machineType': self.machine_type,
            'volumeType': self.volume_type,
            'instanceTemplate': self.instance_template,
            'datasetMountClaims': self.dataset_mount_claims,
        }

        if self.git_source is not None:
            json['gitSource'] = self.git_source

        return json
