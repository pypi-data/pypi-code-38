import json
import threading
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Optional, List, Dict, Tuple

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.aws_session import AwsSession
from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const, get_app_selector
from sidecar.kub_api_service import IKubApiService
from sidecar.model.objects import EnvironmentType
from sidecar.utils import Utils, CallsLogger


class StaleAppException(Exception):
    pass


class AppService:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_network_status(self, app_name: str, status: str):
        raise NotImplementedError

    @abstractmethod
    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_sandbox_public_dns(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        """
        allows public access to sidecar to the instances
        :param identifier:
        :return: whether public access was required
        """
        raise NotImplementedError

    @abstractmethod
    def can_access_from_public_address(self, identifier: AppInstanceIdentifier) -> bool:
        raise NotImplementedError


class AzureAppService(AppService):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def update_network_status(self, app_name: str, status: str):
        pass

    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        pass

    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        pass

    def get_sandbox_public_dns(self) -> str:
        return ''

    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        return False

    def can_access_from_public_address(self, identifier: AppInstanceIdentifier) -> bool:
        return False


class K8sAppService(AppService):
    def __init__(self, api: IKubApiService, sandbox_id: str, own_public_ip: str, logger: Logger):
        super().__init__(logger)
        self._own_public_ip = own_public_ip
        self.sandbox_id = sandbox_id
        self._api = api
        self._lock = threading.RLock()

    @CallsLogger.wrap
    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        return True

    @CallsLogger.wrap
    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        service = self._get_service_by_app_name(app_name=app_name)
        return "{}.{}".format(service['metadata']['name'], self.sandbox_id)

    @CallsLogger.wrap
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        dns_name = Utils.retry_on_exception(func=lambda: self._get_public_dns_name_by_app_name(app_name=app_name),
                                            timeout_in_sec=address_read_timeout,
                                            logger=self._logger,
                                            logger_msg="trying to get public dns for app '{}'.".format(app_name))
        return dns_name

    def get_sandbox_public_dns(self) -> str:
        return ''

    def _get_public_dns_name_by_app_name(self, app_name: str) -> Optional[str]:
        service = self._get_service_by_app_name(app_name=app_name)
        if service["spec"]["type"] != "LoadBalancer":
            return None

        if "status" not in service:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing does not have 'status' yet. "
                "service details: {service_details}".format(app_name=app_name, service_details=json.dumps(service)))

        if "loadBalancer" not in service["status"]:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing does not have 'status.loadBalancer' yet. "
                "service details: {service_details}".format(app_name=app_name, service_details=json.dumps(service)))

        load_balancer = service["status"]['loadBalancer']
        if "ingress" not in load_balancer:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing "
                "does not have 'status.loadBalancer.ingress' yet. "
                "service details: {service_details}".format(
                    app_name=app_name, service_details=json.dumps(service)))

        ingress = next(iter(load_balancer['ingress']), None)
        if ingress and "ip" not in ingress and "hostname" not in ingress:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing "
                "does not have 'status.loadBalancer.ingress.ip' or 'status.loadBalancer.ingress.hostname' yet. "
                "service details: {service_details}".format(
                    app_name=app_name, service_details=json.dumps(service)))

        return ingress['ip'] if "ip" in ingress else ingress['hostname']

    @CallsLogger.wrap
    def update_network_status(self, app_name: str, status: str):
        # TODO: rethink it !!! not so good to mark both services when only one got checked
        app_services = [service for service in self._api.get_all_services()
                        if service['spec']['selector'] == {**{get_app_selector(app_name): app_name}}]

        for app_service in app_services:
            annotations = app_service['metadata']['annotations']
            if app_service['metadata'][
                'annotations'] is None or Const.HEALTH_CHECK_STATUS not in annotations:  # backward compatibility
                annotations = {Const.HEALTH_CHECK_STATUS: status}
            else:
                annotations[Const.HEALTH_CHECK_STATUS] = status
            self._api.update_service(name=app_service['metadata']['name'], data={
                'metadata': {
                    'annotations': annotations
                }
            })

    def _get_service_by_app_name(self, app_name: str) -> dict:
        services = self._api.get_all_services()
        service = next(
            iter([service for service in services if
                  service['spec']['selector'] == {**{get_app_selector(app_name): app_name}}]),
            None)
        if service is None:
            raise StaleAppException(
                "Cannot get '{app_name}' since the service exposing it does not exists.".format(
                    app_name=app_name))

        return service

    def can_access_from_public_address(self, identifier: AppInstanceIdentifier) -> bool:
        return True


class AWSAppService(AppService):
    PUBLIC_PORT_ACCESS = "public port access"
    PUBLIC_HEALTH_CHECK = "public health check"

    def __init__(self,
                 session: AwsSession,
                 aws_status_maintainer: AWSStatusMaintainer,
                 own_public_ip: str,
                 sandbox_id: str,
                 production_id: str,
                 env_type: EnvironmentType,
                 logger: Logger,
                 table_name: str,
                 default_region: str = None):

        super().__init__(logger)
        self._aws_status_maintainer = aws_status_maintainer
        self.default_region = default_region
        self._own_public_ip = own_public_ip
        self._sandbox_id = sandbox_id
        self._production_id = production_id
        self._table_name = table_name
        self._session = session
        self._lock = threading.RLock()
        self._env_type = env_type

    @CallsLogger.wrap
    def update_network_status(self, app_name: str, status: str):
        table, item = Utils.retry_on_exception(
            func=lambda: self._get_table(sandbox_id=self._sandbox_id),
            logger=self._logger,
            logger_msg="cannot get public dns for app '{}'.".format(app_name))

        if 'logical-apps' not in item:  # backward compatibility
            item["logical-apps"] = {**{app_name: {Const.HEALTH_CHECK_STATUS: status}}}
        else:
            item["logical-apps"][app_name][Const.HEALTH_CHECK_STATUS] = status

        response = table.update_item(
            Key={Const.SANDBOX_ID_TAG: self._sandbox_id},
            UpdateExpression='set #col = :r',
            ExpressionAttributeValues={':r': item["logical-apps"]},
            ExpressionAttributeNames={"#col": "logical-apps"},
            ReturnValues="UPDATED_NEW"
        )
        if AWSStatusMaintainer.response_failed(response):
            self._logger.info("Error update_network_status(app_name: '{}', status: {})\n"
                              "Response: {}".format(app_name, status, response))

    def _get_instance_external_ports(self, identifier: AppInstanceIdentifier) -> List[int]:
        ec2_resource = self._session.get_ec2_resource()
        instance = ec2_resource.Instance(identifier.infra_id)
        logical_id = AwsTagHelper.wait_for_tag(instance, Const.INSTANCELOGICALID, self._logger)
        _, item = Utils.retry_on_exception(
            func=lambda: self._get_table(sandbox_id=self._sandbox_id),
            logger=self._logger,
            logger_msg="Cannot get sandbox {} data for instance {} ports".format(self._sandbox_id, logical_id))

        instance_data = item['spec']['expected_apps'].get(logical_id)
        if instance_data:
            return [int(port) for app_ports in instance_data['colony-external-ports'].values() for port in app_ports]
        else:
            self._logger.warning('instance id {} was not found under "expected_apps"'.format(logical_id))
            return []

    def _get_alb_security_group(self) -> Dict:
        ec2_client = self._session.get_ec2_client()
        if self._production_id:
            response = ec2_client.describe_security_groups(
                Filters=[{'Name': f'tag:{Const.PRODUCTION_ID_TAG}', 'Values': [self._production_id]},
                         {'Name': 'tag:Name', 'Values': [Const.MAIN_ALB_SG]}])
        else:
            response = ec2_client.describe_security_groups(
                Filters=[{'Name': f'tag:{Const.SANDBOX_ID_TAG}', 'Values': [self._sandbox_id]},
                         {'Name': 'tag:Name', 'Values': [Const.MAIN_ALB_SG]}])

        return next(iter(response['SecurityGroups']), None)

    def _get_permissions_for_ports(self, sg: Dict, external_ports: List[int]) -> List[Dict]:
        permissions = [p for p in sg['IpPermissions'] if p['FromPort'] in external_ports]
        permissions = [port
                       for port in permissions
                       if len(port["IpRanges"]) > 0 and len([ip
                                                             for ip in port["IpRanges"]
                                                             if "Description" in ip and ip[
                                                                 "Description"] == self.PUBLIC_PORT_ACCESS]) > 0]
        return permissions

    def _add_permissions_for_sidecar(self, sg_id: str, permissions: List[Dict]):
        ec2_client = self._session.get_ec2_client()
        sidecar_public_cidr = "{}/32".format(self._own_public_ip.rstrip('\n'))

        new_permissions = []
        for permission in permissions:
            permitted_cidrs = [cidr["CidrIp"] for cidr in permission["IpRanges"]]
            if sidecar_public_cidr in permitted_cidrs or '0.0.0.0/0' in permitted_cidrs:
                self._logger.info(f'Sidecar is already allowed to access port {permission["FromPort"]}')
                continue

            new_permissions.append({'IpProtocol': 'tcp',
                                    'FromPort': permission["FromPort"],
                                    'ToPort': permission["ToPort"],
                                    'IpRanges': [{
                                        'CidrIp': sidecar_public_cidr,
                                        'Description': self.PUBLIC_HEALTH_CHECK}]})
        if new_permissions:
            self._logger.info(f'Opening ports {[p["FromPort"] for p in new_permissions]} for public healthcheck')
            ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=new_permissions)

    @CallsLogger.wrap
    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        # Allowing access from sidecar's public ip to sandbox ALB
        with self._lock:  # restrict to 1 instance at the time

            # Get instance external ports from DynamoDB
            external_ports = self._get_instance_external_ports(identifier=identifier)
            if not external_ports:
                self._logger.info(f'App "{identifier.name}" does not have external ports')
                return False
            else:
                self._logger.info(f'App "{identifier.name}" have {len(external_ports)} external ports {external_ports}')

            # Get ALB SecurityGroup
            sg = self._get_alb_security_group()
            if not sg:
                self._logger.error(f'Failed to open firewall ports {external_ports} - ALB SecurityGroup was not found')
                return False

            # Get the relevant permissions for the current instance ports
            permissions = self._get_permissions_for_ports(sg=sg, external_ports=external_ports)
            missing_port_permissions = list(set(external_ports) - set([p['FromPort'] for p in permissions]))
            if missing_port_permissions:
                self._logger.error(
                    f'Failed to open firewall ports {missing_port_permissions} - No matching rules where found for')
                return False

            # Verify sidecar's public ip has access, and if not, create one
            self._add_permissions_for_sidecar(sg_id=sg['GroupId'], permissions=permissions)
            return True

    @CallsLogger.wrap
    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        instance = self._session.get_ec2_resource().Instance(infra_id)
        internal_ports = AwsTagHelper.wait_for_tags(instance, self._logger).get(Const.INTERNAL_PORTS)
        if internal_ports:
            return "{}.{}.sandbox.com".format(app_name, self._sandbox_id)
        else:
            return None

    @CallsLogger.wrap
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        return Utils.retry_on_exception(func=lambda: self._get_public_dns_name_by_instance_id(instance_id=infra_id),
                                        timeout_in_sec=address_read_timeout,
                                        logger=self._logger,
                                        logger_msg="trying to get public dns for app '{}'.".format(app_name))

    @CallsLogger.wrap
    def get_sandbox_public_dns(self) -> str:

        stack_name = self._session.production_infra_stack_name or self._session.sandbox_stack_name
        try:
            # Get ALB arn
            response = Utils.retry_on_exception(
                func=lambda: self._session.get_cf_client().describe_stack_resource(
                    StackName=stack_name,
                    LogicalResourceId=Const.MAIN_ALB),
                interval=5,
                timeout_in_sec=30,
                logger=self._logger,
                logger_msg='trying to get stack alb resource')
            alb_arn = response['StackResourceDetail']['PhysicalResourceId']

            # Get ALB dns
            response = self._session.get_elb_v2_client().describe_load_balancers(LoadBalancerArns=[alb_arn])
            alb_dns = response['LoadBalancers'][0]['DNSName']
            return alb_dns
        except:
            self._logger.exception('Failed to get {} from stack {}'.format(Const.MAIN_ALB, stack_name))
            return ''

        # response = self._session.get_cf_client().describe_stack_resource(
        #     StackName=self._session.production_infra_stack_name or self._session.sandbox_stack_name,
        #     LogicalResourceId=Const.MAIN_ALB)
        # alb_arn = response['StackResourceDetail']['PhysicalResourceId']
        #
        # # Get ALB dns
        # response = self._session.get_elb_v2_client().describe_load_balancers(LoadBalancerArns=[alb_arn])
        # alb_dns = response['LoadBalancers'][0]['DNSName']
        # return alb_dns

    @CallsLogger.wrap
    def can_access_from_public_address(self, identifier: AppInstanceIdentifier) -> bool:
        # _, item = Utils.retry_on_exception(
        #     func=lambda: self._get_table(sandbox_id=self._sandbox_id),
        #     logger=self._logger,
        #     logger_msg="Cannot get sandbox {} data for instance {} ports".format(self._sandbox_id, logical_id))
        if self._env_type == EnvironmentType.ProductionGreen:
            return False
        for route in self._aws_status_maintainer.get_ingress_routes():
            if route.app_name == identifier.name and \
                    route.app_port == route.listener_port and \
                    not route.path and not route.host and \
                    route.color.lower() == 'blue' and self._session:
                return True

        return False

    def _get_table(self, sandbox_id: str) -> Tuple[any, dict]:
        dynamo_resource = self._session.get_dynamo_resource(default_region=self.default_region)
        table = dynamo_resource.Table(self._table_name)
        item = table.get_item(Key={Const.SANDBOX_ID_TAG: sandbox_id})
        if "Item" not in item:
            raise Exception("dynamodb table is not ready yet")
        return table, item["Item"]

    def _get_public_dns_name_by_instance_id(self, instance_id: str):
        instance = self._session.get_ec2_resource().Instance(instance_id)
        dns = AwsTagHelper.wait_for_tags(instance, self._logger).get(Const.EXTERNAL_ELB_DNS_NAME)
        if dns:
            return dns

        return instance.public_dns_name
