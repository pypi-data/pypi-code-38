import logging
import os

import docker

from missinglink.resource_manager.docker.config import docker_client
from missinglink.resource_manager.docker.pip import get_version
from missinglink.resource_manager.docker.utils import is_windows_containers
from missinglink.resource_manager.docker.sync_async_tools import run_blocking_code_in_thread
import io
import csv

logger = logging.getLogger(__name__)


class DockerWrapper:
    CUDA_BASE_IAMGE = 'nvidia/cuda:9.0-base'

    def __init__(self, host_base_url=None):
        self.docker_client = docker_client(host_base_url=host_base_url)

    @classmethod
    def _safe_get(cls, method, args=None, kwargs=None, default=None):
        args = args or []
        kwargs = kwargs or {}
        try:
            return method(*args, **kwargs)
        except docker.errors.NotFound:
            return default

    @staticmethod
    def _get_docker_host_port():
        return os.environ.get('ML_DOCKER_HOST_PORT', '2375')

    @staticmethod
    def _get_default_gateway():
        import netifaces

        try:
            gateways = netifaces.gateways()
            return gateways['default'][netifaces.AF_INET][0]
        except Exception as exc:
            logging.warning('Could not get default gateway address: %s', exc)
            return None

    @classmethod
    def _get_docker_host_base_url(cls):
        default_gateway = cls._get_default_gateway()
        if default_gateway is None:
            return None

        docker_host_port = cls._get_docker_host_port()
        return '{}:{}'.format(default_gateway, docker_host_port)

    @classmethod
    def get(cls):
        host_base_url = cls._get_docker_host_base_url() if is_windows_containers() else None
        return cls(host_base_url=host_base_url)

    def container(self, container_id):
        return self._safe_get(self.docker_client.containers.get, [container_id])

    def volume(self, volume_id):
        return self._safe_get(self.docker_client.volumes.get, [volume_id])

    def image(self, image_id):
        return self._safe_get(self.docker_client.images.get, [image_id])

    def create_volume(self, name, **kwargs):
        labels = kwargs.pop('labels', {})

        for k, v in labels.items():
            if not isinstance(v, str):
                labels[k] = str(v)
        kwargs['labels'] = labels
        return self.docker_client.volumes.create(name, **kwargs)

    def create_container(self, **kwargs):
        return self.docker_client.containers.create(**kwargs)

    def raw_status(self):
        return self.docker_client.info()

    def be_summary(self):

        raw = self.raw_status()
        key_mapping = {
            "cpu.memory": "MemTotal",
            "cpu.count": "NCPU",
            "cpu.max.memory": "MemTotal",
            "cpu.max.count": "NCPU",
            "server.arch": "Architecture",
            "server.kernel": "KernelVersion",
            "server.os": "OperatingSystem",
            "server.name": 'Name',
            "server.type": 'OSType',

        }
        res = {}

        def set_key_in_path(key_, val_):
            # res[key] = val
            # TODO: fix deep dics FB error
            prc = res
            key_arr = key_.split('.')
            for lvl in key_arr[:-1]:  # the last one is the key
                if lvl not in prc:
                    prc[lvl] = {}
                prc = prc[lvl]
            prc[key_arr[-1]] = val_

        for key in key_mapping:
            src = key_mapping[key]
            val = raw.get(src)
            set_key_in_path(key, val)
        res["server"]['rm'] = {
            'ML_RM_VERSION': get_version(),
            'ML_PIP_INDEX': os.environ.get('ML_PIP_INDEX'),
            'ML_PIP_VERSION': os.environ.get('ML_PIP_VERSION')
        }
        return res

    @classmethod
    def _get_gpus_from_nvidia_smi_output(cls, output):
        csv_txt = output.decode('utf-8').strip()
        with io.StringIO(csv_txt) as csv_file:
            csv_reader = csv.DictReader(csv_file, skipinitialspace=True, delimiter=',')
            res = []
            for row in csv_reader:
                res.append(dict(row))
            return res

    def _get_gpus(self):
        self.docker_client.images.pull(self.CUDA_BASE_IAMGE)
        smi_output = self.docker_client.containers.run(
            self.CUDA_BASE_IAMGE,
            'nvidia-smi '
            '--query-gpu=index,uuid,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode,temperature.gpu '
            '--format=csv,nounits',
            runtime="nvidia", remove=True)
        gpus = self._get_gpus_from_nvidia_smi_output(smi_output)
        logger.info('found %s gpus: %s', len(gpus), [x['name'] for x in gpus])
        return gpus

    def has_nvidia(self):
        try:
            return self._get_gpus()
        except Exception as ex:
            logger.debug('GPU not found, ignore the error if you do not have GPU installed on this machine', exc_info=1)
            logger.info('GPU not found, ignore the error if you do not have GPU installed on this machine: %s', str(ex))
            return None

    @classmethod
    def _image_downgrade_supported(cls, image):
        return True

    @classmethod
    def _remove_gpu_tag(cls, image):
        if ':' not in image:
            return image

        image_parts = image.split(':')
        tag = image_parts[-1]
        if 'gpu' not in tag:
            return image

        tag = tag.replace('gpu', '').replace('--', '-')
        if tag.endswith('-'):
            tag = tag[:-1]
        if tag.startswith('-'):
            tag = tag[1:]
        image_parts[-1] = tag
        return ':'.join(image_parts)

    @classmethod
    def downgrade_gpu_image_if_needed(cls, original_image, has_gpu):
        if has_gpu:
            return original_image

        if cls._image_downgrade_supported(original_image):
            image = cls._remove_gpu_tag(original_image)
            if image != original_image:
                logger.warning('image %s changed to %s due to lack of GPU on the host machine' % (original_image, image))
            else:
                logger.info('will use image %s on cpu server', original_image)
            return image

    async def async_pull(self, image):
        return await run_blocking_code_in_thread(lambda: self.docker_client.images.pull(image), logger=logger)
