

from sidecar.const import Const

from sidecar.aws_status_maintainer import AWSStatusMaintainer


class AWSStatusMaintainerMock(AWSStatusMaintainer):

    default_table_attributes = [
        {
            'AttributeName': Const.SANDBOX_ID_TAG,
            'AttributeType': 'S',
        }
    ]

    default_table_schema = [
        {
            'AttributeName': Const.SANDBOX_ID_TAG,
            'KeyType': 'HASH',
        }
    ]

    default_table_provisioned_throughput = {
        'ReadCapacityUnits': 25,
        'WriteCapacityUnits': 25
    }

    def __init__(self, sandbox_data):
        if sandbox_data is not None:
            self.cached_sandbox_data = sandbox_data
        else:
            self.cached_sandbox_data = {"spec": {
                "expected_apps": {"1": {"apps": [], "instance_count": 1, Const.EXTERNAL_PORTS: {},
                                        Const.INTERNAL_PORTS: {}},
                                  "2": {"apps": [], "instance_count": 1, Const.EXTERNAL_PORTS: {},
                                        Const.INTERNAL_PORTS: {}}}
            }, "apps": {"1":
                {"instances":
                    {
                    }
                },
                "2":
                    {"instances":
                        {
                        }
                    }
            }}

    def add_sendboxdata_to_structure(self, sandboxid
                                     ):
        self.cached_sandbox_data[Const.SANDBOX_ID_TAG] = sandboxid

        # configuration[sidecarappname] = {"appStatus": CommonCloudStorageManager.APP_STATE.NOT_STARTED.value,
        #                                  "instanceState": CommonCloudStorageManager.INSTANCE_STATE.START_DEPLOYMENT.value}
        #
        # configuration[qualyservicename] = {"appStatus": CommonCloudStorageManager.APP_STATE.NOT_STARTED.value,
        #                                    "instanceState": CommonCloudStorageManager.INSTANCE_STATE.START_DEPLOYMENT.value}

    def create_table_if_not_exists(self):
        return None

    def upload_table_structure(self, sandboxid):
        return None

    def delete_sandbox_record(self, sandboxid):
        return None

    def check_if_sandbox_exists(self, sandbox_id: str):
        return True

    def refresh_sandbox_data(self, sandbox_id: str):
        return None

    def get_all_app_names_for_instance(self, logical_id: str):
        return self.cached_sandbox_data["spec"]["expected_apps"][logical_id]["apps"]

    def get_all_apps_for_logical_id(self, sandbox_id: str, logical_id: str):
        logical_instance = self.cached_sandbox_data["spec"]["expected_apps"][logical_id]
        return logical_instance["apps"]

    def getAllappExternalPortsForInstance(self, sandbox_id: str, logical_id: str, instance_id: str):
        result = {}

        logical_instance = self.cached_sandbox_data["apps"][logical_id]["instances"]
        apps = []
        if instance_id in logical_instance:
            apps = logical_instance[instance_id]["apps"].keys()
        for app in apps:
            result[app] = self.cached_sandbox_data["spec"]["expected_apps"][logical_id][Const.EXTERNAL_PORTS][app]
        return result

    def get_app_to_instances_count_from_cache(self):
        result = {}
        for logical_instance in self.cached_sandbox_data["spec"]["expected_apps"].values():
            for app in logical_instance["apps"]:
                result[app] = int(logical_instance["instance_count"])
        return result

    def set_instance_id(self, logical_id: str, instance_id: str):
        self.cached_sandbox_data["apps"][logical_id]["instances"][instance_id] = {"apps":
            {
            }
        }

    def change_instance_count_for_logical_id(self, logical_id: str, instance_count: int):
        self.cached_sandbox_data["spec"]["expected_apps"][logical_id]["instance_count"] = instance_count

    def add_app_to_sandbox_configuration(self, logical_id: str, instance_id: str, app_name: str, app_status: str,
                                         external_ports):
        self.cached_sandbox_data["spec"]["expected_apps"][logical_id]["apps"].append(app_name)
        self.cached_sandbox_data["spec"]["expected_apps"][logical_id][Const.EXTERNAL_PORTS][app_name] = external_ports

    def add_app_to_sandbox_data(self, logical_id: str, instance_id: str, app_name: str, app_status: str,
                                external_ports):
        self.cached_sandbox_data["apps"][logical_id]["instances"][instance_id]["apps"][app_name] = {
            Const.APP_STATUS_TAG: app_status}
        self.cached_sandbox_data["spec"]["expected_apps"][logical_id]["apps"].append(app_name)
        self.cached_sandbox_data["spec"]["expected_apps"][logical_id][Const.EXTERNAL_PORTS][
            app_name] = external_ports

    def update_app_instance_status(self, instance_logical_id, instance_id, app_name, status_tag, status):

        if instance_id not in self.cached_sandbox_data["apps"][instance_logical_id]["instances"]:
            self.cached_sandbox_data["apps"][instance_logical_id]["instances"][instance_id] = \
                {
                    "apps": {}
                }

        self.cached_sandbox_data["apps"][instance_logical_id]["instances"][instance_id]["apps"][app_name] = {
            status_tag: status}

    def update_sandbox_end_status(self, sandbox_deployment_end_status: str):
        self.cached_sandbox_data[Const.SANDBOX_DEPLOYMENT_END_STATUS_v2] = sandbox_deployment_end_status

    def getAllappStatusForInstance(self, logical_id: str, instance_id: str):
        logical_instance = self.cached_sandbox_data["apps"][logical_id]["instances"]
        if instance_id in logical_instance:
            return logical_instance[instance_id]["apps"]
        else:
            return {}

    def update_sandbox_start_status(self, sandbox_start_time):
        self.cached_sandbox_data[Const.SANDBOX_START_TIME_v2] = sandbox_start_time