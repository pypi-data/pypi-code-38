from kubernetes import client, config, watch
import logging

RESTART_POLICY = "Never"


class AccessModes(object):
    READ_WRITE_MANY = "ReadWriteMany"
    READ_WRITE_ONCE = "ReadWriteOnce"
    READ_ONLY_MANY = "ReadOnlyMany"


class JobConditionType(object):
    COMPLETE = "Complete"
    FAILED = "Failed"


class EventTypes(object):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    ERROR = "ERROR"


class ItemNotFoundException(Exception):
    pass


class ClusterApi(object):
    def __init__(self, host, token, namespace, verify_ssl=True):
        configuration = client.Configuration()
        configuration.host = host
        configuration.api_key = {"authorization": "Bearer " + token}
        configuration.verify_ssl = verify_ssl
        self.api_client = client.ApiClient(configuration)
        self.core = client.CoreV1Api(self.api_client)
        self.batch = client.BatchV1Api(self.api_client)
        self.namespace = namespace

    def create_persistent_volume_claim(self, name, storage_size_in_g, storage_class_name,
                                       access_modes=[AccessModes.READ_WRITE_MANY],
                                       labels={}):
        pvc = client.V1PersistentVolumeClaim()
        pvc.metadata = client.V1ObjectMeta(name=name, labels=labels)
        storage_size = "{}Gi".format(storage_size_in_g)
        resources = client.V1ResourceRequirements(requests={"storage": storage_size})
        pvc.spec = client.V1PersistentVolumeClaimSpec(access_modes=access_modes,
                                                      resources=resources,
                                                      storage_class_name=storage_class_name)
        return self.core.create_namespaced_persistent_volume_claim(self.namespace, pvc)

    def delete_persistent_volume_claim(self, name):
        self.core.delete_namespaced_persistent_volume_claim(name, self.namespace, client.V1DeleteOptions())

    def create_secret(self, name, string_value_dict, labels={}):
        body = client.V1Secret(string_data=string_value_dict,
                               metadata=client.V1ObjectMeta(name=name, labels=labels))
        return self.core.create_namespaced_secret(namespace=self.namespace, body=body)

    def delete_secret(self, name):
        self.core.delete_namespaced_secret(name, self.namespace, body=client.V1DeleteOptions())

    def create_job(self, name, batch_job_spec, labels={}):
        body = client.V1Job(
            metadata=client.V1ObjectMeta(name=name, labels=labels),
            spec=batch_job_spec.create())
        return self.batch.create_namespaced_job(self.namespace, body)

    def wait_for_job_events(self, callback, label_selector=None):
        """
        Run callback for job events that match the specified label selector and event types.
        This function will loop forever unless an exception is raised by the callback.
        :param callback: function: receives single parameter of the event: dict with 'type' and 'object' keys
        :param label_selector: label to filter by
        """
        w = watch.Watch()
        for event in w.stream(self.batch.list_namespaced_job, self.namespace, label_selector=label_selector):
            callback(event)

    def delete_job(self, name, propagation_policy='Background'):
        body = client.V1DeleteOptions(propagation_policy=propagation_policy)
        self.batch.delete_namespaced_job(name, self.namespace, body=body)

    def create_config_map(self, name, data, labels={}):
        body = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name=name, labels=labels),
            data=data
        )
        return self.core.create_namespaced_config_map(self.namespace, body)

    def delete_config_map(self, name):
        self.core.delete_namespaced_config_map(name, self.namespace, body=client.V1DeleteOptions())

    def read_pod_logs(self, name):
        # The read_namespaced_pod_log method by default performs some formatting on the data
        # This can cause double quotes to change to single quotes and other unexpected formatting.
        # So instead we are using the _preload_content flag and calling read() based on the following comment:
        # https://github.com/kubernetes/kubernetes/issues/37881#issuecomment-264366664
        # This changes the returned value so we must add an additional call to read()
        stream = self.core.read_namespaced_pod_log(name, self.namespace, _preload_content=False)
        return stream.read().decode("utf-8")

    def list_pods(self, label_selector):
        return self.core.list_namespaced_pod(self.namespace, label_selector=label_selector).items

    def list_persistent_volume_claims(self, label_selector=None):
        return self.core.list_namespaced_persistent_volume_claim(self.namespace, label_selector=label_selector).items

    def list_jobs(self, label_selector):
        return self.batch.list_namespaced_job(self.namespace, label_selector=label_selector).items

    def list_config_maps(self, label_selector):
        return self.core.list_namespaced_config_map(self.namespace, label_selector=label_selector).items

    def read_job_logs(self, job_name):
        """
        Reads logs from the most recent pod created by the specified job.
        Raises ItemNotFoundException when no pod is found with the job-name label selector.
        :param job_name: str: name of the job we want to read logs for
        :return: str: logs
        """
        pod = self.get_most_recent_pod_for_job(job_name)
        return self.read_pod_logs(pod.metadata.name)

    def get_most_recent_pod_for_job(self, job_name):
        """
        Find the most recent pod created by a job
        :param job_name: name of the job
        :return: V1Pod
        """
        pods = self.list_pods(label_selector="job-name={}".format(job_name))
        if not pods:
            raise ItemNotFoundException("No pods found with job name {}.".format(job_name))
        sorted_pods = sorted(pods, key=lambda pod: pod.metadata.creation_timestamp)
        return sorted_pods[-1]


class Container(object):
    def __init__(self, name, image_name, command, args=[], working_dir=None, env_dict={},
                 requested_cpu=None, requested_memory=None, volumes=[]):
        self.name = name
        self.image_name = image_name
        self.command = command
        self.args = args
        self.working_dir = working_dir
        self.env_dict = env_dict
        self.requested_cpu = requested_cpu
        self.requested_memory = requested_memory
        self.volumes = volumes

    def create_env(self):
        environment_variables = []
        for key, value in self.env_dict.items():
            if isinstance(value, EnvVarSource):
                environment_variables.append(client.V1EnvVar(name=key, value_from=value.create_env_var_source()))
            else:
                environment_variables.append(client.V1EnvVar(name=key, value=value))
        return environment_variables

    def create_volume_mounts(self):
        return [volume.create_volume_mount() for volume in self.volumes]

    def create_volumes(self):
        return [volume.create_volume() for volume in self.volumes]

    def create_resource_requirements(self):
        return client.V1ResourceRequirements(
            requests={
                "memory": self.requested_memory,
                "cpu": self.requested_cpu
            })

    def create(self):
        return client.V1Container(
            name=self.name,
            image=self.image_name,
            working_dir=self.working_dir,
            command=self.command,
            args=self.args,
            resources=self.create_resource_requirements(),
            env=self.create_env(),
            volume_mounts=self.create_volume_mounts()
        )


class EnvVarSource(object):
    def create_env_var_source(self):
        raise NotImplementedError("Subclasses of EnvVarSource should implement create_env_var_source.")


class SecretEnvVar(EnvVarSource):
    def __init__(self, name, key):
        self.name = name
        self.key = key

    def create_env_var_source(self):
        return client.V1EnvVarSource(
            secret_key_ref=client.V1SecretKeySelector(
                key=self.key,
                name=self.name
            )
        )


class FieldRefEnvVar(EnvVarSource):
    def __init__(self, field_path):
        self.field_path = field_path

    def create_env_var_source(self):
        return client.V1EnvVarSource(
            field_ref=client.V1ObjectFieldSelector(field_path=self.field_path)
        )


class VolumeBase(object):
    """
    Base class that represents a volume that will be mounted.
    """
    def __init__(self, name, mount_path):
        self.name = name
        self.mount_path = mount_path

    def create_volume_mount(self):
        return client.V1VolumeMount(
            name=self.name,
            mount_path=self.mount_path)

    def create_volume(self):
        raise NotImplementedError("Subclasses of VolumeBase should implement create_volume.")


class SecretVolume(VolumeBase):
    def __init__(self, name, mount_path, secret_name):
        super(SecretVolume, self).__init__(name, mount_path)
        self.secret_name = secret_name

    def create_volume(self):
        return client.V1Volume(
                name=self.name,
                secret=self.create_secret())

    def create_secret(self):
        return client.V1SecretVolumeSource(secret_name=self.secret_name)


class PersistentClaimVolume(VolumeBase):
    def __init__(self, name, mount_path, volume_claim_name, read_only=False):
        super(PersistentClaimVolume, self).__init__(name, mount_path)
        self.volume_claim_name = volume_claim_name
        self.read_only = read_only

    def create_volume(self):
        return client.V1Volume(
            name=self.name,
            persistent_volume_claim=self.create_volume_source())

    def create_volume_source(self):
        return client.V1PersistentVolumeClaimVolumeSource(
            claim_name=self.volume_claim_name,
            read_only=self.read_only)


class ConfigMapVolume(VolumeBase):
    def __init__(self, name, mount_path, config_map_name, source_key, source_path):
        super(ConfigMapVolume, self).__init__(name, mount_path)
        self.config_map_name = config_map_name
        self.source_key = source_key
        self.source_path = source_path

    def create_volume(self):
        return client.V1Volume(
            name=self.name,
            config_map=self.create_config_map())

    def create_config_map(self):
        items = [client.V1KeyToPath(key=self.source_key, path=self.source_path)]
        return client.V1ConfigMapVolumeSource(name=self.config_map_name,
                                              items=items)


class EmptyDirVolume(VolumeBase):
    def __init__(self, name, mount_path):
        super(EmptyDirVolume, self).__init__(name, mount_path)

    def create_volume(self):
        return client.V1Volume(
                name=self.name,
                empty_dir=client.V1EmptyDirVolumeSource())


class BatchJobSpec(object):
    def __init__(self, name, container, service_account_name=None, labels={}):
        self.name = name
        self.pod_restart_policy = RESTART_POLICY
        self.container = container
        self.service_account_name = service_account_name
        self.labels = labels

    def create(self):
        job_spec_name = "{}spec".format(self.name)
        return client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(name=job_spec_name, labels=self.labels),
                spec=self.create_pod_spec()
            )
        )

    def create_pod_spec(self):
        return client.V1PodSpec(
            containers=self.create_containers(),
            volumes=self.create_volumes(),
            restart_policy=RESTART_POLICY,
            service_account_name=self.service_account_name,
        )

    def create_containers(self):
        return [self.container.create()]

    def create_volumes(self):
        return self.container.create_volumes()
