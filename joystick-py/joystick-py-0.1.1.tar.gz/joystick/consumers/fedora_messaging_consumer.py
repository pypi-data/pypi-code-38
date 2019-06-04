import boto3
import fedfind
import fedfind.release
import itertools
import logging
import subprocess

from fedora_messaging import api
from fedora_messaging.config import conf
from fedora_messaging.message import Message


_log = logging.getLogger(__name__)


class JoyStickController(object):
    """
    JoyStick controller for plume.
    """

    def __init__(self):
        self.config = conf["consumer_config"]
        self.aws_access_key_id = self.config['aws_access_key_id']
        self.aws_secret_access_key = self.config['aws_secret_access_key']
        self.valid_status = ('FINISHED_INCOMPLETE', 'FINISHED')
        self.regions = self.config['regions']

    def run_command(self, command):
        _log.info("Starting the command: %r" % command)
        ret = subprocess.Popen(' '.join(command), stdin=subprocess.PIPE,
                               shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, close_fds=True)
        out, err = ret.communicate()
        retcode = ret.returncode
        _log.info("Finished executing the command: %r" % command)

        if retcode != 0:
            _log.error("Command failed during run")
            _log.error(
                "(output) %s, (error) %s, (retcode) %s" % (out, err, retcode))
        else:
            _log.debug(
                "(output) %s, (error) %s, (retcode) %s" % (out, err, retcode))

        return out, err, retcode

    def __call__(self, msg):
        _log.info("Received message: %s", msg.id)
        topic = msg.topic
        body = msg.body

        msg_info = {}
        if 'msg' not in body:
            return
        else:
            msg_info = body['msg']


        if topic.endswith("pungi.compose.status.change"):
            _log.debug("Processing %r" % (msg.id))
            if msg_info['status'] not in self.valid_status:
                _log.debug("%s is not a valid status" % msg_info["status"])
                return

            compose_id = msg_info.get('compose_id')
            try:
                compose_metadata = fedfind.release.get_release(
                    cid=compose_id).metadata
            except fedfind.exceptions.UnsupportedComposeError:
                _log.debug("%s is unsupported composes" % compose_id)
                return

            self.location = msg_info['location']

            self.channel = self.location.rsplit('/', 3)
            if not self.channel:
                _log.debug('channel cannot be empty')
                return

            self.channel = self.channel[1]
            if self.channel not in ['cloud', 'branched', 'updates', 'rawhide']:
                _log.debug('%s is not a valid channel' % self.channel)
                return

            self.compose_id = msg_info['compose_id']
            self.respin = msg_info['compose_respin']
            self.timestamp = msg_info['compose_date']
            self.release_version = msg_info['release_version']
            self.aws_crendentials = '~/.aws/credentials'
            for image_type, board in itertools.product(['Cloud-Base', 'AtomicHost'], ['x86_64', 'aarch64']):
                self.image_type = image_type
                self.board = board

                if self.channel == 'cloud' and self.image_type == 'AtomicHost':
                    continue

                output, error, retcode = self._run_pre_release()
                if not retcode != 0:
                    _log.debug("There was an issue with pre-release")
                    _log.debug(error)
                    continue

                output, error, retcode = self._publish_upload_messages()
                if not retcode != 0:
                    _log.debug("There was an issue with publishing messages")
                    _log.debug(error)

                output, error, retcode = self._run_release()
                if not retcode != 0:
                    _log.debug("There was an issue with release")
                    _log.debug(error)
                    continue

                output, error, retcode = self._publish_publish_messages()
                if not retcode != 0:
                    _log.debug("There was an issue with publishing messages")
                    _log.debug(error)
        else:
            _log.debug("Dropping %r: %r" % (topic, msg.id))
            pass

    def _run_pre_release(self):
        output, error, retcode = self.run_command([
            'plume',
            'pre-release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', str(self.respin),
            '--board', self.board,
            "--compose-id", self.compose_id,
            "--image-type", self.image_type,
            "--aws-credentials", self.aws_crendentials,
        ])

        return output, error, retcode

    def _run_release(self):
        output, error, retcode = self.run_command([
            'plume',
            'release',
            '--system', 'fedora',
            '--channel', self.channel,
            '--version', self.release_version,
            '--timestamp', self.timestamp,
            '--respin', str(self.respin),
            '--board',  self.board,
            '--compose-id', self.compose_id,
            '--image-type', self.image_type,
            '--aws-credentials', self.aws_credentials
        ])

        return output, error, retcode

    def _generate_ami_upload_list(self):
        for region in self.regions:
            conn = boto3.client(
                "ec2",
                region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            _log.info("%s: Connected" % region)

            images = conn.describe_images(
                Filters=[
                    {
                        'Name': 'ComposeID',
                        'Values': [
                            self.compose_id
                        ]
                    },
                ],
            )

            self.uploaded_images = [
                {
                    'id': image['ImageId'],
                    'vol_type': image["BlockDeviceMappings"][0]['Ebs']['VolumeType'],
                    'region': region,
                    'arch': image['Architecture'],
                    'virt_type': image['VirtualizationType']
                } for image in images['Images']
            ]

    def _publish_messages(self):
        self._generate_ami_upload_list()

        for image in self.uploaded_images:
            msg = Message(
                    topic="image.upload",
                    body={
                        u'status': u'completed',
                        u'compose': self.compose_id,
                        u'service': u'EC2',
                        u'extra': {
                            u'virt_type': u'hvm',
                            u'id': image['id'],
                            u'vol_type': image['vol_type'],
                        }
                    }
                )
            api.publish(msg)

    def _publish_upload_messages(self):
        self._generate_ami_upload_list()

        for image in self.uploaded_images:
            msg = Message(
                    topic="image.publish",
                    body={
                        u'compose': self.compose_id,
                        u'service': u'EC2',
                        u'destination': image['region'],
                        u'architecture': image['arch'],
                        u'extra': {
                            u'virt_type': image['virt_type'],
                            u'id': image['id'],
                            u'vol_type': image['vol_type'],
                        }
                    }
                )
            api.publish(msg)
