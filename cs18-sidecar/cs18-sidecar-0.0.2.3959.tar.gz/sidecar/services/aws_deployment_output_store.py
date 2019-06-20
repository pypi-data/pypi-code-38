import json
import shlex
import threading
from logging import Logger
from typing import List

from sidecar.aws_session import AwsSession
from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const
from sidecar.model.objects import ISidecarConfiguration
from sidecar.services.deployment_output_converter import DeploymentOutputConverter
from sidecar.services.deployment_output_store import DeploymentOutputStore


class AwsDeploymentOutputStore(DeploymentOutputStore):

    def __init__(self, logger: Logger,
                 aws_session: AwsSession,
                 status_maintainer: AWSStatusMaintainer,
                 config: ISidecarConfiguration):
        self._config = config
        self._aws_session = aws_session
        self._status_maintainer = status_maintainer
        self._logger = logger
        self._lock = threading.RLock()

    def _get_service_declared_outputs(self, service_name: str) -> List[str]:
        outputs = next((s.outputs for s in self._config.services if s.name == service_name))
        if outputs:
            return outputs
        return []

    def _get_application_declared_outputs(self, application_name: str) -> List[str]:
        outputs = next((a.outputs for a in self._config.apps if a.name == application_name))
        if outputs:
            return outputs
        return []

    @staticmethod
    def _parse_output_name(output: str):
        try:
            split = output.split('.')
            entity_name = split[1]
            output_name = split[2]
            return entity_name, output_name
        except IndexError:
            raise Exception(f"output {output} cannot be resolved")

    def get_deployment_outputs(self, outputs: List[str]) -> str:
        entity_name_outputs_map = {}
        res = {}
        for output in outputs:
            try:
                entity_name, output_name = self._parse_output_name(output)
                entity_outputs = entity_name_outputs_map.get(entity_name, None)
                if entity_outputs is None:
                    entity_outputs = self._status_maintainer.get_deployment_output(entity_name)
                    entity_name_outputs_map[entity_name] = entity_outputs

                res[output] = entity_outputs.get(output_name, 'Output value not found')
            except Exception as ex:
                res[output] = repr(ex)
        return "\n".join("{}={}".format(k, shlex.quote(v)) for k, v in res.items())

    @staticmethod
    def filter_redundant_deployment_outputs(deployment_output: dict, declared_outputs: List[str]):
        deployment_output_names = list(deployment_output.keys())
        for deployment_output_name in deployment_output_names:
            if deployment_output_name not in declared_outputs:
                deployment_output.pop(deployment_output_name, None)

    def save_service_output(self, service_name: str, output_json: {}):
        try:
            deployment_output = DeploymentOutputConverter.convert_from_terraform_output(output_json)
        except Exception:
            output_str = json.dumps(output_json)
            err = f"service '{service_name}' deployment output is not valid:\n{output_str}"
            self._logger.exception(err)
            raise Exception(err)

        self._log_deployment_output(service_name, deployment_output)
        declared_outputs = self._get_service_declared_outputs(service_name)
        self.filter_redundant_deployment_outputs(deployment_output, declared_outputs)
        with self._lock:
            self._status_maintainer.update_service_output(service_name, deployment_output)

    def _log_deployment_output(self, service_name: str, deployment_output: {}):
        output_str = json.dumps(deployment_output, indent=2)
        self._logger.info(f"service '{service_name}' deployment output is:\n{output_str}")

    def save_application_output(self, app_name: str, app_instance_id: str, output: str):
        try:
            deployment_output = DeploymentOutputConverter.convert_from_configuration_script(output)
        except Exception as exc:
            self._logger.exception(f"application '{app_instance_id}/{app_name}' "
                                   f"deployment output is not valid:\n{output}")
            raise exc

        self._logger.info(f"application '{app_instance_id}/{app_name}' deployment output is:\n{deployment_output}")
        declared_outputs = self._get_application_declared_outputs(app_name)
        self.filter_redundant_deployment_outputs(deployment_output, declared_outputs)

        instance = self._get_instance_by_id(instance_id=app_instance_id)
        instance_logical_id = AwsTagHelper.wait_for_tag(instance, Const.INSTANCELOGICALID, self._logger)
        with self._lock:
            self._status_maintainer.update_app_instance_output(instance_logical_id,
                                                               app_instance_id,
                                                               app_name,
                                                               deployment_output)

    def _get_instance_by_id(self, instance_id: str):
        ec2 = self._aws_session.get_ec2_resource()
        return ec2.Instance(instance_id)
