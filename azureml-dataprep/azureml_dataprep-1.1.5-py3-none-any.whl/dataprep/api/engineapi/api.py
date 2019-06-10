# Copyright (c) Microsoft Corporation. All rights reserved.
# pylint: skip-file
# This file is auto-generated. Do not modify.
from typing import List, Dict
from uuid import uuid4
from .engine import launch_engine
from . import typedefinitions
from .._aml_helper import update_aml_env_vars


_engine_api = None

def get_engine_api():
    global _engine_api
    if not _engine_api:
        _engine_api = EngineAPI()
        from .._dataset_resolver import register_dataset_resolver
        register_dataset_resolver()
    return _engine_api


def kill_engine_api():
    global _engine_api
    if _engine_api:
        _engine_api._engine.close()
        _engine_api = None


class EngineAPI:
    def __init__(self):
        self._engine = launch_engine()

    @update_aml_env_vars(get_engine_api)
    def add_block_to_list(self, message_args: typedefinitions.AddBlockToListMessageArguments) -> typedefinitions.AnonymousBlockData:
        response = self._engine.send_message('Engine.AddBlockToList', message_args)
        return typedefinitions.AnonymousBlockData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def add_temporary_secrets(self, message_args: Dict[str, str]) -> None:
        response = self._engine.send_message('Engine.AddTemporarySecrets', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def anonymous_data_source_prose_suggestions(self, message_args: typedefinitions.AnonymousDataSourceProseSuggestionsMessageArguments) -> typedefinitions.DataSourceProperties:
        response = self._engine.send_message('GetProseAnonymousDataSourcePropertiesSuggestion', message_args)
        return typedefinitions.DataSourceProperties.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def anonymous_send_message_to_block(self, message_args: typedefinitions.AnonymousSendMessageToBlockMessageArguments) -> typedefinitions.AnonymousSendMessageToBlockMessageResponseData:
        response = self._engine.send_message('Engine.SendMessageToBlock', message_args)
        return typedefinitions.AnonymousSendMessageToBlockMessageResponseData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def create_anonymous_reference(self, message_args: typedefinitions.CreateAnonymousReferenceMessageArguments) -> typedefinitions.ActivityReference:
        response = self._engine.send_message('Engine.CreateAnonymousReference', message_args)
        return typedefinitions.ActivityReference.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def execute_anonymous_blocks(self, message_args: typedefinitions.ExecuteAnonymousBlocksMessageArguments) -> None:
        response = self._engine.send_message('Engine.ExecuteActivity', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def execute_inspector(self, message_args: typedefinitions.ExecuteInspectorCommonArguments) -> typedefinitions.ExecuteInspectorCommonResponse:
        response = self._engine.send_message('Engine.ExecuteInspector', message_args)
        return typedefinitions.ExecuteInspectorCommonResponse.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def export_script(self, message_args: typedefinitions.ExportScriptMessageArguments) -> List[typedefinitions.SecretData]:
        response = self._engine.send_message('Project.ExportScript', message_args)
        return [typedefinitions.SecretData.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_activity(self, message_args: str) -> typedefinitions.AnonymousActivityData:
        response = self._engine.send_message('Engine.GetActivity', message_args)
        return typedefinitions.AnonymousActivityData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_data(self, message_args: typedefinitions.GetDataMessageArguments) -> typedefinitions.GetDataMessageResponse:
        response = self._engine.send_message('Engine.GetData', message_args)
        return typedefinitions.GetDataMessageResponse.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_secrets(self, message_args: typedefinitions.GetSecretsMessageArguments) -> List[typedefinitions.SecretData]:
        response = self._engine.send_message('Engine.GetSecrets', message_args)
        return [typedefinitions.SecretData.from_pod(i) if i is not None else None for i in response] if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def get_source_data_hash(self, message_args: typedefinitions.GetSourceDataHashMessageArguments) -> str:
        response = self._engine.send_message('Engine.GetSourceDataHash', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def infer_types(self, message_args: List[typedefinitions.AnonymousBlockData]) -> Dict[str, typedefinitions.FieldInference]:
        response = self._engine.send_message('Engine.InferTypes', message_args)
        return {k: typedefinitions.FieldInference.from_pod(v) if v is not None else None for k, v in response.items()} if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def load_activity_from_json(self, message_args: str) -> typedefinitions.AnonymousActivityData:
        response = self._engine.send_message('Engine.LoadProjectFromJson', message_args)
        return typedefinitions.AnonymousActivityData.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def register_secret(self, message_args: typedefinitions.RegisterSecretMessageArguments) -> typedefinitions.Secret:
        response = self._engine.send_message('SecretManager.RegisterSecrert', message_args)
        return typedefinitions.Secret.from_pod(response) if response is not None else None

    @update_aml_env_vars(get_engine_api)
    def save_activity_from_data(self, message_args: typedefinitions.SaveActivityFromDataMessageArguments) -> None:
        response = self._engine.send_message('Project.SaveAnonymous', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def save_activity_to_json(self, message_args: typedefinitions.AnonymousActivityData) -> str:
        response = self._engine.send_message('Project.SaveAnonymousToJson', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_aml_auth(self, message_args: typedefinitions.SetAmlAuthMessageArgument) -> None:
        response = self._engine.send_message('Engine.SetAmlAuth', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_executor(self, message_args: typedefinitions.ExecutorType) -> None:
        response = self._engine.send_message('Engine.SetExecutor', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_host_channel_port(self, message_args: int) -> None:
        response = self._engine.send_message('Engine.SetHostChannelPort', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def set_host_secret(self, message_args: str) -> None:
        response = self._engine.send_message('Engine.SetHostSecret', message_args)
        return response

    @update_aml_env_vars(get_engine_api)
    def update_environment_variable(self, message_args: Dict[str, str]) -> None:
        response = self._engine.send_message('Engine.UpdateEnvironmentVariable', message_args)
        return response
