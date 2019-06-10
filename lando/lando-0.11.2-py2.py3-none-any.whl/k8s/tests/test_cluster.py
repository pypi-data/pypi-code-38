from unittest import TestCase
from unittest.mock import patch, Mock, call
from lando.k8s.cluster import ClusterApi, AccessModes, Container, SecretVolume, SecretEnvVar, EnvVarSource, \
    FieldRefEnvVar, VolumeBase, SecretVolume, PersistentClaimVolume, ConfigMapVolume, BatchJobSpec, \
    ItemNotFoundException
from kubernetes import client
from dateutil.parser import parse


class TestClusterApi(TestCase):
    def setUp(self):
        self.cluster_api = ClusterApi(host='somehost', token='myToken', namespace='lando-job-runner', verify_ssl=False)
        self.mock_core_api = Mock()
        self.mock_batch_api = Mock()
        self.cluster_api.core = self.mock_core_api
        self.cluster_api.batch = self.mock_batch_api

    def test_constructor(self):
        configuration = self.cluster_api.api_client.configuration
        self.assertEqual(configuration.host, 'somehost')
        self.assertEqual(configuration.api_key, {"authorization": "Bearer myToken"})
        self.assertEqual(configuration.verify_ssl, False)

    def test_create_persistent_volume_claim(self):
        resp = self.cluster_api.create_persistent_volume_claim(name='myvolume', storage_size_in_g=2,
                                                               storage_class_name='gluster',
                                                               labels={"bespin": "true"})
        self.assertEqual(resp, self.mock_core_api.create_namespaced_persistent_volume_claim.return_value)
        args, kwargs = self.mock_core_api.create_namespaced_persistent_volume_claim.call_args
        namespace = args[0]
        self.assertEqual(namespace, 'lando-job-runner')
        pvc = args[1]
        self.assertEqual(pvc.metadata.name, 'myvolume')
        self.assertEqual(pvc.metadata.labels, {"bespin": "true"})
        self.assertEqual(pvc.spec.access_modes, [AccessModes.READ_WRITE_MANY])
        self.assertEqual(pvc.spec.resources.requests, {'storage': '2Gi'})
        self.assertEqual(pvc.spec.storage_class_name, 'gluster')

    def test_create_persistent_volume_claim_custom_access_mode(self):
        resp = self.cluster_api.create_persistent_volume_claim(name='myvolume', storage_size_in_g=2,
                                                               storage_class_name='gluster',
                                                               access_modes=[AccessModes.READ_WRITE_ONCE])
        self.assertEqual(resp, self.mock_core_api.create_namespaced_persistent_volume_claim.return_value)
        args, kwargs = self.mock_core_api.create_namespaced_persistent_volume_claim.call_args
        pvc = args[1]
        self.assertEqual(pvc.spec.access_modes, [AccessModes.READ_WRITE_ONCE])

    def test_delete_persistent_volume_claim(self):
        self.cluster_api.delete_persistent_volume_claim(name='myvolume')
        self.mock_core_api.delete_namespaced_persistent_volume_claim.assert_called_with(
            'myvolume', 'lando-job-runner', client.V1DeleteOptions()
        )

    def test_create_secret(self):
        resp = self.cluster_api.create_secret(name='mysecret', string_value_dict={
            'password': 's3cr3t'
        }, labels={"bespin": "true"})
        self.assertEqual(resp, self.mock_core_api.create_namespaced_secret.return_value)
        args, kwargs = self.mock_core_api.create_namespaced_secret.call_args
        self.assertEqual(kwargs['namespace'], 'lando-job-runner')
        self.assertEqual(kwargs['body'].metadata.name, 'mysecret')
        self.assertEqual(kwargs['body'].metadata.labels, {"bespin": "true"})
        self.assertEqual(kwargs['body'].string_data, {'password': 's3cr3t'})

    def test_delete_secret(self):
        self.cluster_api.delete_secret(name='mysecret')
        self.mock_core_api.delete_namespaced_secret.assert_called_with(
            'mysecret', 'lando-job-runner', body=client.V1DeleteOptions()
        )

    def test_create_job(self):
        mock_batch_job_spec = Mock()
        resp = self.cluster_api.create_job(name='myjob',
                                           batch_job_spec=mock_batch_job_spec,
                                           labels={"bespin": "true"})

        self.assertEqual(resp, self.mock_batch_api.create_namespaced_job.return_value)
        args, kwargs = self.mock_batch_api.create_namespaced_job.call_args
        self.assertEqual(args[0], 'lando-job-runner')
        self.assertEqual(args[1].metadata.name, 'myjob')
        self.assertEqual(args[1].metadata.labels, {"bespin": "true"})
        self.assertEqual(args[1].spec, mock_batch_job_spec.create.return_value)

    @patch('lando.k8s.cluster.watch')
    def test_wait_for_job_events(self, mock_watch):
        callback = Mock()
        mock_watch.Watch.return_value.stream.return_value = [
            {'object': 'job1', 'type': 'ADDED'},
            {'object': 'job2', 'type': 'ADDED'},
        ]
        self.cluster_api.wait_for_job_events(callback)
        callback.assert_has_calls([
            call({'object': 'job1', 'type': 'ADDED'}),
            call({'object': 'job2', 'type': 'ADDED'}),
        ])
        args, kwargs = mock_watch.Watch.return_value.stream.call_args
        self.assertEqual(args[1], 'lando-job-runner')
        self.assertEqual(kwargs['label_selector'], None)

    @patch('lando.k8s.cluster.watch')
    def test_wait_for_job_events_with_label_selector(self, mock_watch):
        callback = Mock()
        mock_watch.Watch.return_value.stream.return_value = []
        self.cluster_api.wait_for_job_events(Mock(), label_selector='name=mypod')
        args, kwargs = mock_watch.Watch.return_value.stream.call_args
        self.assertEqual(args[1], 'lando-job-runner')
        self.assertEqual(kwargs['label_selector'], 'name=mypod')

    def test_delete_job(self):
        self.cluster_api.delete_job(name='myjob')
        args, kwargs = self.mock_batch_api.delete_namespaced_job.call_args
        self.assertEqual(args[0], 'myjob')
        self.assertEqual(args[1], 'lando-job-runner')
        self.assertEqual(kwargs['body'].propagation_policy, 'Background')

    def test_delete_job_custom_propogation_policy(self):
        self.cluster_api.delete_job(name='myjob', propagation_policy='Foreground')
        args, kwargs = self.mock_batch_api.delete_namespaced_job.call_args
        self.assertEqual(kwargs['body'].propagation_policy, 'Foreground')

    def test_create_config_map(self):
        resp = self.cluster_api.create_config_map(name='myconfig',
                                                  data={'threads': 2},
                                                  labels={"bespin": "true"})

        self.assertEqual(resp, self.mock_core_api.create_namespaced_config_map.return_value)
        args, kwargs = self.mock_core_api.create_namespaced_config_map.call_args
        self.assertEqual(args[0], 'lando-job-runner')
        self.assertEqual(args[1].metadata.name, 'myconfig')
        self.assertEqual(args[1].metadata.labels, {"bespin": "true"})
        self.assertEqual(args[1].data, {'threads': 2})

    def test_delete_config_map(self):
        self.cluster_api.delete_config_map(name='myconfig')
        args, kwargs = self.mock_core_api.delete_namespaced_config_map.call_args
        self.assertEqual(args[0], 'myconfig')
        self.assertEqual(args[1], 'lando-job-runner')

    def test_read_pod_logs(self):
        # Added _preload_content argument to allow fetching actual text instead of parsed
        # based on https://github.com/kubernetes/kubernetes/issues/37881#issuecomment-264366664
        resp = self.cluster_api.read_pod_logs('mypod')
        log_stream = self.mock_core_api.read_namespaced_pod_log.return_value
        self.assertEqual(resp, log_stream.read.return_value.decode.return_value)
        log_stream.read.return_value.decode.assert_called_with('utf-8')
        self.mock_core_api.read_namespaced_pod_log.assert_called_with('mypod', 'lando-job-runner',
                                                                      _preload_content=False)

    def test_list_pods(self):
        resp = self.cluster_api.list_pods(label_selector='bespin=true')
        self.mock_core_api.list_namespaced_pod.assert_called_with(
            'lando-job-runner', label_selector='bespin=true'
        )
        mock_pod_list = self.mock_core_api.list_namespaced_pod.return_value
        self.assertEqual(resp, mock_pod_list.items)

    def test_list_persistent_volume_claims(self):
        resp = self.cluster_api.list_persistent_volume_claims(label_selector='bespin=true')
        self.mock_core_api.list_namespaced_persistent_volume_claim.assert_called_with(
            'lando-job-runner', label_selector='bespin=true'
        )
        mock_pvc_list = self.mock_core_api.list_namespaced_persistent_volume_claim.return_value
        self.assertEqual(resp, mock_pvc_list.items)

    def test_list_jobs(self):
        resp = self.cluster_api.list_jobs(label_selector='bespin=true')
        self.mock_batch_api.list_namespaced_job.assert_called_with(
            'lando-job-runner', label_selector='bespin=true'
        )
        mock_job_list = self.mock_batch_api.list_namespaced_job.return_value
        self.assertEqual(resp, mock_job_list.items)

    def test_list_config_maps(self):
        resp = self.cluster_api.list_config_maps(label_selector='bespin=true')
        self.mock_core_api.list_namespaced_config_map.assert_called_with(
            'lando-job-runner', label_selector='bespin=true'
        )
        mock_config_map_list = self.mock_core_api.list_namespaced_config_map.return_value
        self.assertEqual(resp, mock_config_map_list.items)

    def test_read_job_logs(self):
        mock_pod = Mock()
        mock_pod.metadata.name = 'myjob-abcd'
        self.cluster_api.get_most_recent_pod_for_job = Mock()
        self.cluster_api.get_most_recent_pod_for_job.return_value = mock_pod
        self.cluster_api.read_pod_logs = Mock()
        logs = self.cluster_api.read_job_logs('myjob')
        self.assertEqual(logs, self.cluster_api.read_pod_logs.return_value)
        self.cluster_api.get_most_recent_pod_for_job.assert_called_with('myjob')
        self.cluster_api.read_pod_logs.assert_called_with('myjob-abcd')

    def test_get_most_recent_pod_for_job_name__no_pods_found(self):
        self.cluster_api.list_pods = Mock()
        self.cluster_api.list_pods.return_value = []
        with self.assertRaises(ItemNotFoundException) as raised_exception:
            self.cluster_api.get_most_recent_pod_for_job('myjob')
        self.assertEqual(str(raised_exception.exception), 'No pods found with job name myjob.')

    def test_get_most_recent_pod_for_job_name__finds_pod(self):
        pod1 = Mock()
        pod1.metadata.creation_timestamp = parse("2012-01-01 12:30:00")
        pod2 = Mock()
        pod2.metadata.creation_timestamp = parse("2012-01-01 12:50:00")
        pod3 = Mock()
        pod3.metadata.creation_timestamp = parse("2012-01-01 12:40:00")
        self.cluster_api.list_pods = Mock()
        self.cluster_api.list_pods.return_value = [
            pod1, pod2, pod3
        ]
        pod = self.cluster_api.get_most_recent_pod_for_job('myjob')
        self.assertEqual(pod, pod2)

class TestContainer(TestCase):
    def test_minimal_create(self):
        container = Container(
            name='mycontainer', image_name='someimage', command=['wc', '-l']
        )
        container_dict = container.create().to_dict()

        self.assertEqual(container_dict['name'], 'mycontainer')
        self.assertEqual(container_dict['image'], 'someimage')
        self.assertEqual(container_dict['command'], ['wc', '-l'])
        self.assertEqual(container_dict['args'], [])

    def test_full_create(self):
        container = Container(
            name='mycontainer2',
            image_name='someimage',
            command=['wc'],
            args=['-l'],
            working_dir='/tmp/data',
            env_dict={
                'SOMEENV': 'SomeVal'
            },
            requested_cpu='2',
            requested_memory='200M',
            volumes=[
                SecretVolume(name='mymountedvolume', mount_path='/secret', secret_name='mysecret')
            ]
        )
        container_dict = container.create().to_dict()
        expected_container_dict = {
            'name': 'mycontainer2',
            'image': 'someimage',
            'image_pull_policy': None,
            'command': ['wc'],
            'args': ['-l'],
            'working_dir': '/tmp/data',
            'env': [
                {
                    'name': 'SOMEENV',
                    'value': 'SomeVal',
                    'value_from': None
                }
            ],
            'env_from': None,
            'resources': {
                'limits': None,
                'requests': {
                    'cpu': '2',
                    'memory': '200M'
                }
            },
            'volume_mounts': [
                {
                    'mount_path': '/secret',
                    'mount_propagation': None,
                    'name': 'mymountedvolume',
                    'read_only': None,
                    'sub_path': None
                }
            ],
            'lifecycle': None,
            'liveness_probe': None,
            'ports': None,
            'readiness_probe': None,
            'security_context': None,
            'stdin': None,
            'stdin_once': None,
            'termination_message_path': None,
            'termination_message_policy': None,
            'tty': None,
            'volume_devices': None, }
        self.assertEqual(container_dict, expected_container_dict)

    def test_create_env(self):
        container = Container(
            name='mycontainer', image_name='someimage', command=['wc', '-l'],
            env_dict={
                'USERNAME': 'joe',
                'PASSWORD': SecretEnvVar(name='mysecret', key='username')
            }
        )
        env = container.create_env()
        self.assertEqual(len(env), 2)

        self.assertEqual(env[0].name, 'USERNAME')
        self.assertEqual(env[0].value, 'joe')
        self.assertEqual(env[0].value_from, None)

        self.assertEqual(env[1].name, 'PASSWORD')
        self.assertEqual(env[1].value, None)
        self.assertEqual(env[1].value_from.to_dict()['secret_key_ref'],
                         {'key': 'username', 'name': 'mysecret', 'optional': None})

    def test_create_resource_requirements(self):
        container = Container(
            name='mycontainer', image_name='someimage', command=['wc', '-l'],
            requested_memory='200M', requested_cpu=4,
        )
        requirements = container.create_resource_requirements()
        expected_requirements = {
            'limits': None,
            'requests': {
                'cpu': 4,
                'memory': '200M'
            }
        }
        self.assertEqual(requirements.to_dict(), expected_requirements)


class TestEnvVarSource(TestCase):
    def test_create_env_var_source_is_required(self):
        with self.assertRaises(NotImplementedError):
            EnvVarSource().create_env_var_source()


class TestSecretEnvVar(TestCase):
    def test_create_env_var_source(self):
        env_var = SecretEnvVar(name='mysecret', key='mykey')
        env_var_source_dict = env_var.create_env_var_source().to_dict()
        self.assertEqual(env_var_source_dict['secret_key_ref'],
                         {'key': 'mykey', 'name': 'mysecret', 'optional': None})


class TestFieldRefEnvVar(TestCase):
    def test_create_env_var_source(self):
        env_var = FieldRefEnvVar(field_path='metadata.name')
        env_var_source_dict = env_var.create_env_var_source().to_dict()
        self.assertEqual(env_var_source_dict['field_ref'],
                         {'api_version': None, 'field_path': 'metadata.name'})


class TestVolumeBase(TestCase):
    def test_create_volume_mount(self):
        volume = VolumeBase(name='myvolume', mount_path='/data')
        volume_dict = volume.create_volume_mount().to_dict()
        self.assertEqual(volume_dict, {
            'mount_path': '/data',
            'mount_propagation': None,
            'name': 'myvolume',
            'read_only': None,
            'sub_path': None
        })

    def test_create_volume_is_required(self):
        volume = VolumeBase(name='myvolume', mount_path='/data')
        with self.assertRaises(NotImplementedError):
            volume.create_volume()


class TestSecretVolume(TestCase):
    def test_create_volume(self):
        volume = SecretVolume(name='myvolume', mount_path='/data2', secret_name='mysecret')
        volume_dict = volume.create_volume().to_dict()
        self.assertEqual(volume_dict['secret']['secret_name'], 'mysecret')


class TestPersistentClaimVolume(TestCase):
    def test_create_volume(self):
        volume = PersistentClaimVolume(name='myvolume', mount_path='/data3', volume_claim_name='mypvc')
        volume_dict = volume.create_volume().to_dict()
        self.assertEqual(volume_dict['persistent_volume_claim'],
                         {'claim_name': 'mypvc', 'read_only': False})


class TestConfigMapVolume(TestCase):
    def test_create_volume(self):
        volume = ConfigMapVolume(name='myvolume', mount_path='/data/config.dat',
                                 config_map_name='myconfig', source_key='datastore', source_path='config')
        volume_dict = volume.create_volume().to_dict()
        expected_dict = {
            'default_mode': None,
            'items': [{'key': 'datastore', 'mode': None, 'path': 'config'}],
            'name': 'myconfig',
            'optional': None
        }
        self.assertEqual(volume_dict['config_map'], expected_dict)


class TestBatchJobSpec(TestCase):
    def test_create(self):
        container = Container(
            name='mycontainer', image_name='someimage', command=['wc', '-l']
        )
        spec = BatchJobSpec(name='mybatch', container=container, labels={'service': 'bespin'})
        spec_dict = spec.create().to_dict()
        self.assertEqual(spec_dict['template']['metadata']['name'], 'mybatchspec')
        self.assertEqual(spec_dict['template']['spec']['containers'], [container.create().to_dict()])

    def test_create_with_service_account_name(self):
        container = Container(
            name='mycontainer', image_name='someimage', command=['wc', '-l']
        )
        spec = BatchJobSpec(name='mybatch', container=container,
                            labels={'service': 'bespin'},
                            service_account_name='sa-name')
        spec_dict = spec.create().to_dict()
        self.assertEqual(spec_dict['template']['metadata']['name'], 'mybatchspec')
        self.assertEqual(spec_dict['template']['spec']['containers'], [container.create().to_dict()])
        self.assertEqual(spec_dict['template']['spec']['service_account_name'], 'sa-name')
