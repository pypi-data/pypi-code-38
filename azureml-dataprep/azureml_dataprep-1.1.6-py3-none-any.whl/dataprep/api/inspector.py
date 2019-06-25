# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.api import EngineAPI
from .engineapi.typedefinitions import (ActivityReference, ExecuteInspectorCommonArguments, ExecuteInspectorsMessageArguments, InspectorArguments)
from typing import Any, Dict, List, Tuple, Union
from uuid import uuid4
import json

_MAX_ROW_COUNT = 2**31 - 1

class _Inspector:
    @classmethod
    def _from_execution(
        cls,
        engine_api: EngineAPI,
        context: ActivityReference,
        inspector: Union[str, InspectorArguments]):
        if isinstance(inspector, str):
            inspector = json.loads(inspector)
        return engine_api.execute_inspector(ExecuteInspectorCommonArguments(
            context=context,
            inspector_arguments=inspector,
            offset=0,
            row_count=_MAX_ROW_COUNT))

class _InspectorBatch:

    # inspector_id corresponds to a GUID that is used to match the requested
    # InspectorArguments as a key and the content in the Inspector as a value 
    # due to objects being unable to be stored as keys for a dictionary in JSON
    @classmethod
    def _from_execution(
        cls,
        engine_api: EngineAPI,
        context: ActivityReference,
        inspectors: Union[str, List[InspectorArguments]]):
        if isinstance(inspectors, str):
            inspectors = json.loads(inspectors)
        request = [ExecuteInspectorsMessageArguments(
            inspector_arguments = ExecuteInspectorCommonArguments(
                context=context,
                inspector_arguments=inspector,
                offset=0,
                row_count=_MAX_ROW_COUNT),
            inspector_id=uuid4()
            ) for inspector in inspectors]
        response = engine_api.execute_inspectors(request)
        result = {}
        for inspector in request:
            result[inspector.inspector_arguments.inspector_arguments] = response[inspector.inspector_id]
        return result
