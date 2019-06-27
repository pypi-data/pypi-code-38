import json
from typing import List

from sidecar.const import Const


class KubApiPodReader:
    @staticmethod
    def get_pod_name(pod: {}) -> str:
        return pod['metadata']['name']

    @staticmethod
    def is_pod_ended(pod):
        return KubApiPodReader.get_pod_phase(pod) in ["Failed", "Succeeded"]

    @staticmethod
    def is_pod_terminating(pod: {}) -> bool:
        return True if pod['metadata'].get('deletionTimestamp', None) else False

    @staticmethod
    def get_pod_annotations(pod: {}) -> {}:
        return pod['metadata']['annotations']

    @staticmethod
    def get_apps_info_json(pod: {}) -> {}:
        return json.loads(KubApiPodReader.get_pod_annotations(pod)[Const.APPS])

    @staticmethod
    def get_service_json(pod: {}, service_name: str):
        return json.loads(KubApiPodReader.get_pod_annotations(pod)[service_name])

    @staticmethod
    def safely_get_pod_ip(pod: {}) -> str:
        # pod status may not contain podIP key because by default the k8s api doesn't return uninitialized properties
        # and this property can be empty in some pod states
        return pod['status'].get('podIP', None)

    @staticmethod
    def get_pod_phase(pod: {}) -> str:
        return pod['status']['phase']

    @staticmethod
    def safely_get_container_id_for_app(app_name: str, pod: {}) -> str:
        container_statuses = pod['status'].get('containerStatuses', [])
        return next(iter(KubApiPodReader._get_container_id_from_status(container_status)
                         for container_status in container_statuses if container_status['name'] == app_name),
                    None)

    @staticmethod
    def safely_get_container_ids_in_pod(pod: {}) -> List[str]:
        container_ids = []
        container_statuses = pod['status'].get('containerStatuses', [])
        for container_status in container_statuses:
            container_id = KubApiPodReader._get_container_id_from_status(container_status)
            if container_id:
                container_ids.append(container_id)
        return container_ids

    @staticmethod
    def _get_container_id_from_status(container_status: {}) -> str:
        container_id = container_status.get('containerID', None)
        if container_id:
            # when container has restarted but hasn't start running yet ("waiting", e.g. due to CrashLoopBackOff),
            # containerID holds the id of the previous container for some reason
            # so we don't return it because that container has already terminated
            container_state = container_status['state']
            if container_state.get('waiting', None) is not None:
                container_id = None
        return container_id
