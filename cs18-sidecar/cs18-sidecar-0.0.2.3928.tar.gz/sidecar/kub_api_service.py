import json
from abc import abstractmethod, ABCMeta
from logging import Logger

import requests
import urllib3
from requests import Session

from sidecar.const import Const
from sidecar.kub_api_pod_reader import KubApiPodReader
from sidecar.kub_token_provider import KubTokenProvider


class IKubApiService(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_all_pods_list(self, include_infra: bool = True, include_ended=True, include_terminating: bool = True) -> []:
        raise NotImplementedError

    @abstractmethod
    def try_get_pod_json_by_ip(self, ip_address: str) -> {}:
        raise NotImplementedError

    @abstractmethod
    def try_get_pod_json_by_container_id(self, container_id: str) -> {}:
        raise NotImplementedError

    @abstractmethod
    def try_get_pod_json_by_pod_name(self, pod_name: str) -> {}:
        raise NotImplementedError

    @abstractmethod
    def update_namespace(self, annotations: {}):
        raise NotImplementedError

    @abstractmethod
    def update_pod(self, pod_name: str, annotations: {}):
        raise NotImplementedError

    @abstractmethod
    def update_service(self, name: str, data: {}):
        raise NotImplementedError

    @abstractmethod
    def get_all_services(self) -> {}:
        raise NotImplementedError

    def get_pod_by_name(self, name: str) -> {}:
        raise NotImplementedError()


class KubApiService(IKubApiService):
    def __init__(self,
                 hostname: str,
                 namespace: str,
                 kub_token_provider: KubTokenProvider,
                 logger: Logger):
        super().__init__()
        self.logger = logger
        self.namespace = namespace
        self.hostname = hostname
        self._disable_secure_warnings()
        self.token = kub_token_provider.get_token()

    def get_pod_by_name(self, name: str) -> str:
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = "{HOSTNAME}/api/v1/namespaces/{NAMESPACE}/pods/{POD}".format(
            HOSTNAME=self.hostname,
            NAMESPACE=self.namespace,
            POD=name
        )

        try:
            res = s.get(url=url, verify=False)
            res.raise_for_status()
            return res.json()
        except Exception as exc:
            self.logger.exception("Got exception while getting pod {pod}, message: {message}".format(
                pod=name,
                message=str(exc)))
            raise exc

    def get_all_pods_list(self, include_infra: bool = True, include_ended=True, include_terminating: bool = True) -> []:
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}/pods'. \
            format(hostname=self.hostname,
                   namespace=self.namespace)
        query_params = {}
        if not include_infra:
            query_params['labelSelector'] = '{app_selector_label}!={sidecar_selector_value}'.format(
                app_selector_label=Const.K8S_SIDECAR_APP_SELECTOR,
                sidecar_selector_value=Const.K8S_SIDECAR_SERVICE)
        res = s.get(url=url, verify=False, params=query_params)
        try:
            res.raise_for_status()
        except Exception as exc:
            self.logger.exception("Got exception while getting all pods list, message: {message}".format(message=str(exc)))
            raise exc

        pods_json = res.json()
        pods = pods_json['items']
        live_app_pods = self._filter_pods(pods=pods, include_ended=include_ended,
                                          include_terminating=include_terminating)
        return live_app_pods

    def try_get_pod_json_by_ip(self, ip_address: str) -> {}:
        # when we're looking for a specific pod, we want to find it no matter in what state it is
        pods = self.get_all_pods_list()
        pod_json = next(iter([pod for pod in pods if KubApiPodReader.safely_get_pod_ip(pod) == ip_address]), None)
        return pod_json

    def try_get_pod_json_by_container_id(self, container_id: str) -> {}:
        # when we're looking for a specific pod, we want to find it no matter in what state it is
        pods = self.get_all_pods_list()
        pod_json = next(iter([pod for pod in pods
                              if container_id in KubApiPodReader.safely_get_container_ids_in_pod(pod=pod)]),
                        None)
        return pod_json

    def try_get_pod_json_by_pod_name(self, pod_name: str) -> {}:
        # when we're looking for a specific pod, we want to find it no matter in what state it is
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}/pods/{pod_name}'. \
            format(hostname=self.hostname,
                   namespace=self.namespace,
                   pod_name=pod_name)
        res = s.get(url=url, verify=False)
        if res.status_code == 404:
            self.logger.error("Got 404 while trying to try_get_pod_json_by_pod_name, pod name: {pod_name}"
                              .format(pod_name=pod_name))
            return None
        try:
            res.raise_for_status()
        except Exception as exc:
            self.logger.exception("Got exception while getting json by pd name, pod name: {pod_name} , message: {message}".format(pod_name=pod_name, message=str(exc)))
            raise exc
        pod_json = res.json()
        return pod_json

    def get_all_services(self) -> []:
        s = self._get_session()
        url = '{}/api/v1/namespaces/{}/services/'.format(self.hostname, self.namespace)
        res = s.get(url=url, verify=False)
        if res.status_code == 404:
            self.logger.error("Could not find services in namespace {}".format(self.namespace))
            return None
        try:
            res.raise_for_status()
            return res.json()['items']
        except Exception as exc:
            self.logger.exception(exc)
            raise exc

    def _update(self, url: str, annotations: {}):
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        data_json = {
            'metadata': {
                'annotations': annotations
            }
        }
        metadata_json = json.dumps(data_json)
        res = s.patch(url=url, data=metadata_json, verify=False)
        res.raise_for_status()

    def update_service(self, name: str, data: {}):
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}/services/{name}' \
            .format(hostname=self.hostname,
                    namespace=self.namespace,
                    name=name)
        try:
            metadata_json = json.dumps(data)
            res = s.patch(url=url, data=metadata_json, verify=False)
            res.raise_for_status()
        except Exception as exc:
            self.logger.exception("Got exception while updating service, message: {message}".format(message=str(exc)))
            raise exc

    def update_namespace(self, annotations: {}):
        url = '{hostname}/api/v1/namespaces/{namespace}'.format(hostname=self.hostname,
                                                                namespace=self.namespace)
        try:
            self._update(url=url, annotations=annotations)
        except Exception as exc:
            self.logger.exception("Got exception while updating namespace, message: {message}".format(message=str(exc)))
            raise exc

    def update_pod(self, pod_name: str, annotations: {}):
        url = '{hostname}/api/v1/namespaces/{namespace}/pods/{pod_name}' \
            .format(hostname=self.hostname,
                    namespace=self.namespace,
                    pod_name=pod_name)
        try:
            self._update(url=url, annotations=annotations)
        except Exception as exc:
            self.logger.exception("Got exception while updating pod, pod name: {pod_name}, message: {message}".format(pod_name=pod_name, message=str(exc)))
            raise exc

    def _get_session(self) -> Session:
        s = requests.Session()
        s.headers['Authorization'] = 'Bearer ' + self.token
        return s

    @staticmethod
    def _filter_pods(pods: [], include_ended: bool, include_terminating: bool) -> []:
        # filtering out ended pods relies on the assumption that pods' restart policy is Always,
        # meaning that new pods were created instead of the ended ones and the old ones are no longer relevant
        # the terminating pods are filtered out because under this restart policy sometimes the new pod can be created
        # while the old one is still terminating and we don't want to get both of them, but only the "live" one
        return [pod for pod in pods
                if (include_ended or not KubApiPodReader.is_pod_ended(pod)) and
                (include_terminating or not KubApiPodReader.is_pod_terminating(pod))
                ]

    @staticmethod
    def _disable_secure_warnings():
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
