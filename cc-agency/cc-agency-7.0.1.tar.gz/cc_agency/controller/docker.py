import os
from queue import Queue
from threading import Thread
from time import time
from traceback import format_exc
from uuid import uuid4

import docker
from bson.objectid import ObjectId

from cc_agency.commons.secrets import get_experiment_secret_keys, fill_experiment_secrets
from cc_core.commons.engines import engine_to_runtime
from cc_core.commons.gpu_info import set_nvidia_environment_variables

from cc_agency.commons.helper import generate_secret, create_kdf, batch_failure, calculate_agency_id
from cc_agency.commons.build_dir import build_dir_path


CURL_IMAGE = 'docker.io/buildpack-deps:bionic-curl'


class ClientProxy:
    def __init__(self, node_name, conf, mongo, trustee_client):
        self._node_name = node_name
        self._conf = conf
        self._mongo = mongo
        self._trustee_client = trustee_client

        self._build_dir = build_dir_path(conf)

        node_conf = conf.d['controller']['docker']['nodes'][node_name]
        self._base_url = node_conf['base_url']
        self._tls = False
        if 'tls' in node_conf:
            self._tls = docker.tls.TLSConfig(**node_conf['tls'])

        self._environment = node_conf.get('environment')
        self._network = node_conf.get('network')

        self._external_url = conf.d['broker']['external_url'].rstrip('/')

        self._action_q = None
        self._client = None
        self._online = None

        # using hash of external url to distinguish between volume names created by different agency installations
        self._agency_id = calculate_agency_id(conf)
        self._blue_agent_volume = None

        node = {
            'nodeName': node_name,
            'state': None,
            'history': [],
            'ram': None,
            'cpus': None
        }

        bson_node_id = self._mongo.db['nodes'].insert_one(node).inserted_id
        self._node_id = str(bson_node_id)

        try:
            self._client = docker.DockerClient(base_url=self._base_url, tls=self._tls, version='auto')
            ram, cpus = self._info()
            self._fail_batches_without_assigned_container()  # in case of agency restart
        except Exception:
            self._set_offline(format_exc())
            return

        self._action_q = Queue()
        Thread(target=self._action_loop).start()
        self._set_online(ram, cpus)
        self._action_q.put({'action': 'inspect'})

    def _set_online(self, ram, cpus):
        print('Node online:', self._node_name)

        self._online = True
        bson_node_id = ObjectId(self._node_id)
        self._mongo.db['nodes'].update_one(
            {'_id': bson_node_id},
            {
                '$set': {
                    'state': 'online',
                    'ram': ram,
                    'cpus': cpus
                },
                '$push': {
                    'history': {
                        'state': 'online',
                        'time': time(),
                        'debugInfo': None
                    }
                }
            }
        )
        self._action_q.put({'action': 'init_cc_core'})

    def _set_offline(self, debug_info):
        print('Node offline:', self._node_name)
        timestamp = time()

        self._online = False
        bson_node_id = ObjectId(self._node_id)
        self._mongo.db['nodes'].update_one(
            {'_id': bson_node_id},
            {
                '$set': {'state': 'offline'},
                '$push': {
                    'history': {
                        'state': 'offline',
                        'time': timestamp,
                        'debugInfo': debug_info
                    }
                }
            }
        )

        # change state of assigned batches
        cursor = self._mongo.db['batches'].find(
            {
                'node': self._node_name,
                'state': {'$in': ['scheduled', 'processing']}
            },
            {'_id': 1}
        )

        for batch in cursor:
            bson_id = batch['_id']
            batch_id = str(bson_id)
            debug_info = 'Node offline: {}'.format(self._node_name)
            batch_failure(self._mongo, batch_id, debug_info, None, self._conf)

    def _info(self):
        info = self._client.info()
        ram = info['MemTotal'] // (1024 * 1024)
        cpus = info['NCPU']
        return ram, cpus

    def _batch_containers(self, status):
        batch_containers = {}

        if not self._online:
            return batch_containers

        filters = {'status': status}
        if status is None:
            filters = None

        containers = self._client.containers.list(all=True, limit=-1, filters=filters)

        for c in containers:
            try:
                ObjectId(c.name)
                batch_containers[c.name] = c
            except:
                pass

        return batch_containers

    def _fail_batches_without_assigned_container(self):
        containers = self._batch_containers(None)

        cursor = self._mongo.db['batches'].find(
            {
                'node': self._node_name,
                'state': {'$in': ['scheduled', 'processing']}
            },
            {'_id': 1}
        )

        for batch in cursor:
            bson_id = batch['_id']
            batch_id = str(bson_id)

            if batch_id not in containers:
                debug_info = 'No container assigned.'
                batch_failure(self._mongo, batch_id, debug_info, None, self._conf)

    def _remove_cancelled_containers(self):
        running_containers = self._batch_containers('running')

        cursor = self._mongo.db['batches'].find(
            {
                '_id': {'$in': [ObjectId(_id) for _id in running_containers]},
                'state': 'cancelled'
            },
            {'_id': 1}
        )
        for batch in cursor:
            bson_id = batch['_id']
            batch_id = str(bson_id)

            c = running_containers[batch_id]
            c.remove(force=True)

    def _remove_exited_containers(self):
        exited_containers = self._batch_containers('exited')

        cursor = self._mongo.db['batches'].find(
            {'_id': {'$in': [ObjectId(_id) for _id in exited_containers]}},
            {'state': 1}
        )
        for batch in cursor:
            bson_id = batch['_id']
            batch_id = str(bson_id)

            c = exited_containers[batch_id]
            debug_info = c.logs().decode('utf-8')
            c.remove()

            if batch['state'] == 'processing':
                batch_failure(self._mongo, batch_id, debug_info, None, self._conf)

    def inspect_offline_node(self):
        try:
            self._client = docker.DockerClient(base_url=self._base_url, tls=self._tls, version='auto')
            ram, cpus = self._info()
            if self._blue_agent_volume is None:
                self._init_blue_agent(self._build_dir)
            self._inspect()
        except Exception:
            self._client = None
            return

        self._action_q = Queue()
        Thread(target=self._action_loop).start()
        self._set_online(ram, cpus)

    def _inspect(self):
        print('Node inspection:', self._node_name)

        command = 'curl -f {}'.format(self._external_url)

        self._client.containers.run(
            CURL_IMAGE,
            command,
            user='1000:1000',
            remove=True,
            environment=self._environment,
            network=self._network
        )

    def put_action(self, data):
        """
        Adds the action data into the action_q. Returns if this operation was successful or not.

        :param data: The action data to process
        :return: True, if the action could be put into the action_queue, otherwise False
        """
        if self._action_q is None:
            return False

        try:
            self._action_q.put(data)
        except AttributeError:
            return False
        return True

    def _action_loop(self):
        while True:
            data = self._action_q.get()

            if 'action' not in data:
                continue

            action = data['action']

            inspect = False

            if action == 'inspect':
                inspect = True

            elif action == 'check_for_batches':
                try:
                    self._check_for_batches()
                except Exception:
                    inspect = True

            elif action == 'clean_up':
                try:
                    self._remove_cancelled_containers()
                    self._remove_exited_containers()
                except:
                    inspect = True

            if inspect:
                try:
                    if self._blue_agent_volume is None:
                        self._init_blue_agent(self._build_dir)
                    self._inspect()
                except Exception:
                    self._blue_agent_volume = None
                    self._set_offline(format_exc())
                    self._action_q = None
                    self._client = None

            if not self._online:
                return

    def _init_blue_agent(self, build_dir):
        self._client.images.build(path=build_dir, tag='blue-agent')

        for volume in self._client.volumes.list():
            if volume.name.startswith(self._agency_id):
                try:
                    volume.remove()
                except Exception:
                    pass

        blue_agent_volume = '{}-{}'.format(self._agency_id, str(uuid4()))

        binds = {
            blue_agent_volume: {
                'bind': os.path.join('/vol'),
                'mode': 'rw'
            }
        }

        command = 'cp /cc/blue_agent.py /vol'

        self._client.containers.run(
            'blue-agent',
            command,
            remove=True,
            volumes=binds
        )

        self._blue_agent_volume = blue_agent_volume

    def _check_for_batches(self):
        """
        Queries the database to find batches, which are in state 'scheduled' and are scheduled to the node of this
        ClientProxy. If a batch with these conditions was found, the docker image for this batch is pulled and the batch
        is started. The state of the batch is then updated to 'processing'.
        :raise TrusteeServiceError: If the trustee service is unavailable or the trustee service could not fulfill all
        requested keys
        """

        # query for batches, that are in state 'scheduled' and are scheduled to this node
        query = {
            'state': 'scheduled',
            'node': self._node_name
        }

        for batch in self._mongo.db['batches'].find(query):
            # get batch_id and experiment
            batch_id = batch['_id']
            experiment = self._get_experiment_with_secrets(batch['experimentId'])

            # pull image
            try:
                self._pull_image_for_experiment(experiment)
            except:
                self._pull_image_failure(format_exc(), batch_id)
                continue

            # run container
            try:
                self._run_batch_container(batch, experiment)
            except:
                self._run_batch_container_failure(batch_id, format_exc())

    def _get_experiment_with_secrets(self, experiment_id):
        """
        Returns the experiment of the given experiment_id with filled secrets.
        :param experiment_id: The experiment id to resolve.
        :return: The experiment as dictionary with filled template values.
        :raise TrusteeServiceError: If the trustee service is unavailable or the trustee service could not fulfill all
        requested keys
        """
        experiment = self._mongo.db['experiments'].find_one(
            {'_id': ObjectId(experiment_id)},
        )

        experiment = self._fill_experiment_secret_keys(experiment)

        return experiment

    def _fill_experiment_secret_keys(self, experiment):
        """
        Returns the given experiment with filled template keys and values.
        :param experiment: The experiment to complete.
        :return: Returns the given experiment with filled template keys and values.
        :raise TrusteeServiceError: If the trustee service is unavailable or the trustee service could not fulfill all
        requested keys
        """
        experiment_secret_keys = get_experiment_secret_keys(experiment)
        response = self._trustee_client.collect(experiment_secret_keys)
        if response['state'] == 'failed':

            debug_info = response['debugInfo']

            if response.get('inspect'):
                response = self._trustee_client.inspect()
                if response['state'] == 'failed':
                    debug_info = response['debug_info']
                    raise TrusteeServiceError('Trustee service unavailable:{}{}'.format(os.linesep, debug_info))

            experiment_id = str(experiment['_id'])
            raise TrusteeServiceError(
                'Trustee service request failed for experiment "{}":{}{}'.format(experiment_id, os.linesep, debug_info)
            )

        experiment_secrets = response['secrets']
        return fill_experiment_secrets(experiment, experiment_secrets)

    def _pull_image_for_experiment(self, experiment):
        """
        Reads the needed docker image for the given batch and pulls it on the node of this ClientProxy.
        :param experiment: An experiment with filled secret keys, whose image should be pulled
        :raise TrusteeServiceError: If the trustee service is unavailable or the trustee service could not fulfill all
        requested keys
        :raise Exception: If the given image authentication information is not complete (username and password are
        mandatory)
        """

        image_url = experiment['container']['settings']['image']['url']

        image_auth = experiment['container']['settings']['image'].get('auth')
        if image_auth:
            for mandatory_key in ('username', 'password'):
                if mandatory_key not in image_auth:
                    raise Exception('Image authentication is given, but "{}" is missing'.format(mandatory_key))

        self._pull_image(image_url, image_auth)

    def _run_batch_container(self, batch, experiment):
        """
        Runs the given batch, with settings described in the given batch and experiment.
        Sets the state of the given batch to 'processing'.
        Creates a callback token for the given batch

        :param batch: The batch to run
        :type batch: dict
        :param experiment: The experiment of this batch
        :type experiment: dict
        """
        batch_id = str(batch['_id'])
        runtime = engine_to_runtime(experiment['container']['engine'])

        # set nvidia gpu environment
        gpus = batch['usedGPUs']
        environment = {}
        if self._environment:
            environment = self._environment.copy()
        if gpus:
            set_nvidia_environment_variables(environment, gpus)

        # set mount variables
        devices = []
        capabilities = []
        security_opt = []
        if batch['mount']:
            devices.append('/dev/fuse')
            capabilities.append('SYS_ADMIN')
            security_opt.append('apparmor:unconfined')

        # set image
        image = experiment['container']['settings']['image']['url']

        token = generate_secret()
        salt = os.urandom(16)
        kdf = create_kdf(salt)

        self._mongo.db['callback_tokens'].insert_one({
            'batch_id': batch_id,
            'salt': salt,
            'token': kdf.derive(token.encode('utf-8')),
            'timestamp': time()
        })

        command = [
            'python3',
            '/cc/blue_agent.py',
            '--outputs',
            '{}/callback/{}/{}'.format(self._external_url, batch_id, token)
        ]

        command = ' '.join([str(c) for c in command])

        ram = experiment['container']['settings']['ram']
        mem_limit = '{}m'.format(ram)

        binds = {
            self._blue_agent_volume: {
                'bind': '/cc',
                'mode': 'ro'
            }
        }

        self._mongo.db['batches'].update_one(
            {'_id': ObjectId(batch_id)},
            {
                '$set': {
                    'state': 'processing',
                },
                '$push': {
                    'history': {
                        'state': 'processing',
                        'time': time(),
                        'debugInfo': None,
                        'node': self._node_name,
                        'ccagent': None
                    }
                }
            }
        )

        # remove container if it exists from earlier attempt
        existing_container = self._batch_containers(None).get(batch_id)
        if existing_container is not None:
            existing_container.remove(force=True)

        self._client.containers.run(
            image,
            command,
            name=batch_id,
            user='1000:1000',
            remove=False,
            detach=True,
            mem_limit=mem_limit,
            memswap_limit=mem_limit,
            runtime=runtime,
            environment=environment,
            network=self._network,
            volumes=binds,
            devices=devices,
            cap_add=capabilities,
            security_opt=security_opt
        )

    def _run_batch_container_failure(self, batch_id, debug_info):
        batch_failure(self._mongo, batch_id, debug_info, None, self._conf)

    def _pull_image(self, image, auth):
        self._client.images.pull(image, auth_config=auth)

    def _pull_image_failure(self, debug_info, batch_id):
        batch_failure(self._mongo, batch_id, debug_info, None, self._conf)


class TrusteeServiceError(Exception):
    pass
