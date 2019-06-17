class Logger(object):

    def create_logger(self, project_id, service_name):
        from google.cloud import logging
        log_client = logging.Client(project=project_id)
        logger = log_client.logger(service_name)
        return logger

    def get_instance(self):
        import socket
        gce_name = socket.gethostname()
        return gce_name

    def __init__(self, service_name=None, run_id=None, project_id=None, local_run=False, module_id=None, version_id=None, function_name=None, cluster_name=None, namespace_name=None, container_name=None, location=None, revision_version=None, resource_type='global'):
        self.service_name = service_name
        self.trace_id = run_id
        self.project_id = project_id
        self.module_id = module_id
        self.version_id = version_id
        self.resource_type = resource_type
        self.function_name = function_name
        self.cluster_name = cluster_name
        self.namespace_name = namespace_name
        self.container_name = container_name
        self.location = location
        self.local_run = local_run
        self.revision_version = revision_version

        if local_run is False:
            from google.cloud.logging.resource import Resource
            # Check resource_type
            if self.resource_type == 'gae_app':
                self.res = Resource(type=self.resource_type, labels={
                    "project_id": self.project_id,
                    "module_id": self.module_id,
                    "version_id": self.version_id
                })
            elif self.resource_type == 'cloud_function':
                self.res = Resource(type=self.resource_type, labels={
                    "function_name": self.function_name,
                    "project_id": self.project_id
                })
            elif self.resource_type == 'gce_instance':
                self.instance_id = self.get_instance()
                self.res = Resource(type=self.resource_type, labels={
                    "instance_id": self.instance_id,
                    "project_id": self.project_id
                })
            elif self.resource_type == "k8s_container":
                self.res = Resource(type=self.resource_type, labels={
                    "cluster_name": self.cluster_name,
                    "container_name": self.container_name,
                    "project_id": self.project_id,
                    "location": self.location,
                    "namespace_name": self.namespace_name,
                    "pod_id": ' '
                })
            elif self.resource_type == 'cloud_run_revision':
                self.res = Resource(type=self.resource_type, labels={
                    "configuration_name": self.service_name,
                    "location": self.location,
                    "project_id": self.project_id,
                    "revision_name": self.revision_version,
                    "service_name": self.service_name
                })
            else:
                self.res = Resource(type='global', labels={"project_id": self.project_id})

            self.logger = self.create_logger(self.project_id, self.service_name)


    def info(self, message):
        message = str(message)
        if self.local_run is False:
            self.logger.log_struct({'message': message, 'trace_id': self.trace_id, 'service_name': self.service_name}, resource=self.res, severity='INFO')
        else:
            print('Info: {}'.format(message))

    def warning(self, message):
        message = str(message)
        if self.local_run is False:
            self.logger.log_struct({'message': message, 'trace_id': self.trace_id, 'service_name': self.service_name}, resource=self.res, severity='WARNING')
        else:
            print('Warning: {}'.format(message))

    def error(self, message):
        message = str(message)
        if self.local_run is False:
            self.logger.log_struct({'message': message, 'trace_id': self.trace_id, 'service_name': self.service_name}, resource=self.res, severity='ERROR')
        else:
            print('Error: {}'.format(message))

    def critical(self, message):
        message = str(message)
        if self.local_run is False:
            self.logger.log_struct({'message': message, 'trace_id': self.trace_id, 'service_name': self.service_name}, resource=self.res, severity='CRITICAL')
        else:
            print('Critical: {}'.format(message))

    def debug(self, message):
        message = str(message)
        if self.local_run is False:
            self.logger.log_struct({'message': message, 'trace_id': self.trace_id, 'service_name': self.service_name}, resource=self.res, severity='DEBUG')
        else:
            print('Debug: {}'.format(message))