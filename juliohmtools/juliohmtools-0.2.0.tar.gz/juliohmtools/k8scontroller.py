import kubernetes
import os
import logging
import threading
import time

logger = logging.getLogger(__name__)

class Controller():
    '''
    A general purpose controller wrapped around the Kubernetes API.

    This controller will only listen to CRDs from the CustomObjectsApi. It will
    not listen to native Kubernetes objects.
    '''

    group       = None
    name        = None
    namespace   = None
    version     = 'v1'

    timeout_seconds = 0
    reconnect_interval_seconds = 15

    handlers = list()

    def set_group(self, group):
        self.group = group

    def set_name(self, name):
        self.name = name

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_version(self, version):
        self.version = version

    def set_kubeconfig_file(self, kubeconfig_file):
        self.kubeconfig_file = kubeconfig_file

    def set_api_timeout(self, timeout_seconds):
        '''
        Timeout waiting for Kubernetes API events. When this time expires, the
        controller will reloop, reconnect to the stream and keep watching for
        events.

        Parameters
        ==========
        `timeout_seconds`:
            Time in seconds to wait for API events. Default: 300 (5min)
        '''
        self.timeout_seconds=timeout_seconds

    def set_reconnect_interval(self, reconnect_interval_seconds):
        '''
        How long to wait and reconnect to the API server after a timeout.

        Parameters
        ===========
        `reconnect_interval_seconds`:
            Time in seconds to wait before reconnecting. Default: 15
        '''
        self.reconnect_interval_seconds=reconnect_interval_seconds

    def add_handler(self, handler):
        '''
        Handler functions that will be called when new events are captured
        on the objects that being watched.

        Handler signature
        =================
        ```
        def my_handler(event, obj):
            pass
        ```
        
        Handler parameters
        ==================
        `event`:
            Event that was received from the API
        
        `obj`:
            Object related to the event. This is also contained inside
            the event object, but handed separately here for convenience.
        '''
        self.handlers.append(handler)

    def watch(self):
        '''
        Main loop that watches over CRD events.
        '''

        if self.kubeconfig_file:
            logging.info('Using kubeconfig_file='+str(self.kubeconfig_file))
            kubernetes.config.load_kube_config(config_file=self.kubeconfig_file)
        elif 'KUBERNETES_SERVICE_HOST' in os.environ:
            kubernetes.config.load_incluster_config()
        else:
            raise Exception('Unable to load Kubernetes configuration')

        if not self.group:
            raise Exception('group is a required value')

        if not self.name:
            raise Exception('name is a required value')

        if not self.version:
            self.version = 'v1'

        crdapi  = kubernetes.client.CustomObjectsApi()
        watch = kubernetes.watch.Watch()

        while True:
            try:
                stream = None
                if self.namespace:
                    logger.info('Watching for CRD group={:s} version={:s} name={:s} namespace={:s}'.format(self.group, self.version, self.name, self.namespace))
                    stream = watch.stream(
                        crdapi.list_namespaced_custom_object,
                        group=self.group,
                        version=self.version,
                        plural=self.name,
                        timeout_seconds=self.timeout_seconds
                        )
                else:
                    logger.info('Watching for CRD group={:s} version={:s} name={:s}'.format(self.group, self.version, self.name))
                    stream = watch.stream(
                        crdapi.list_cluster_custom_object,
                        group=self.group,
                        version=self.version,
                        plural=self.name,
                        timeout_seconds=self.timeout_seconds
                        )
                for event in stream:
                    self.on_event(event, event['object'])
            except Exception as err:
                logging.error('Error watching: '+str(err))
                logging.debug(err, exc_info=True)
                time.sleep(self.reconnect_interval_seconds)
 
    def watch_background(self):
        '''
        Start watch() in a background thread.

        Returns
        =======
        The thread object where the loop is running.
        '''
        th = threading.Thread(target=self.watch)
        th.start()
        return th

    def on_event(self, event, obj):
        '''
        Default implementation for the CRD event handler.
        '''
        logger.info('{:s} {:s} {:s}/{:s}'.format(event['type'], obj['kind'], obj['metadata']['namespace'], obj['metadata']['name']))
        if len(self.handlers) <= 0:
            logger.info('No handlers defined')
            return
        for h in self.handlers:
            try:
                h(event, obj)
            except Exception as err:
                logging.error('Error handling event {:s} for {:s}/{:s}'.format(
                    event['type'],
                    obj['metadata']['namespace'], obj['metadata']['name']
                ))
                logging.error('Error: '+str(err))
                logging.debug(err, exc_info=True)
                time.sleep(self.reconnect_interval_seconds)

