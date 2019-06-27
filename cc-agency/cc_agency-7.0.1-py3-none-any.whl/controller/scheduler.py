import os
import sys
from threading import Thread
from queue import Queue, Full
from time import time, sleep

import requests
from bson.objectid import ObjectId

from cc_core.commons.gpu_info import GPUDevice, match_gpus, get_gpu_requirements, InsufficientGPUError
from cc_core.commons.red import red_get_mount_connectors_from_inputs

from cc_agency.controller.docker import ClientProxy, TrusteeServiceError
from cc_agency.commons.helper import calculate_agency_id, batch_failure
from cc_agency.commons.build_dir import init_build_dir
from cc_agency.commons.secrets import get_experiment_secret_keys, fill_experiment_secrets
from cc_agency.commons.secrets import get_batch_secret_keys

_CRON_INTERVAL = 60


class CompleteNode:
    """
    Represents a processing node inside a cluster.
    """

    def __init__(self, node_name, online, ram, gpus, ram_available, gpus_available, num_batches_running):
        """
        Initialises a new CompleteNode.
        :param node_name: The name of the node given by the agency config.
        :param online: Whether the given node is online or not.
        :param ram: The amount of ram of this node.
        :param gpus: The GPUs that are present on this node. Does include gpus, which are used by batches.
        :param ram_available: The ram that is available. Given by the amount of ram of the node minus the amount of ram
        used by batches.
        :param gpus_available: The GPUs that are available and not used by batches.
        :param num_batches_running: The number of batches currently running on the node.
        """
        self.node_name = node_name
        self.online = online
        self.ram = ram
        self.gpus = gpus
        self.ram_available = ram_available
        self.gpus_available = gpus_available
        self.num_batches_running = num_batches_running


class Scheduler:
    def __init__(self, conf, mongo, trustee_client):
        self._conf = conf
        self._mongo = mongo
        self._trustee_client = trustee_client

        self._agency_id = calculate_agency_id(conf)

        mongo.db['nodes'].drop()

        self._scheduling_q = Queue(maxsize=1)
        self._inspection_q = Queue(maxsize=1)
        self._voiding_q = Queue(maxsize=1)
        self._notification_q = Queue(maxsize=1)

        init_build_dir(conf)

        self._nodes = {
            node_name: ClientProxy(node_name, conf, mongo, trustee_client)
            for node_name
            in conf.d['controller']['docker']['nodes'].keys()
        }

        Thread(target=self._scheduling_loop).start()
        Thread(target=self._inspection_loop).start()
        Thread(target=self._voiding_loop).start()
        Thread(target=self._notification_loop).start()
        Thread(target=self._cron).start()

    def _cron(self):
        while True:
            batch = self._mongo.db['batches'].find_one(
                {'$or': [
                    {'state': {'$nin': ['succeeded', 'failed', 'cancelled']}},
                    {'protectedKeysVoided': False},
                    {'notificationsSent': False}
                ]},
                {'_id': 1}
            )
            if batch:
                self.schedule()

            sleep(_CRON_INTERVAL)

    def schedule(self):
        try:
            self._scheduling_q.put_nowait(None)
        except:
            pass

    def _inspection_loop(self):
        while True:
            self._inspection_q.get()

            cursor = self._mongo.db['nodes'].find(
                {'state': 'offline'},
                {'nodeName': 1, 'state': 1}
            )

            threads = []

            for node in cursor:
                node_name = node['nodeName']
                client_proxy = self._nodes[node_name]
                t = Thread(target=client_proxy.inspect_offline_node)
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

    def _notification_loop(self):
        while True:
            self._notification_q.get()

            # batches
            cursor = self._mongo.db['batches'].find(
                {
                    'state': {'$in': ['succeeded', 'failed', 'cancelled']},
                    'notificationsSent': False
                },
                {'state': 1}
            )

            bson_ids = []
            payload = {'batches': []}

            for batch in cursor:
                bson_id = batch['_id']
                bson_ids.append(bson_id)

                payload['batches'].append({
                    'batchId': str(bson_id),
                    'state': batch['state']
                })

            self._mongo.db['batches'].update(
                {'_id': {'$in': bson_ids}},
                {'$set': {'notificationsSent': True}}
            )

            notification_hooks = self._conf.d['controller'].get('notification_hooks', [])

            for hook in notification_hooks:
                auth = hook.get('auth')

                if auth is not None:
                    auth = (auth['username'], auth['password'])

                try:
                    r = requests.post(hook['url'], auth=auth, json=payload)
                    r.raise_for_status()
                except Exception as e:
                    debug_info = 'Notification post hook failed:{0}{1}{0}{2}'.format(os.linesep, repr(e), e)
                    print(debug_info, file=sys.stderr)

    def _voiding_loop(self):
        while True:
            self._voiding_q.get()

            # batches
            cursor = self._mongo.db['batches'].find(
                {
                    'state': {'$in': ['succeeded', 'failed', 'cancelled']},
                    'protectedKeysVoided': False
                }
            )

            for batch in cursor:
                bson_id = batch['_id']

                batch_secret_keys = get_batch_secret_keys(batch)
                self._trustee_client.delete(batch_secret_keys)

                self._mongo.db['batches'].update_one({'_id': bson_id}, {'$set': {'protectedKeysVoided': True}})

            # experiments
            cursor = self._mongo.db['experiments'].find(
                {
                    'protectedKeysVoided': False
                }
            )

            for experiment in cursor:
                bson_id = experiment['_id']
                experiment_id = str(bson_id)

                all_count = self._mongo.db['batches'].count({'experimentId': experiment_id})

                finished_count = self._mongo.db['batches'].count({
                    'experimentId': experiment_id,
                    'state': {'$in': ['succeeded', 'failed', 'cancelled']}
                })

                if all_count == finished_count:
                    experiment_secret_keys = get_experiment_secret_keys(experiment)
                    self._trustee_client.delete(experiment_secret_keys)

                    self._mongo.db['experiments'].update_one({'_id': bson_id}, {'$set': {'protectedKeysVoided': True}})

    def _scheduling_loop(self):
        while True:
            self._scheduling_q.get()

            # inspect offline nodes
            try:
                self._inspection_q.put_nowait(None)
            except Full:
                pass

            # void protected keys
            try:
                self._voiding_q.put_nowait(None)
            except Full:
                pass

            # send notifications
            try:
                self._notification_q.put_nowait(None)
            except Full:
                pass

            # inspect trustee
            response = self._trustee_client.inspect()
            if response['state'] == 'failed':
                debug_info = response['debug_info']
                print('Trustee service unavailable, retry in {} seconds:{}{}'.format(
                    _CRON_INTERVAL, os.linesep, debug_info
                ), file=sys.stderr)
                sleep(_CRON_INTERVAL)
                continue

            self._schedule_batches()

    @staticmethod
    def _get_busy_gpu_ids(batches, node_name):
        """
        Returns a list of busy GPUs in the given batches

        :param batches: The batches to analyse given as list of dictionaries.
                        If GPUs are busy by a current batch the key 'usedGPUs' should be present.
                        The value of 'usedGPUs' has to be a list of busy device IDs.
        :return: A list of GPUDevice-IDs, which are used by the given batches on the given node
        """

        busy_gpus = []
        for b in batches:
            if b['node'] == node_name:
                batch_gpus = b.get('usedGPUs')
                if type(batch_gpus) == list:
                    busy_gpus.extend(batch_gpus)

        return busy_gpus

    def _get_present_gpus(self, node_name):
        """
        Returns a list of GPUDevices

        :param node_name: The name of the node
        :return: A list of GPUDevices, which are representing the GPU Devices present on the specified node
        """

        result = []

        gpus = self._conf.d['controller']['docker']['nodes'][node_name].get('hardware', {}).get('gpus')
        if gpus:
            for gpu in gpus:
                result.append(GPUDevice(device_id=gpu['id'], vram=gpu['vram']))

        return result

    def _get_available_gpus(self, node, batches):
        """
        Returns a list of available GPUs on the given node.
        Available in this context means, that this device is present on the node and is not busy with another batch.

        :param node: The node whose available GPUs should be calculated
        :param batches: The batches currently running
        :return: A list of available GPUDevices of the specified node
        """

        node_name = node['nodeName']

        busy_gpu_ids = Scheduler._get_busy_gpu_ids(batches, node_name)
        present_gpus = self._get_present_gpus(node_name)

        return [gpu for gpu in present_gpus if gpu.device_id not in busy_gpu_ids]

    def _get_cluster_state(self):
        """
        Returns a list of complete nodes, which are currently present in the cluster.
        """
        cursor = self._mongo.db['nodes'].find(
            {},
            {'state': 1, 'ram': 1, 'nodeName': 1}
        )

        nodes = list(cursor)
        node_names = [node['nodeName'] for node in nodes]

        cursor = self._mongo.db['batches'].find(
            {
                'node': {'$in': node_names},
                'state': {'$in': ['scheduled', 'processing']}},
            {'experimentId': 1, 'node': 1, 'usedGPUs': 1}
        )
        batches = list(cursor)
        experiment_ids = list(set([ObjectId(b['experimentId']) for b in batches]))

        cursor = self._mongo.db['experiments'].find(
            {'_id': {'$in': experiment_ids}},
            {'container.settings.ram': 1}
        )
        experiments = {str(e['_id']): e for e in cursor}

        complete_nodes = []

        for node in nodes:
            node_name = node['nodeName']
            node_batches = list(filter(lambda batch: batch['node'] == node_name, batches))

            num_batches = len(node_batches)

            used_ram = sum([
                experiments[b['experimentId']]['container']['settings']['ram']
                for b in node_batches
            ])

            available_gpus = self._get_available_gpus(node, batches)

            online = node['state'] == 'online'

            complete_node = CompleteNode(
                node_name=node_name,
                online=online,
                ram=node['ram'],
                gpus=self._get_present_gpus(node['nodeName']),
                ram_available=node['ram'] - used_ram,
                gpus_available=available_gpus,
                num_batches_running=num_batches,
            )

            complete_nodes.append(complete_node)

        return complete_nodes

    @staticmethod
    def _node_sufficient(node, experiment):
        """
        Returns True if the nodes hardware is sufficient for the experiment

        :param node: The node to test
        :param experiment: A dictionary containing hardware requirements for the experiment
        :return: True, if the nodes hardware is sufficient for the experiment, otherwise False
        """

        if not node.online:
            return False

        if node.ram_available < experiment['container']['settings']['ram']:
            return False

        # check gpus
        gpu_requirements = get_gpu_requirements(experiment['container']['settings'].get('gpus'))

        try:
            _gpus = match_gpus(node.gpus_available, gpu_requirements)
        except InsufficientGPUError:
            return False

        return True

    @staticmethod
    def _node_possibly_sufficient(node, experiment):
        """
        Returns True if the node could be sufficient for the experiment, even if the node does not have
        sufficient hardware at the moment (because of running batches).
        :param node: The node to check
        :param experiment: The experiment for which the node is sufficient or not.
        :return: True, if the node is possibly sufficient otherwise False
        """
        if node.ram < experiment['container']['settings']['ram']:
            return False
        
        gpu_requirements = get_gpu_requirements(experiment['container']['settings'].get('gpus'))

        try:
            match_gpus(node.gpus, gpu_requirements)
        except InsufficientGPUError:
            return False
        return True

    @staticmethod
    def _check_nodes_possibly_sufficient(nodes, experiment):
        """
        Returns True if a possibly sufficient node is found otherwise False
        :param nodes: The nodes to check
        :type nodes: List[CompleteNode]
        :param experiment: The description of the experiment
        :return: True if a possibly sufficient node is found otherwise False
        """
        for node in nodes:
            if Scheduler._node_possibly_sufficient(node, experiment):
                return True
        return False

    @staticmethod
    def _get_best_node(nodes, experiment):
        """
        Returns the node, that fits best for the given experiment. If no node could be found returns None
        :param nodes: The nodes, that are available for this experiment.
        :param experiment: The description of the experiment
        :return: The node that fits best for the given experiment. If no node fits at the moment None is returned.
        :rtype: CompleteNode
        """
        # check sufficient nodes
        sufficient_nodes = [node for node in nodes if Scheduler._node_sufficient(node, experiment)]
        if not sufficient_nodes:
            return None

        # prefer nodes without GPUs
        nodes_without_gpus = [node for node in sufficient_nodes if (not node.gpus)]
        if nodes_without_gpus:
            sufficient_nodes = nodes_without_gpus

        # prefer nodes with few jobs
        min_num_batches = None
        nodes_with_few_batches = []
        for node in sufficient_nodes:
            if min_num_batches is None:
                min_num_batches = node.num_batches_running
                nodes_with_few_batches.append(node)
                continue

            if node.num_batches_running < min_num_batches:
                min_num_batches = node.num_batches_running
                nodes_with_few_batches = [node]
            elif node.num_batches_running == min_num_batches:
                nodes_with_few_batches.append(node)

        # prefer nodes with less free ram
        nodes_with_few_batches.sort(reverse=False, key=lambda n: n.ram_available)

        return nodes_with_few_batches[0]

    def _schedule_batches(self):
        """
        state before _schedule_batches:
        There might be batches with state "registered" (given in _fifo()).
        There might be nodes, that are online and capable of processing the given batches (given in _online_nodes()).

        state after _schedule_batches:
        ClientProxies for which a batch is scheduled have a 'check_for_batches' action in their queue.
        Batches that are scheduled have state "scheduled" now and the node property of these batches is filled.
        """
        # list of tuple(batch_id, node_name) with node_names to which the batches were scheduled
        scheduled_nodes = []
        cluster_nodes = self._get_cluster_state()

        # select batch to be scheduled
        for next_batch in self._fifo():
            node_name = self._schedule_batch(next_batch, cluster_nodes)

            if node_name is not None:
                cluster_nodes = self._get_cluster_state()
                scheduled_nodes.append((next_batch['_id'], node_name))

        # ClientProxies clean up
        for cluster_node in cluster_nodes:
            node_name = cluster_node.node_name
            client_proxy = self._nodes[node_name]

            if not client_proxy.put_action({'action': 'clean_up'}):
                continue

        # inform ClientProxies about new batches
        for batch_id, node_name in scheduled_nodes:
            client_proxy = self._nodes[node_name]
            check_for_batches_data = {
                'action': 'check_for_batches'
            }

            if not client_proxy.put_action(check_for_batches_data):
                debug_info = 'Could not reach docker client proxy for node "{}" during scheduling.'.format(
                    node_name
                )
                batch_failure(
                    self._mongo,
                    batch_id,
                    debug_info,
                    None,
                    self._conf
                )

    def _schedule_batch(self, next_batch, nodes):
        """
        Tries to find a node that is capable of processing the given batch. If no capable node could be found, None is
        returned.
        If a node was found, that is capable of processing the given batch, this node is written to the node property of
        the batch. The batches state is then updated to 'scheduled'.

        :param next_batch: The batch to schedule.
        :param nodes: The nodes on which the batch should be scheduled.
        :return: The name of the node on which the given batch is scheduled
        If the batch could not be scheduled None is returned
        :raise TrusteeServiceError: If the trustee service is unavailable.
        """
        batch_id = str(next_batch['_id'])
        experiment_id = next_batch['experimentId']

        try:
            experiment = self._get_experiment_of_batch(experiment_id)
        except Exception as e:
            batch_failure(
                self._mongo,
                batch_id,
                repr(e),
                None,
                self._conf,
                disable_retry_if_failed=True
            )
            return None

        ram = experiment['container']['settings']['ram']

        # limit the number of currently executed batches from a single experiment
        concurrency_limit = experiment.get('execution', {}).get('settings', {}).get('batchConcurrencyLimit', 64)
        batch_count = self._mongo.db['batches'].count({
            'experimentId': experiment_id,
            'state': {'$in': ['scheduled', 'processing']}
        })

        if batch_count >= concurrency_limit:
            return None

        # check impossible experiments
        if not Scheduler._check_nodes_possibly_sufficient(nodes, experiment):
            debug_info = 'There are no nodes configured that are possibly sufficient for experiment "{}"' \
                .format(next_batch['experimentId'])
            batch_failure(self._mongo, batch_id, debug_info, None, self._conf, disable_retry_if_failed=True)
            return None

        # select node
        selected_node = Scheduler._get_best_node(nodes, experiment)

        if selected_node is None:
            return None

        # calculate ram / gpus
        selected_node.ram_available -= ram

        used_gpu_ids = None
        if selected_node.gpus_available:
            gpu_requirements = get_gpu_requirements(experiment['container']['settings'].get('gpus'))
            available_gpus = selected_node.gpus_available
            used_gpus = match_gpus(available_gpus, requirements=gpu_requirements)

            used_gpu_ids = []
            for gpu in used_gpus:
                used_gpu_ids.append(gpu.device_id)
                available_gpus.remove(gpu)

        # check mounting
        mount_connectors = red_get_mount_connectors_from_inputs(next_batch['inputs'])
        is_mounting = bool(mount_connectors)

        allow_insecure_capabilities = self._conf.d['controller']['docker'].get('allow_insecure_capabilities', False)

        if not allow_insecure_capabilities and is_mounting:
            # set state to failed, because insecure_capabilities are not allowed but needed, by this batch.
            debug_info = 'FUSE support for this agency is disabled, but the following input/output-keys are ' \
                         'configured to mount inside a docker container.{}{}'.format(os.linesep, mount_connectors)
            batch_failure(
                self._mongo,
                batch_id,
                debug_info,
                None,
                self._conf,
                disable_retry_if_failed=True
            )
            return None

        # update batch data
        self._mongo.db['batches'].update_one(
            {'_id': next_batch['_id']},
            {
                '$set': {
                    'state': 'scheduled',
                    'node': selected_node.node_name,
                    'usedGPUs': used_gpu_ids,
                    'mount': is_mounting
                },
                '$push': {
                    'history': {
                        'state': 'scheduled',
                        'time': time(),
                        'debugInfo': None,
                        'node': selected_node.node_name,
                        'ccagent': None
                    }
                },
                '$inc': {
                    'attempts': 1
                }
            }
        )

        return selected_node.node_name

    def _get_experiment_of_batch(self, experiment_id):
        """
        Returns the experiment of the given experiment_id with filled secrets.
        :param experiment_id: The experiment id to resolve.
        :return: The experiment as dictionary with filled template values.
        """
        experiment = self._mongo.db['experiments'].find_one(
            {'_id': ObjectId(experiment_id)},
            {'container.settings': 1, 'execution.settings': 1}
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

    def _fifo(self):
        cursor = self._mongo.db['batches'].aggregate([
            {'$match': {'state': 'registered'}},
            {'$sort': {'registrationTime': 1}},
            {'$project': {'experimentId': 1, 'inputs': 1, 'outputs': 1}}
        ])
        for b in cursor:
            yield b


class InsufficientNodesException(Exception):
    pass
