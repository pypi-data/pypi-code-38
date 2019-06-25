from logging import Logger
from typing import List, Optional

from azure.mgmt.compute.v2017_03_30.models import Resource, VirtualMachineScaleSet
from msrestazure.azure_exceptions import CloudError
from retrying import retry

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_instance_service import IAppInstanceService
from sidecar.azure_clp.azure_clients import AzureClientsManager
from sidecar.azure_clp.azure_status_maintainer import AzureStatusMaintainer
from sidecar.azure_clp.azure_tag_helper import AzureTagHelper
from sidecar.azure_clp.retrying_helpers import retry_if_connection_error
from sidecar.const import Const


class AzureAppInstanceService(IAppInstanceService):
    def __init__(self,
                 logger: Logger,
                 sandbox_id: str,
                 clients_manager: AzureClientsManager,
                 status_maintainer: AzureStatusMaintainer):
        super().__init__(logger)
        self._sandbox_id = sandbox_id
        self._compute_client = clients_manager.compute_client
        self._status_maintainer = status_maintainer

    def get_public_address(self, app_instance_identifier: AppInstanceIdentifier) -> str:
        # vm_resource = self._get_existing_vm_resource(vm_name=app_instance_identifier.infra_id,
        #                                              app_name=app_instance_identifier.name)
        return ''

    def update_status_if_not_stale(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        vm_name = app_instance_identifier.infra_id
        app_name = app_instance_identifier.name
        vm_resource = self._get_existing_vm_resource(vm_name, app_name)

        instance_logical_id = AzureTagHelper.safely_get_tag(vm_resource, Const.INSTANCELOGICALID)
        self._status_maintainer.update_app_instance_status(instance_logical_id=instance_logical_id,
                                                           instance_id=vm_name,
                                                           app_name=app_name,
                                                           status=status)

    def check_which_exist(self, identifiers: List[AppInstanceIdentifier]) -> List[AppInstanceIdentifier]:
        vm_names = list(set(identifier.infra_id for identifier in identifiers))
        vm_resources = self._get_sandbox_app_vm_resources_by_names(vm_names=vm_names)

        existing_identifiers = [app_instance_identifier
                                for vm_resource in vm_resources
                                for app_instance_identifier in self._create_app_instance_identifiers_from_vm(vm_resource)
                                if app_instance_identifier in identifiers]
        return existing_identifiers

    def update_deployment_outputs(self, app_instance_identifier: AppInstanceIdentifier, outputs: {}):
        vm_name = app_instance_identifier.infra_id
        app_name = app_instance_identifier.name
        vm_resource = self._get_existing_vm_resource(vm_name, app_name)

        instance_logical_id = AzureTagHelper.safely_get_tag(vm_resource, Const.INSTANCELOGICALID)
        self._status_maintainer.update_app_instance_deployment_outputs(instance_logical_id, vm_name, app_name, outputs)

    def get_deployment_outputs(self, app_name: str) -> {}:
        return self._status_maintainer.get_app_deployment_outputs(app_name)

    def _get_existing_vm_resource(self, vm_name, app_name) -> Resource:
        vm_resource = self._try_get_vm_under_resource_group(vm_name)
        if vm_resource is None:
            vm_resource = self._try_get_vm_under_scale_set(vm_name, app_name)
        if vm_resource is None:
            raise Exception("Instance for app '{APP_NAME}' not found. Instance_id={INSTANCE_ID}".
                            format(APP_NAME=app_name, INSTANCE_ID=vm_name))
        return vm_resource

    @retry(stop_max_attempt_number=5, wait_fixed=1000, retry_on_exception=retry_if_connection_error)
    def _try_get_vm_under_resource_group(self, vm_name) -> Optional[Resource]:
        try:
            return self._compute_client.virtual_machines.get(
                resource_group_name=self._sandbox_id,
                vm_name=vm_name)
        except CloudError as az_ex:
            if az_ex.status_code == 404:
                return None
            raise

    def _try_get_vm_under_scale_set(self, vm_name, app_name) -> Optional[Resource]:
        ss_vms = self._query_vms_under_scale_set(
            scale_set_name=self._construct_scale_set_name(app_name))
            # vm_filter="name eq '{vm_name}'".format(vm_name=vm_name)) # TODO: why filter gives error?
        vm_resource = next(iter(ss_vm for ss_vm in ss_vms if ss_vm.name == vm_name), None)
        return vm_resource

    @staticmethod
    def _construct_scale_set_name(app_name):
        return app_name

    def _get_sandbox_app_vm_resources_by_names(self, vm_names: List[str]) -> List[Resource]:
        # TODO: can do a better query?
        vm_resources = self._get_sandbox_app_vm_resources()
        return [vm for vm in vm_resources if vm.name in vm_names]

    def _get_sandbox_app_vm_resources(self) -> List[Resource]:
        vms_under_resource_group = self._query_vms_under_resource_groups()
        vms_under_scale_sets = self._get_vms_under_scale_sets()
        all_vms = vms_under_resource_group + vms_under_scale_sets
        app_vms_resources = self._filter_app_vm_resources(all_vms)
        return app_vms_resources

    def _filter_app_vm_resources(self, vm_resources: List[Resource]) -> List[Resource]:
        return [vm for vm in vm_resources
                if not self._is_infra_vm_resource(vm)]

    def _create_app_instance_identifiers_from_vm(self, vm_resource: Resource) -> List[AppInstanceIdentifier]:
        instance_logical_id = AzureTagHelper.safely_get_tag(vm_resource, Const.INSTANCELOGICALID)
        all_app_names = self._status_maintainer.get_app_names_on_instance(instance_logical_id)
        return [AppInstanceIdentifier(name=app_name, infra_id=vm_resource.name) for app_name in all_app_names]

    def _get_vms_under_scale_sets(self):
        scale_sets = self._query_scale_sets_under_resource_group()
        vms = [vm
               for scale_set in scale_sets
               for vm in self._query_vms_under_scale_set(scale_set.name)]
        return vms

    @retry(stop_max_attempt_number=5, wait_fixed=1000, retry_on_exception=retry_if_connection_error)
    def _query_vms_under_resource_groups(self) -> List[Resource]:
        return list(self._compute_client.virtual_machines.list(self._sandbox_id))

    @retry(stop_max_attempt_number=5, wait_fixed=1000, retry_on_exception=retry_if_connection_error)
    def _query_scale_sets_under_resource_group(self) -> List[VirtualMachineScaleSet]:
        return list(self._compute_client.virtual_machine_scale_sets.list(self._sandbox_id))

    @retry(stop_max_attempt_number=5, wait_fixed=1000, retry_on_exception=retry_if_connection_error)
    def _query_vms_under_scale_set(self, scale_set_name: str, vm_filter: str = None) -> List[Resource]:
        return list(self._compute_client.virtual_machine_scale_set_vms.list(
            resource_group_name=self._sandbox_id,
            virtual_machine_scale_set_name=scale_set_name,
            filter=vm_filter))

    @staticmethod
    def _is_infra_vm_resource(vm_resource: Resource) -> bool:
        app_name_tag_value = AzureTagHelper.safely_get_tag(vm_resource, Const.APP_NAME_TAG)
        return app_name_tag_value == Const.AWS_SIDECAR_APP_NAME or app_name_tag_value == Const.QUALY_SERVICE_NAME
