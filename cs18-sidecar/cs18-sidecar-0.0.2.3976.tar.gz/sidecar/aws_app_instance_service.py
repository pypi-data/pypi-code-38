from logging import Logger
from typing import List

import datetime

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.aws_session import AwsSession
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const
from sidecar.app_instance_service import IAppInstanceService, StaleAppInstanceException
from sidecar.aws_status_maintainer import AWSStatusMaintainer


class AwsAppInstanceService(IAppInstanceService):

    def __init__(self, sandbox_id: str, logger: Logger, aws_session: AwsSession,
                 aws_status_maintainer: AWSStatusMaintainer):
        super().__init__(logger)
        self.aws_session = aws_session
        self.sandbox_id = sandbox_id
        self.aws_status_maintainer = aws_status_maintainer

    def _update_app_status(self, instance_id: str, app_name: str, status: str):
        instance = self._get_existing_instance(instance_id, app_name)
        # should update status only for a "live" instance
        if not self._is_instance_part_of_sandbox(instance):
            raise StaleAppInstanceException("cannot update '{APP_NAME}' status to '{STATUS}' since the app instance is "
                                            "no longer a part of the sandbox. infra id: {INFRA_ID}"
                                            .format(APP_NAME=app_name, STATUS=status, INFRA_ID=instance_id))

        instance_logical_id = AwsTagHelper.wait_for_tag(instance, Const.INSTANCELOGICALID, self._logger)
        self.aws_status_maintainer.update_app_instance_status(instance_logical_id, instance_id, app_name,
                                                              Const.APP_STATUS_TAG, status)

    def get_deployment_outputs(self, app_name: str) -> {}:
        return self.aws_status_maintainer.get_app_deployment_outputs(app_name)

    def update_deployment_outputs(self, app_instance_identifier: AppInstanceIdentifier, outputs: {}):
        instance_id = app_instance_identifier.infra_id
        app_name = app_instance_identifier.name
        instance = self._get_existing_instance(instance_id, app_name)
        # should update status only for a "live" instance
        if not self._is_instance_part_of_sandbox(instance):
            raise StaleAppInstanceException("cannot update '{APP_NAME}' outputs since the app instance is "
                                            "no longer a part of the sandbox. infra id: {INFRA_ID}"
                                            .format(APP_NAME=app_name, INFRA_ID=instance_id))

        instance_logical_id = AwsTagHelper.wait_for_tag(instance, Const.INSTANCELOGICALID, self._logger)
        self.aws_status_maintainer.update_app_instance_outputs(instance_logical_id, instance_id, app_name, outputs)

    def _get_existing_instance(self, instance_id: str, app_name: str):
        instance = self._get_instance_by_id(instance_id)
        if instance is None:
            raise Exception("instance for app '{APP_NAME}' not found. instance_id={INSTANCE_ID}"
                            .format(APP_NAME=app_name, INSTANCE_ID=instance_id))
        return instance

    def get_public_address(self, app_instance_identifier: AppInstanceIdentifier) -> str:
        instance = self._get_existing_instance(instance_id=app_instance_identifier.infra_id,
                                               app_name=app_instance_identifier.name)
        alb_dns = next((tag['Value'] for tag in instance.tags if tag['Name'] == Const.EXTERNAL_ELB_DNS_NAME), None)
        return alb_dns

    def update_status_if_not_stale(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        instance_id = app_instance_identifier.infra_id
        self._update_app_status(instance_id, app_instance_identifier.name, status)

    def check_which_exist(self, identifiers: List[AppInstanceIdentifier]) -> List[AppInstanceIdentifier]:
        instance_ids = list(set(identifier.infra_id for identifier in identifiers))
        instances = self._get_sandbox_app_instances_by_ids(instance_ids=instance_ids)

        existing_identifiers = [app_instance_identifier
                                for instance in instances
                                for app_instance_identifier in self._create_app_instance_identifiers(instance)
                                if app_instance_identifier in identifiers]
        return existing_identifiers

    def _get_instance_by_id(self, instance_id: str):
        ec2 = self.aws_session.get_ec2_resource()
        return ec2.Instance(instance_id)

    def _is_instance_part_of_sandbox(self, instance) -> bool:
        instance_as_list = [instance]
        self._filter_out_autoscaling_instances_not_in_asg(instance_as_list)
        return instance in instance_as_list

    def _get_sandbox_app_instances_by_ids(self, instance_ids: List[str]) -> list():
        instances = self._query_instances_by_ids(instance_ids)
        self._filter_live_app_instances(instances)
        return instances

    def _query_instances_by_ids(self, instance_ids: List[str]):
        instances = list(self.aws_session.get_ec2_resource().instances.filter(InstanceIds=instance_ids))
        self._logger.info("[{TIMESTAMP} utc] query for instances by ids ({queries_ids}) returned: {ids}"
                          .format(TIMESTAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%X'),
                                  queries_ids=", ".join(instance_ids),
                                  ids=", ".join(inst.instance_id for inst in instances)))

        return instances

    def _filter_live_app_instances(self, instances: list()):
        self._filter_out_infra_instances(instances)
        self._filter_out_autoscaling_instances_not_in_asg(instances)

    def _filter_out_infra_instances(self, instances: list()):
        for instance in instances[:]:
            if self._is_infra_instance(instance):
                instances.remove(instance)

    def _filter_out_autoscaling_instances_not_in_asg(self, instances_to_filter: list()):
        asg_name_to_instances_map = self._get_asg_name_to_instances_map(instances_to_filter)
        asg_names = list(asg_name_to_instances_map.keys())
        if not asg_names:
            return
        asg_name_to_existing_instance_ids_map = self._get_existing_asg_instance_ids(asg_names)

        for asg_name, asg_instances_list in asg_name_to_instances_map.items():
            existing_instance_ids = asg_name_to_existing_instance_ids_map.get(asg_name, [])
            for instance in asg_instances_list:
                if instance.instance_id not in existing_instance_ids:
                    instances_to_filter.remove(instance)

    def _get_asg_name_to_instances_map(self, instances):
        asg_name_to_instances_map = dict()
        for instance in instances:
            asg_tag_value = AwsTagHelper.wait_for_tags(instance, self._logger).get(AwsTagHelper.AutoScalingGroupNameTag)
            if asg_tag_value:
                asg_instances_list = asg_name_to_instances_map.setdefault(asg_tag_value, [])
                asg_instances_list.append(instance)
        return asg_name_to_instances_map

    def _get_existing_asg_instance_ids(self, asg_names: List[str]) -> dict():
        if not asg_names:
            return {}
        autoscaling_groups = self._query_autoscaling_groups_by_names(asg_names)
        asg_name_to_existing_instance_ids_map = \
            {asg['AutoScalingGroupName']: [as_inst['InstanceId'] for as_inst in asg['Instances']]
             for asg in autoscaling_groups}
        return asg_name_to_existing_instance_ids_map

    def _query_autoscaling_groups_by_names(self, asg_names: List[str]) -> []:
        autoscaling_client = self.aws_session.get_autoscaling_client()
        response = autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=asg_names)
        autoscaling_groups = response['AutoScalingGroups']
        return autoscaling_groups

    def _create_app_instance_identifiers(self, instance) -> List[AppInstanceIdentifier]:
        instance_logical_id = AwsTagHelper.wait_for_tag(instance, Const.INSTANCELOGICALID, self._logger)
        all_app_names = self.aws_status_maintainer.get_all_app_names_for_instance(instance_logical_id)
        return [AppInstanceIdentifier(name=app_name, infra_id=instance.instance_id) for app_name in all_app_names]

    def _is_infra_instance(self, instance) -> bool:
        app_name_tag_value = AwsTagHelper.wait_for_tag(instance, Const.APP_NAME_TAG, self._logger)
        return app_name_tag_value in [Const.AWS_SIDECAR_APP_NAME, Const.QUALY_SERVICE_NAME]
