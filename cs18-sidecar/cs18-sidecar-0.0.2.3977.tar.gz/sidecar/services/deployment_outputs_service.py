import json
import shlex
import threading
from logging import Logger
from typing import List

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_instance_service import IAppInstanceService
from sidecar.model.objects import ISidecarConfiguration
from sidecar.services.deployment_outputs_converter import DeploymentOutputsConverter, \
    OutputValueToStringConverterFactory
from sidecar.services.service_updater import IServiceUpdater


class DeploymentOutputsService:

    def __init__(self, logger: Logger,
                 app_instance_service: IAppInstanceService,
                 service_updater: IServiceUpdater,
                 config: ISidecarConfiguration):
        self._service_updater = service_updater
        self._app_instance_service = app_instance_service
        self._config = config
        self._logger = logger
        self._lock = threading.RLock()
        self._output_value_to_str_factory = OutputValueToStringConverterFactory()

    def get_deployment_outputs(self, outputs: List[str]) -> str:
        entity_name_outputs_map = {}
        res = {}
        for output in outputs:
            try:
                entity_name, output_name = self._parse_output_name(output)
                entity_outputs = entity_name_outputs_map.get(entity_name, None)
                if entity_outputs is None:
                    entity_outputs = self._get_outputs(entity_name)
                    entity_name_outputs_map[entity_name] = entity_outputs

                if output_name in entity_outputs:
                    value_json = entity_outputs.get(output_name)
                    res[output] = self._output_value_to_str_factory.convert_to_str(value_json['type'],
                                                                                   value_json['value'])
                else:
                    res[output] = 'Output value not found'
            except Exception as ex:
                self._logger.exception("failed to resolve output: {output}\n{exc}".format(output=output, exc=ex))
                raise ex
        return "\n".join("{}={}".format(k, v) for k, v in res.items())

    def save_application_outputs(self, app_identifier: AppInstanceIdentifier, outputs: str):
        app_name = app_identifier.name
        app_instance_id = app_identifier.infra_id
        try:
            deployment_output = DeploymentOutputsConverter.convert_from_configuration_script(outputs)
        except Exception as exc:
            self._logger.exception(f"application '{app_instance_id}/{app_name}' "
                                   f"deployment output is not valid:\n{outputs}")
            raise exc

        # for debugging
        # self._log_deployment_output_info(f'{app_instance_id}/{app_name}' if app_instance_id else app_name,
        #                                  deployment_output)

        declared_outputs = self._get_application_declared_outputs(app_name)
        self._filter_redundant_deployment_outputs(deployment_output, declared_outputs)

        with self._lock:
            self._app_instance_service.update_deployment_outputs(app_identifier,
                                                                 deployment_output)

    def save_service_outputs(self, service_name: str, output_json: {}):
        try:
            deployment_output = DeploymentOutputsConverter.convert_from_terraform_outputs(output_json)
        except Exception:
            output_str = json.dumps(output_json)
            err = f"service '{service_name}' deployment output is not valid:\n{output_str}"
            self._logger.exception(err)
            raise Exception(err)

        # for debugging
        # self._log_deployment_output_info(service_name, json.dumps(deployment_output))
        declared_outputs = self._get_service_declared_outputs(service_name)
        self._filter_redundant_deployment_outputs(deployment_output, declared_outputs)
        with self._lock:
            self._service_updater.update_deployment_outputs(service_name, deployment_output)

    @staticmethod
    def _filter_redundant_deployment_outputs(deployment_output: dict, declared_outputs: List[str]):
        deployment_output_names = list(deployment_output.keys())
        for deployment_output_name in deployment_output_names:
            if deployment_output_name not in declared_outputs:
                deployment_output.pop(deployment_output_name, None)

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
            raise Exception(f"output '{output}' cannot be resolved")

    def _get_outputs(self, entity_name: str) -> {}:
        if next((service for service in self._config.services if service.name == entity_name), None):
            return self._service_updater.get_deployment_outputs(entity_name)

        if next((app for app in self._config.apps if app.name == entity_name), None):
            return self._app_instance_service.get_deployment_outputs(entity_name)
        else:
            raise Exception(f"could not find application/service with name '{entity_name}'")

    def _log_deployment_output_info(self, entity_name: str, deployment_output: str):
        self._logger.info(f"save deployment output:\nentity name: {entity_name}\noutput: {deployment_output}")
