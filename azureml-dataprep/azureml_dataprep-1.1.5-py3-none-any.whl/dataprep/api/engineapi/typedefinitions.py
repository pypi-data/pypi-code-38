# Copyright (c) Microsoft Corporation. All rights reserved.
# pylint: skip-file
# This file is auto-generated. Do not modify.
# 'pod' stands for 'plain old data' a C++ concept. Practically it's a nested Dict that can contain some arbitrary JSON.
from typing import List, Dict
from enum import Enum
from uuid import UUID
import json


def to_dprep_pod(obj):
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, List):
        return [to_dprep_pod(v) for v in obj]
    if hasattr(obj, 'to_pod'):
        return obj.to_pod()
    if hasattr(obj, '__dict__'):
        return {k.lstrip('_'): to_dprep_pod(v) for k, v in vars(obj).items()}
    return obj


class PropertyValues:
    """Empty class"""

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AnonymousBlockData:
    def __init__(self,
        arguments: 'PropertyValues' = None,
        id: UUID = None,
        local_data: 'PropertyValues' = None,
        type: str = None,
    ):
        self._pod = {
            'arguments': to_dprep_pod(arguments),
            'id': to_dprep_pod(id),
            'localData': to_dprep_pod(local_data),
            'type': to_dprep_pod(type),
        }

    @property
    def arguments(self) -> 'PropertyValues':
        return PropertyValues.from_pod(self._pod['arguments']) if self._pod['arguments'] is not None else None

    @arguments.setter
    def arguments(self, value: 'PropertyValues'):
        self._pod['arguments'] = to_dprep_pod(value)

    @property
    def id(self) -> UUID:
        return UUID(self._pod['id']) if self._pod['id'] is not None else None

    @id.setter
    def id(self, value: UUID):
        self._pod['id'] = to_dprep_pod(value)

    @property
    def local_data(self) -> 'PropertyValues':
        return PropertyValues.from_pod(self._pod['localData']) if self._pod['localData'] is not None else None

    @local_data.setter
    def local_data(self, value: 'PropertyValues'):
        self._pod['localData'] = to_dprep_pod(value)

    @property
    def type(self) -> str:
        return self._pod['type']

    @type.setter
    def type(self, value: str):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class BlockArguments:
    def __init__(self,
        arguments: 'PropertyValues' = None,
        block_type: str = None,
        local_data: 'PropertyValues' = None,
    ):
        self._pod = {
            'arguments': to_dprep_pod(arguments),
            'blockType': to_dprep_pod(block_type),
            'localData': to_dprep_pod(local_data),
        }

    @property
    def arguments(self) -> 'PropertyValues':
        return PropertyValues.from_pod(self._pod['arguments']) if self._pod['arguments'] is not None else None

    @arguments.setter
    def arguments(self, value: 'PropertyValues'):
        self._pod['arguments'] = to_dprep_pod(value)

    @property
    def block_type(self) -> str:
        return self._pod['blockType']

    @block_type.setter
    def block_type(self, value: str):
        self._pod['blockType'] = to_dprep_pod(value)

    @property
    def local_data(self) -> 'PropertyValues':
        return PropertyValues.from_pod(self._pod['localData']) if self._pod['localData'] is not None else None

    @local_data.setter
    def local_data(self, value: 'PropertyValues'):
        self._pod['localData'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AddBlockToListMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None,
        new_block_arguments: 'BlockArguments' = None,
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
            'newBlockArguments': to_dprep_pod(new_block_arguments),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @property
    def new_block_arguments(self) -> 'BlockArguments':
        return BlockArguments.from_pod(self._pod['newBlockArguments']) if self._pod['newBlockArguments'] is not None else None

    @new_block_arguments.setter
    def new_block_arguments(self, value: 'BlockArguments'):
        self._pod['newBlockArguments'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class FileEncoding(Enum):
    UTF8 = 0
    ISO88591 = 1
    LATIN1 = 2
    ASCII = 3
    UTF16 = 4
    UTF32 = 5
    UTF8BOM = 6
    WINDOWS1252 = 7


class AnonymousDataSourceProseSuggestionsMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None,
        path_column_name: str = None,
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
            'pathColumnName': to_dprep_pod(path_column_name),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @property
    def path_column_name(self) -> str:
        return self._pod['pathColumnName']

    @path_column_name.setter
    def path_column_name(self, value: str):
        self._pod['pathColumnName'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DataSourceProperties:
    def __init__(self,
        column_count: int = None,
        column_positions: List[int] = None,
        data_source_type: str = None,
        delimiter: str = None,
        encoding: object = None,
        promote_headers: bool = None,
        skip_lines_count: int = None,
    ):
        self._pod = {
            'columnCount': to_dprep_pod(column_count),
            'columnPositions': to_dprep_pod(column_positions),
            'dataSourceType': to_dprep_pod(data_source_type),
            'delimiter': to_dprep_pod(delimiter),
            'encoding': to_dprep_pod(encoding),
            'promoteHeaders': to_dprep_pod(promote_headers),
            'skipLinesCount': to_dprep_pod(skip_lines_count),
        }

    @property
    def column_count(self) -> int:
        return self._pod['columnCount']

    @column_count.setter
    def column_count(self, value: int):
        self._pod['columnCount'] = to_dprep_pod(value)

    @property
    def column_positions(self) -> List[int]:
        return [i for i in self._pod['columnPositions']] if self._pod['columnPositions'] is not None else None

    @column_positions.setter
    def column_positions(self, value: List[int]):
        self._pod['columnPositions'] = to_dprep_pod(value)

    @property
    def data_source_type(self) -> str:
        return self._pod['dataSourceType']

    @data_source_type.setter
    def data_source_type(self, value: str):
        self._pod['dataSourceType'] = to_dprep_pod(value)

    @property
    def delimiter(self) -> str:
        return self._pod['delimiter']

    @delimiter.setter
    def delimiter(self, value: str):
        self._pod['delimiter'] = to_dprep_pod(value)

    @property
    def encoding(self) -> object:
        return self._pod['encoding']

    @encoding.setter
    def encoding(self, value: object):
        self._pod['encoding'] = to_dprep_pod(value)

    @property
    def promote_headers(self) -> bool:
        return self._pod['promoteHeaders']

    @promote_headers.setter
    def promote_headers(self, value: bool):
        self._pod['promoteHeaders'] = to_dprep_pod(value)

    @property
    def skip_lines_count(self) -> int:
        return self._pod['skipLinesCount']

    @skip_lines_count.setter
    def skip_lines_count(self, value: int):
        self._pod['skipLinesCount'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AnonymousSendMessageToBlockMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None,
        message: str = None,
        message_arguments: Dict[str, object] = None,
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
            'message': to_dprep_pod(message),
            'messageArguments': to_dprep_pod(message_arguments),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @property
    def message(self) -> str:
        return self._pod['message']

    @message.setter
    def message(self, value: str):
        self._pod['message'] = to_dprep_pod(value)

    @property
    def message_arguments(self) -> Dict[str, object]:
        return {k: v for k, v in self._pod['messageArguments'].items()} if self._pod['messageArguments'] is not None else None

    @message_arguments.setter
    def message_arguments(self, value: Dict[str, object]):
        self._pod['messageArguments'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AnonymousSendMessageToBlockMessageResponseData:
    def __init__(self,
        data: Dict[str, object] = None
    ):
        self._pod = {
            'data': to_dprep_pod(data),
        }

    @property
    def data(self) -> Dict[str, object]:
        return {k: v for k, v in self._pod['data'].items()} if self._pod['data'] is not None else None

    @data.setter
    def data(self, value: Dict[str, object]):
        self._pod['data'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class CreateAnonymousReferenceMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ActivityReferenceType(Enum):
    INTERNAL = 0
    FILE = 1
    ANONYMOUS = 2


class PropertyType(Enum):
    CHARACTER = 0
    STRING = 1
    INT = 2
    DECIMAL = 3
    BOOLEAN = 4
    COLUMN = 5
    ENUM = 6
    COMPOUNDPROPERTY = 7
    TEXTAREA = 8
    URL = 9
    ROWCOUNT = 10
    DATASOURCE = 11
    DATACONNECTION = 12
    CODEBLOCK = 13
    CODEEXPRESSION = 14
    PASSWORD = 15
    DATABASEAUTH = 16
    AZUREFILE = 17
    OUTPUTFILE = 18
    DATABASEDATASOURCE = 19
    DATETIME = 20
    ACTIVITYREFERENCE = 21
    SAMPLEGENERATORID = 22
    PROGRAMSTEP = 23
    BINARY = 24
    OUTPUTDIRECTORY = 25
    EXPRESSION = 26
    LARIATVALUE = 27


class DomainType(Enum):
    COMPOUNDPROPERTY = 0
    ENUMVALUES = 1
    EXISTINGCOLUMN = 2
    VALIDCOLUMNNAME = 3
    VALUERANGE = 4
    CODELANGUAGE = 5
    VALUESFROMSET = 6
    FILESOURCES = 7
    OUTPUTFILETYPE = 8
    DATETIMEFORMAT = 9
    ALLOWEDFILETARGETS = 10
    ONLYREMOTEGENERATORS = 11
    COLUMNSSELECTOR = 12


class PropertyDomain:
    def __init__(self,
        details: object = None,
        type: 'DomainType' = None,
    ):
        self._pod = {
            'details': to_dprep_pod(details),
            'type': to_dprep_pod(type),
        }

    @property
    def details(self) -> object:
        return self._pod['details']

    @details.setter
    def details(self, value: object):
        self._pod['details'] = to_dprep_pod(value)

    @property
    def type(self) -> 'DomainType':
        return DomainType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'DomainType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class MultiValuedPropertyDetails:
    def __init__(self,
        is_ordered: bool = None
    ):
        self._pod = {
            'isOrdered': to_dprep_pod(is_ordered),
        }

    @property
    def is_ordered(self) -> bool:
        return self._pod['isOrdered']

    @is_ordered.setter
    def is_ordered(self, value: bool):
        self._pod['isOrdered'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class PropertyOrigin(Enum):
    SYSTEM = 0
    USER = 1
    GENERATED = 2


class TelemetryStrategy(Enum):
    KEEP = 0
    ANONYMIZE = 1
    OMIT = 2


class PropertyReference:
    def __init__(self,
        property_path: List[str] = None
    ):
        self._pod = {
            'propertyPath': to_dprep_pod(property_path),
        }

    @property
    def property_path(self) -> List[str]:
        return [i for i in self._pod['propertyPath']] if self._pod['propertyPath'] is not None else None

    @property_path.setter
    def property_path(self, value: List[str]):
        self._pod['propertyPath'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class Op(Enum):
    EQUALS = 0
    DOESNOTEQUAL = 1
    CACHERTYPEIS = 2


class Condition:
    def __init__(self,
        comparison: 'Op' = None,
        prop: 'PropertyReference' = None,
        value: object = None,
    ):
        self._pod = {
            'comparison': to_dprep_pod(comparison),
            'property': to_dprep_pod(prop),
            'value': to_dprep_pod(value),
        }

    @property
    def comparison(self) -> 'Op':
        return Op(self._pod['comparison']) if self._pod['comparison'] is not None else None

    @comparison.setter
    def comparison(self, value: 'Op'):
        self._pod['comparison'] = to_dprep_pod(value)

    @property
    def prop(self) -> 'PropertyReference':
        return PropertyReference.from_pod(self._pod['property']) if self._pod['property'] is not None else None

    @prop.setter
    def prop(self, value: 'PropertyReference'):
        self._pod['property'] = to_dprep_pod(value)

    @property
    def value(self) -> object:
        return self._pod['value']

    @value.setter
    def value(self, value: object):
        self._pod['value'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AggregationType(Enum):
    AND = 0
    OR = 1


class Aggregate:
    def __init__(self,
        clauses: List['Clause'] = None,
        type: 'AggregationType' = None,
    ):
        self._pod = {
            'clauses': to_dprep_pod(clauses),
            'type': to_dprep_pod(type),
        }

    @property
    def clauses(self) -> List['Clause']:
        return [Clause.from_pod(i) if i is not None else None for i in self._pod['clauses']] if self._pod['clauses'] is not None else None

    @clauses.setter
    def clauses(self, value: List['Clause']):
        self._pod['clauses'] = to_dprep_pod(value)

    @property
    def type(self) -> 'AggregationType':
        return AggregationType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'AggregationType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class Clause:
    def __init__(self,
        aggregate: 'Aggregate' = None,
        condition: 'Condition' = None,
    ):
        self._pod = {
            'aggregate': to_dprep_pod(aggregate),
            'condition': to_dprep_pod(condition),
        }

    @property
    def aggregate(self) -> 'Aggregate':
        return Aggregate.from_pod(self._pod['aggregate']) if self._pod['aggregate'] is not None else None

    @aggregate.setter
    def aggregate(self, value: 'Aggregate'):
        self._pod['aggregate'] = to_dprep_pod(value)

    @property
    def condition(self) -> 'Condition':
        return Condition.from_pod(self._pod['condition']) if self._pod['condition'] is not None else None

    @condition.setter
    def condition(self, value: 'Condition'):
        self._pod['condition'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class PropertyDescription:
    def __init__(self,
        condition: 'Clause' = None,
        default_value: object = None,
        documentation: str = None,
        domain: 'PropertyDomain' = None,
        initialize_from_property: str = None,
        is_required: bool = None,
        multiple_values: bool = None,
        multi_value_details: 'MultiValuedPropertyDetails' = None,
        name: str = None,
        origin: 'PropertyOrigin' = None,
        telemetry_strategy: 'TelemetryStrategy' = None,
        type: 'PropertyType' = None,
    ):
        self._pod = {
            'condition': to_dprep_pod(condition),
            'defaultValue': to_dprep_pod(default_value),
            'documentation': to_dprep_pod(documentation),
            'domain': to_dprep_pod(domain),
            'initializeFromProperty': to_dprep_pod(initialize_from_property),
            'isRequired': to_dprep_pod(is_required),
            'multipleValues': to_dprep_pod(multiple_values),
            'multiValueDetails': to_dprep_pod(multi_value_details),
            'name': to_dprep_pod(name),
            'origin': to_dprep_pod(origin),
            'telemetryStrategy': to_dprep_pod(telemetry_strategy),
            'type': to_dprep_pod(type),
        }

    @property
    def condition(self) -> 'Clause':
        return Clause.from_pod(self._pod['condition']) if self._pod['condition'] is not None else None

    @condition.setter
    def condition(self, value: 'Clause'):
        self._pod['condition'] = to_dprep_pod(value)

    @property
    def default_value(self) -> object:
        return self._pod['defaultValue']

    @default_value.setter
    def default_value(self, value: object):
        self._pod['defaultValue'] = to_dprep_pod(value)

    @property
    def documentation(self) -> str:
        return self._pod['documentation']

    @documentation.setter
    def documentation(self, value: str):
        self._pod['documentation'] = to_dprep_pod(value)

    @property
    def domain(self) -> 'PropertyDomain':
        return PropertyDomain.from_pod(self._pod['domain']) if self._pod['domain'] is not None else None

    @domain.setter
    def domain(self, value: 'PropertyDomain'):
        self._pod['domain'] = to_dprep_pod(value)

    @property
    def initialize_from_property(self) -> str:
        return self._pod['initializeFromProperty']

    @initialize_from_property.setter
    def initialize_from_property(self, value: str):
        self._pod['initializeFromProperty'] = to_dprep_pod(value)

    @property
    def is_required(self) -> bool:
        return self._pod['isRequired']

    @is_required.setter
    def is_required(self, value: bool):
        self._pod['isRequired'] = to_dprep_pod(value)

    @property
    def multiple_values(self) -> bool:
        return self._pod['multipleValues']

    @multiple_values.setter
    def multiple_values(self, value: bool):
        self._pod['multipleValues'] = to_dprep_pod(value)

    @property
    def multi_value_details(self) -> 'MultiValuedPropertyDetails':
        return MultiValuedPropertyDetails.from_pod(self._pod['multiValueDetails']) if self._pod['multiValueDetails'] is not None else None

    @multi_value_details.setter
    def multi_value_details(self, value: 'MultiValuedPropertyDetails'):
        self._pod['multiValueDetails'] = to_dprep_pod(value)

    @property
    def name(self) -> str:
        return self._pod['name']

    @name.setter
    def name(self, value: str):
        self._pod['name'] = to_dprep_pod(value)

    @property
    def origin(self) -> 'PropertyOrigin':
        return PropertyOrigin(self._pod['origin']) if self._pod['origin'] is not None else None

    @origin.setter
    def origin(self, value: 'PropertyOrigin'):
        self._pod['origin'] = to_dprep_pod(value)

    @property
    def telemetry_strategy(self) -> 'TelemetryStrategy':
        return TelemetryStrategy(self._pod['telemetryStrategy']) if self._pod['telemetryStrategy'] is not None else None

    @telemetry_strategy.setter
    def telemetry_strategy(self, value: 'TelemetryStrategy'):
        self._pod['telemetryStrategy'] = to_dprep_pod(value)

    @property
    def type(self) -> 'PropertyType':
        return PropertyType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'PropertyType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ReferenceStepFallback(Enum):
    FAIL = 0
    LAST = 1


class DataEffect(Enum):
    NONE = 0
    UNSPECIFIEDSCHEMACHANGE = 1
    COLUMNSCHEMACHANGE = 2
    ADDSCOLUMNS = 3
    REMOVESCOLUMNS = 4
    TRANSFORMSCOLUMNS = 5
    REMOVESROWS = 6
    DATAWRITER = 7
    DATAREADER = 8
    STREAMLOADER = 9


class DataEffectDetails:
    def __init__(self,
        data_effect: 'DataEffect' = None
    ):
        self._pod = {
            'dataEffect': to_dprep_pod(data_effect),
        }

    @property
    def data_effect(self) -> 'DataEffect':
        return DataEffect(self._pod['dataEffect']) if self._pod['dataEffect'] is not None else None

    @data_effect.setter
    def data_effect(self, value: 'DataEffect'):
        self._pod['dataEffect'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ProgramStepDescription:
    def __init__(self,
        data_effect_details: 'DataEffectDetails' = None,
        property_descriptions: List['PropertyDescription'] = None,
        type: str = None,
    ):
        self._pod = {
            'dataEffectDetails': to_dprep_pod(data_effect_details),
            'propertyDescriptions': to_dprep_pod(property_descriptions),
            'type': to_dprep_pod(type),
        }

    @property
    def data_effect_details(self) -> 'DataEffectDetails':
        return DataEffectDetails.from_pod(self._pod['dataEffectDetails']) if self._pod['dataEffectDetails'] is not None else None

    @data_effect_details.setter
    def data_effect_details(self, value: 'DataEffectDetails'):
        self._pod['dataEffectDetails'] = to_dprep_pod(value)

    @property
    def property_descriptions(self) -> List['PropertyDescription']:
        return [PropertyDescription.from_pod(i) if i is not None else None for i in self._pod['propertyDescriptions']] if self._pod['propertyDescriptions'] is not None else None

    @property_descriptions.setter
    def property_descriptions(self, value: List['PropertyDescription']):
        self._pod['propertyDescriptions'] = to_dprep_pod(value)

    @property
    def type(self) -> str:
        return self._pod['type']

    @type.setter
    def type(self, value: str):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ProgramStep:
    def __init__(self,
        arguments: 'PropertyValues' = None,
        data_effect_details: 'DataEffectDetails' = None,
        description: 'ProgramStepDescription' = None,
        id: UUID = None,
        property_descriptions: List['PropertyDescription'] = None,
        type: str = None,
    ):
        self._pod = {
            'arguments': to_dprep_pod(arguments),
            'dataEffectDetails': to_dprep_pod(data_effect_details),
            'description': to_dprep_pod(description),
            'id': to_dprep_pod(id),
            'propertyDescriptions': to_dprep_pod(property_descriptions),
            'type': to_dprep_pod(type),
        }

    @property
    def arguments(self) -> 'PropertyValues':
        return PropertyValues.from_pod(self._pod['arguments']) if self._pod['arguments'] is not None else None

    @arguments.setter
    def arguments(self, value: 'PropertyValues'):
        self._pod['arguments'] = to_dprep_pod(value)

    @property
    def data_effect_details(self) -> 'DataEffectDetails':
        return DataEffectDetails.from_pod(self._pod['dataEffectDetails']) if self._pod['dataEffectDetails'] is not None else None

    @data_effect_details.setter
    def data_effect_details(self, value: 'DataEffectDetails'):
        self._pod['dataEffectDetails'] = to_dprep_pod(value)

    @property
    def description(self) -> 'ProgramStepDescription':
        return ProgramStepDescription.from_pod(self._pod['description']) if self._pod['description'] is not None else None

    @description.setter
    def description(self, value: 'ProgramStepDescription'):
        self._pod['description'] = to_dprep_pod(value)

    @property
    def id(self) -> UUID:
        return UUID(self._pod['id']) if self._pod['id'] is not None else None

    @id.setter
    def id(self, value: UUID):
        self._pod['id'] = to_dprep_pod(value)

    @property
    def property_descriptions(self) -> List['PropertyDescription']:
        return [PropertyDescription.from_pod(i) if i is not None else None for i in self._pod['propertyDescriptions']] if self._pod['propertyDescriptions'] is not None else None

    @property_descriptions.setter
    def property_descriptions(self, value: List['PropertyDescription']):
        self._pod['propertyDescriptions'] = to_dprep_pod(value)

    @property
    def type(self) -> str:
        return self._pod['type']

    @type.setter
    def type(self, value: str):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class StepReference:
    def __init__(self,
        fallback: 'ReferenceStepFallback' = None,
        referenced_step_id: UUID = None,
    ):
        self._pod = {
            'fallback': to_dprep_pod(fallback),
            'referencedStepId': to_dprep_pod(referenced_step_id),
        }

    @property
    def fallback(self) -> 'ReferenceStepFallback':
        return ReferenceStepFallback(self._pod['fallback']) if self._pod['fallback'] is not None else None

    @fallback.setter
    def fallback(self, value: 'ReferenceStepFallback'):
        self._pod['fallback'] = to_dprep_pod(value)

    @property
    def referenced_step_id(self) -> UUID:
        return UUID(self._pod['referencedStepId']) if self._pod['referencedStepId'] is not None else None

    @referenced_step_id.setter
    def referenced_step_id(self, value: UUID):
        self._pod['referencedStepId'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ActivityReference:
    def __init__(self,
        anonymous_steps: List['ProgramStep'] = None,
        reference_container_path: str = None,
        referenced_step: 'StepReference' = None,
        reference_type: 'ActivityReferenceType' = None,
    ):
        self._pod = {
            'anonymousSteps': to_dprep_pod(anonymous_steps),
            'referenceContainerPath': to_dprep_pod(reference_container_path),
            'referencedStep': to_dprep_pod(referenced_step),
            'referenceType': to_dprep_pod(reference_type),
        }

    @property
    def anonymous_steps(self) -> List['ProgramStep']:
        return [ProgramStep.from_pod(i) if i is not None else None for i in self._pod['anonymousSteps']] if self._pod['anonymousSteps'] is not None else None

    @anonymous_steps.setter
    def anonymous_steps(self, value: List['ProgramStep']):
        self._pod['anonymousSteps'] = to_dprep_pod(value)

    @property
    def reference_container_path(self) -> str:
        return self._pod['referenceContainerPath']

    @reference_container_path.setter
    def reference_container_path(self, value: str):
        self._pod['referenceContainerPath'] = to_dprep_pod(value)

    @property
    def referenced_step(self) -> 'StepReference':
        return StepReference.from_pod(self._pod['referencedStep']) if self._pod['referencedStep'] is not None else None

    @referenced_step.setter
    def referenced_step(self, value: 'StepReference'):
        self._pod['referencedStep'] = to_dprep_pod(value)

    @property
    def reference_type(self) -> 'ActivityReferenceType':
        return ActivityReferenceType(self._pod['referenceType']) if self._pod['referenceType'] is not None else None

    @reference_type.setter
    def reference_type(self, value: 'ActivityReferenceType'):
        self._pod['referenceType'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ExecuteAnonymousBlocksMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class InspectorArguments:
    def __init__(self,
        arguments: 'PropertyValues' = None,
        inspector_type: str = None,
    ):
        self._pod = {
            'arguments': to_dprep_pod(arguments),
            'inspectorType': to_dprep_pod(inspector_type),
        }

    @property
    def arguments(self) -> 'PropertyValues':
        return PropertyValues.from_pod(self._pod['arguments']) if self._pod['arguments'] is not None else None

    @arguments.setter
    def arguments(self, value: 'PropertyValues'):
        self._pod['arguments'] = to_dprep_pod(value)

    @property
    def inspector_type(self) -> str:
        return self._pod['inspectorType']

    @inspector_type.setter
    def inspector_type(self, value: str):
        self._pod['inspectorType'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class FieldType(Enum):
    STRING = 0
    BOOLEAN = 1
    INTEGER = 2
    DECIMAL = 3
    DATE = 4
    UNKNOWN = 5
    ERROR = 6
    NULL = 7
    DATAROW = 8
    LIST = 9
    STREAM = 10


class ColumnDefinition:
    def __init__(self,
        id: str = None,
        type: 'FieldType' = None,
    ):
        self._pod = {
            'id': to_dprep_pod(id),
            'type': to_dprep_pod(type),
        }

    @property
    def id(self) -> str:
        return self._pod['id']

    @id.setter
    def id(self, value: str):
        self._pod['id'] = to_dprep_pod(value)

    @property
    def type(self) -> 'FieldType':
        return FieldType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'FieldType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DataField:
    def __init__(self,
        type: 'FieldType' = None,
        value: object = None,
    ):
        self._pod = {
            'type': to_dprep_pod(type),
            'value': to_dprep_pod(value),
        }

    @property
    def type(self) -> 'FieldType':
        return FieldType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'FieldType'):
        self._pod['type'] = to_dprep_pod(value)

    @property
    def value(self) -> object:
        return self._pod['value']

    @value.setter
    def value(self, value: object):
        self._pod['value'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ExecuteInspectorCommonArguments:
    def __init__(self,
        context: 'ActivityReference' = None,
        inspector_arguments: 'InspectorArguments' = None,
        offset: int = None,
        row_count: int = None,
    ):
        self._pod = {
            'context': to_dprep_pod(context),
            'inspectorArguments': to_dprep_pod(inspector_arguments),
            'offset': to_dprep_pod(offset),
            'rowCount': to_dprep_pod(row_count),
        }

    @property
    def context(self) -> 'ActivityReference':
        return ActivityReference.from_pod(self._pod['context']) if self._pod['context'] is not None else None

    @context.setter
    def context(self, value: 'ActivityReference'):
        self._pod['context'] = to_dprep_pod(value)

    @property
    def inspector_arguments(self) -> 'InspectorArguments':
        return InspectorArguments.from_pod(self._pod['inspectorArguments']) if self._pod['inspectorArguments'] is not None else None

    @inspector_arguments.setter
    def inspector_arguments(self, value: 'InspectorArguments'):
        self._pod['inspectorArguments'] = to_dprep_pod(value)

    @property
    def offset(self) -> int:
        return self._pod['offset']

    @offset.setter
    def offset(self, value: int):
        self._pod['offset'] = to_dprep_pod(value)

    @property
    def row_count(self) -> int:
        return self._pod['rowCount']

    @row_count.setter
    def row_count(self, value: int):
        self._pod['rowCount'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class RowsData:
    def __init__(self,
        rows: List[List['DataField']] = None
    ):
        self._pod = {
            'rows': to_dprep_pod(rows),
        }

    @property
    def rows(self) -> List[List['DataField']]:
        return [[DataField.from_pod(i) if i is not None else None for i in i] if i is not None else None for i in self._pod['rows']] if self._pod['rows'] is not None else None

    @rows.setter
    def rows(self, value: List[List['DataField']]):
        self._pod['rows'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ExecuteInspectorCommonResponse:
    def __init__(self,
        column_definitions: List['ColumnDefinition'] = None,
        rows_data: 'RowsData' = None,
    ):
        self._pod = {
            'columnDefinitions': to_dprep_pod(column_definitions),
            'rowsData': to_dprep_pod(rows_data),
        }

    @property
    def column_definitions(self) -> List['ColumnDefinition']:
        return [ColumnDefinition.from_pod(i) if i is not None else None for i in self._pod['columnDefinitions']] if self._pod['columnDefinitions'] is not None else None

    @column_definitions.setter
    def column_definitions(self, value: List['ColumnDefinition']):
        self._pod['columnDefinitions'] = to_dprep_pod(value)

    @property
    def rows_data(self) -> 'RowsData':
        return RowsData.from_pod(self._pod['rowsData']) if self._pod['rowsData'] is not None else None

    @rows_data.setter
    def rows_data(self, value: 'RowsData'):
        self._pod['rowsData'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class PropertyOverride:
    def __init__(self,
        activity_reference: 'ActivityReference' = None,
        expected_value: object = None,
        override_value: object = None,
        property_domain: 'PropertyDomain' = None,
        property_name: str = None,
        property_type: 'PropertyType' = None,
    ):
        self._pod = {
            'activityReference': to_dprep_pod(activity_reference),
            'expectedValue': to_dprep_pod(expected_value),
            'overrideValue': to_dprep_pod(override_value),
            'propertyDomain': to_dprep_pod(property_domain),
            'propertyName': to_dprep_pod(property_name),
            'propertyType': to_dprep_pod(property_type),
        }

    @property
    def activity_reference(self) -> 'ActivityReference':
        return ActivityReference.from_pod(self._pod['activityReference']) if self._pod['activityReference'] is not None else None

    @activity_reference.setter
    def activity_reference(self, value: 'ActivityReference'):
        self._pod['activityReference'] = to_dprep_pod(value)

    @property
    def expected_value(self) -> object:
        return self._pod['expectedValue']

    @expected_value.setter
    def expected_value(self, value: object):
        self._pod['expectedValue'] = to_dprep_pod(value)

    @property
    def override_value(self) -> object:
        return self._pod['overrideValue']

    @override_value.setter
    def override_value(self, value: object):
        self._pod['overrideValue'] = to_dprep_pod(value)

    @property
    def property_domain(self) -> 'PropertyDomain':
        return PropertyDomain.from_pod(self._pod['propertyDomain']) if self._pod['propertyDomain'] is not None else None

    @property_domain.setter
    def property_domain(self, value: 'PropertyDomain'):
        self._pod['propertyDomain'] = to_dprep_pod(value)

    @property
    def property_name(self) -> str:
        return self._pod['propertyName']

    @property_name.setter
    def property_name(self, value: str):
        self._pod['propertyName'] = to_dprep_pod(value)

    @property
    def property_type(self) -> 'PropertyType':
        return PropertyType(self._pod['propertyType']) if self._pod['propertyType'] is not None else None

    @property_type.setter
    def property_type(self, value: 'PropertyType'):
        self._pod['propertyType'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ExportScriptFormat(Enum):
    PYTHONSCRIPT = 0
    PYTHONNOTEBOOK = 1
    PYSPARK = 2
    LARIAT = 3
    PYTHONDATAFRAMELOADER = 4
    PYSPARKDATAFRAMELOADER = 5
    PYTHONRUNFUNCTION = 6
    PYSPARKRUNFUNCTION = 7
    PYSPARKGETLARIATDATASETFUNCTION = 8


class SecretData:
    def __init__(self,
        is_available: bool = None,
        key: str = None,
        value: str = None,
    ):
        self._pod = {
            'isAvailable': to_dprep_pod(is_available),
            'key': to_dprep_pod(key),
            'value': to_dprep_pod(value),
        }

    @property
    def is_available(self) -> bool:
        return self._pod['isAvailable']

    @is_available.setter
    def is_available(self, value: bool):
        self._pod['isAvailable'] = to_dprep_pod(value)

    @property
    def key(self) -> str:
        return self._pod['key']

    @key.setter
    def key(self, value: str):
        self._pod['key'] = to_dprep_pod(value)

    @property
    def value(self) -> str:
        return self._pod['value']

    @value.setter
    def value(self, value: str):
        self._pod['value'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ExportScriptMessageArguments:
    def __init__(self,
        activity_reference: 'ActivityReference' = None,
        format: 'ExportScriptFormat' = None,
        overrides: List['PropertyOverride'] = None,
        path: str = None,
        use_sampling: bool = None,
    ):
        self._pod = {
            'activityReference': to_dprep_pod(activity_reference),
            'format': to_dprep_pod(format),
            'overrides': to_dprep_pod(overrides),
            'path': to_dprep_pod(path),
            'useSampling': to_dprep_pod(use_sampling),
        }

    @property
    def activity_reference(self) -> 'ActivityReference':
        return ActivityReference.from_pod(self._pod['activityReference']) if self._pod['activityReference'] is not None else None

    @activity_reference.setter
    def activity_reference(self, value: 'ActivityReference'):
        self._pod['activityReference'] = to_dprep_pod(value)

    @property
    def format(self) -> 'ExportScriptFormat':
        return ExportScriptFormat(self._pod['format']) if self._pod['format'] is not None else None

    @format.setter
    def format(self, value: 'ExportScriptFormat'):
        self._pod['format'] = to_dprep_pod(value)

    @property
    def overrides(self) -> List['PropertyOverride']:
        return [PropertyOverride.from_pod(i) if i is not None else None for i in self._pod['overrides']] if self._pod['overrides'] is not None else None

    @overrides.setter
    def overrides(self, value: List['PropertyOverride']):
        self._pod['overrides'] = to_dprep_pod(value)

    @property
    def path(self) -> str:
        return self._pod['path']

    @path.setter
    def path(self, value: str):
        self._pod['path'] = to_dprep_pod(value)

    @property
    def use_sampling(self) -> bool:
        return self._pod['useSampling']

    @use_sampling.setter
    def use_sampling(self, value: bool):
        self._pod['useSampling'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AnonymousActivityData:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class GetDataMessageArguments:
    def __init__(self,
        context: 'ActivityReference' = None,
        count: int = None,
        offset: int = None,
    ):
        self._pod = {
            'context': to_dprep_pod(context),
            'count': to_dprep_pod(count),
            'offset': to_dprep_pod(offset),
        }

    @property
    def context(self) -> 'ActivityReference':
        return ActivityReference.from_pod(self._pod['context']) if self._pod['context'] is not None else None

    @context.setter
    def context(self, value: 'ActivityReference'):
        self._pod['context'] = to_dprep_pod(value)

    @property
    def count(self) -> int:
        return self._pod['count']

    @count.setter
    def count(self, value: int):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def offset(self) -> int:
        return self._pod['offset']

    @offset.setter
    def offset(self, value: int):
        self._pod['offset'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class GetDataMessageResponse:
    def __init__(self,
        column_definitions: List['ColumnDefinition'] = None,
        rows_data: 'RowsData' = None,
    ):
        self._pod = {
            'columnDefinitions': to_dprep_pod(column_definitions),
            'rowsData': to_dprep_pod(rows_data),
        }

    @property
    def column_definitions(self) -> List['ColumnDefinition']:
        return [ColumnDefinition.from_pod(i) if i is not None else None for i in self._pod['columnDefinitions']] if self._pod['columnDefinitions'] is not None else None

    @column_definitions.setter
    def column_definitions(self, value: List['ColumnDefinition']):
        self._pod['columnDefinitions'] = to_dprep_pod(value)

    @property
    def rows_data(self) -> 'RowsData':
        return RowsData.from_pod(self._pod['rowsData']) if self._pod['rowsData'] is not None else None

    @rows_data.setter
    def rows_data(self, value: 'RowsData'):
        self._pod['rowsData'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class GetSecretsMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class FieldInference:
    def __init__(self,
        arguments: Dict[str, object] = None,
        type: 'FieldType' = None,
    ):
        self._pod = {
            'arguments': to_dprep_pod(arguments),
            'type': to_dprep_pod(type),
        }

    @property
    def arguments(self) -> Dict[str, object]:
        return {k: v for k, v in self._pod['arguments'].items()} if self._pod['arguments'] is not None else None

    @arguments.setter
    def arguments(self, value: Dict[str, object]):
        self._pod['arguments'] = to_dprep_pod(value)

    @property
    def type(self) -> 'FieldType':
        return FieldType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'FieldType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class GetSourceDataHashMessageArguments:
    def __init__(self,
        blocks: List['AnonymousBlockData'] = None
    ):
        self._pod = {
            'blocks': to_dprep_pod(blocks),
        }

    @property
    def blocks(self) -> List['AnonymousBlockData']:
        return [AnonymousBlockData.from_pod(i) if i is not None else None for i in self._pod['blocks']] if self._pod['blocks'] is not None else None

    @blocks.setter
    def blocks(self, value: List['AnonymousBlockData']):
        self._pod['blocks'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class SaveActivityFromDataMessageArguments:
    def __init__(self,
        activity: 'AnonymousActivityData' = None,
        path: str = None,
    ):
        self._pod = {
            'activity': to_dprep_pod(activity),
            'path': to_dprep_pod(path),
        }

    @property
    def activity(self) -> 'AnonymousActivityData':
        return AnonymousActivityData.from_pod(self._pod['activity']) if self._pod['activity'] is not None else None

    @activity.setter
    def activity(self, value: 'AnonymousActivityData'):
        self._pod['activity'] = to_dprep_pod(value)

    @property
    def path(self) -> str:
        return self._pod['path']

    @path.setter
    def path(self, value: str):
        self._pod['path'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AuthType(Enum):
    DERIVED = 0
    SERVICEPRINCIPAL = 1


class SetAmlAuthMessageArgument:
    def __init__(self,
        auth_type: 'AuthType' = None,
        auth_value: str = None,
    ):
        self._pod = {
            'authType': to_dprep_pod(auth_type),
            'authValue': to_dprep_pod(auth_value),
        }

    @property
    def auth_type(self) -> 'AuthType':
        return AuthType(self._pod['authType']) if self._pod['authType'] is not None else None

    @auth_type.setter
    def auth_type(self, value: 'AuthType'):
        self._pod['authType'] = to_dprep_pod(value)

    @property
    def auth_value(self) -> str:
        return self._pod['authValue']

    @auth_value.setter
    def auth_value(self, value: str):
        self._pod['authValue'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ExecutorType(Enum):
    CLEX = 0
    INTERACTIVESPARK = 1


class RegisterSecretMessageArguments:
    def __init__(self,
        secret_id: str = None,
        secret_value: str = None,
    ):
        self._pod = {
            'secretId': to_dprep_pod(secret_id),
            'secretValue': to_dprep_pod(secret_value),
        }

    @property
    def secret_id(self) -> str:
        return self._pod['secretId']

    @secret_id.setter
    def secret_id(self, value: str):
        self._pod['secretId'] = to_dprep_pod(value)

    @property
    def secret_value(self) -> str:
        return self._pod['secretValue']

    @secret_value.setter
    def secret_value(self, value: str):
        self._pod['secretValue'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class Secret:
    def __init__(self,
        id: str = None
    ):
        self._pod = {
            'id': to_dprep_pod(id),
        }

    @property
    def id(self) -> str:
        return self._pod['id']

    @id.setter
    def id(self, value: str):
        self._pod['id'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ArchiveType(Enum):
    ZIP = 0


class AssertPolicy(Enum):
    FAILEXECUTION = 0
    ERRORVALUE = 1


class BlockGroup(Enum):
    DEFAULT = 0
    SMART = 1
    CREATE = 2
    COLUMNTRANSFORM = 3
    REPLACETRANSFORM = 4
    FILTERCOLUMNTRANSFORM = 5
    SCHEMA = 6
    TYPECONVERSION = 7
    TABLETRANSFORM = 8
    CUSTOM = 9
    CACHE = 10
    WRITE = 11
    ASSERTION = 12
    DATASCIENCETRANSFORM = 13


class CodeBlockType(Enum):
    EXPRESSION = 0
    MODULE = 1
    FILE = 2


class ColumnRelationship(Enum):
    ALL = 0
    ANY = 1


class HistogramCompareMethod(Enum):
    WASSERSTEIN = 0
    ENERGY = 1


class PromoteHeadersMode(Enum):
    NONE = 0
    UNGROUPED = 1
    FIRSTFILE = 1
    GROUPED = 2
    ALLFILES = 2
    CONSTANTGROUPED = 3
    SAMEALLFILES = 3


class SkipMode(Enum):
    NONE = 0
    UNGROUPED = 1
    FIRSTFILE = 1
    GROUPED = 2
    ALLFILES = 2


class SType(Enum):
    EMAILADDRESS = 0
    GEOGRAPHICCOORDINATE = 1
    IPV4ADDRESS = 2
    IPV6ADDRESS = 3
    USPHONENUMBER = 4
    ZIPCODE = 5


class FilterClauseRelationship(Enum):
    ALL = 0
    ANY = 1


class FilterBoolOperators(Enum):
    EQUALS = 0
    DOESNOTEQUAL = 1


class FilterBoolValues(Enum):
    FALSE = 0
    TRUE = 1


class FilterDateOperators(Enum):
    EQUALS = 0
    DOESNOTEQUAL = 1
    ISNULL = 2
    ISNOTNULL = 3
    ISERROR = 4
    ISNOTERROR = 5
    ISBEFORE = 6
    ISBEFOREOREQUALTO = 7
    ISAFTER = 8
    ISAFTEROREQUALTO = 9


class FilterNumberOperators(Enum):
    EQUALS = 0
    DOESNOTEQUAL = 1
    ISNULL = 2
    ISNOTNULL = 3
    ISERROR = 4
    ISNOTERROR = 5
    GREATERTHAN = 6
    GREATERTHANOREQUALS = 7
    LESSTHAN = 8
    LESSTHANOREQUALS = 9


class FilterStringOperators(Enum):
    EQUALS = 0
    DOESNOTEQUAL = 1
    ISNULL = 2
    ISNOTNULL = 3
    ISERROR = 4
    ISNOTERROR = 5
    ISEMPTY = 6
    ISNOTEMPTY = 7
    BEGINSWITH = 8
    DOESNOTBEGINWITH = 9
    ENDSWITH = 10
    DOESNOTENDWITH = 11
    CONTAINS = 12
    DOESNOTCONTAIN = 13


class FilterResult(Enum):
    KEEPROWS = 0
    REMOVEROWS = 1


class HandlingInconsistentValuesAction(Enum):
    REMOVE = 0
    KEEP = 1
    REPLACE = 2


class ValueCountDifference:
    def __init__(self,
        difference_in_percent: float = None,
        value: 'DataField' = None,
    ):
        self._pod = {
            'differenceInPercent': to_dprep_pod(difference_in_percent),
            'value': to_dprep_pod(value),
        }

    @property
    def difference_in_percent(self) -> float:
        return self._pod['differenceInPercent']

    @difference_in_percent.setter
    def difference_in_percent(self, value: float):
        self._pod['differenceInPercent'] = to_dprep_pod(value)

    @property
    def value(self) -> 'DataField':
        return DataField.from_pod(self._pod['value']) if self._pod['value'] is not None else None

    @value.setter
    def value(self, value: 'DataField'):
        self._pod['value'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DataRow:
    def __init__(self,
        column_names: List[str] = None,
        values: List['DataField'] = None,
    ):
        self._pod = {
            'columnNames': to_dprep_pod(column_names),
            'values': to_dprep_pod(values),
        }

    @property
    def column_names(self) -> List[str]:
        return [i for i in self._pod['columnNames']] if self._pod['columnNames'] is not None else None

    @column_names.setter
    def column_names(self, value: List[str]):
        self._pod['columnNames'] = to_dprep_pod(value)

    @property
    def values(self) -> List['DataField']:
        return [DataField.from_pod(i) if i is not None else None for i in self._pod['values']] if self._pod['values'] is not None else None

    @values.setter
    def values(self, value: List['DataField']):
        self._pod['values'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class MomentsDifference:
    def __init__(self,
        difference_in_kurtosis: float = None,
        difference_in_mean: float = None,
        difference_in_skewness: float = None,
        difference_in_standard_deviation: float = None,
        difference_in_variance: float = None,
    ):
        self._pod = {
            'differenceInKurtosis': to_dprep_pod(difference_in_kurtosis),
            'differenceInMean': to_dprep_pod(difference_in_mean),
            'differenceInSkewness': to_dprep_pod(difference_in_skewness),
            'differenceInStandardDeviation': to_dprep_pod(difference_in_standard_deviation),
            'differenceInVariance': to_dprep_pod(difference_in_variance),
        }

    @property
    def difference_in_kurtosis(self) -> float:
        return self._pod['differenceInKurtosis']

    @difference_in_kurtosis.setter
    def difference_in_kurtosis(self, value: float):
        self._pod['differenceInKurtosis'] = to_dprep_pod(value)

    @property
    def difference_in_mean(self) -> float:
        return self._pod['differenceInMean']

    @difference_in_mean.setter
    def difference_in_mean(self, value: float):
        self._pod['differenceInMean'] = to_dprep_pod(value)

    @property
    def difference_in_skewness(self) -> float:
        return self._pod['differenceInSkewness']

    @difference_in_skewness.setter
    def difference_in_skewness(self, value: float):
        self._pod['differenceInSkewness'] = to_dprep_pod(value)

    @property
    def difference_in_standard_deviation(self) -> float:
        return self._pod['differenceInStandardDeviation']

    @difference_in_standard_deviation.setter
    def difference_in_standard_deviation(self, value: float):
        self._pod['differenceInStandardDeviation'] = to_dprep_pod(value)

    @property
    def difference_in_variance(self) -> float:
        return self._pod['differenceInVariance']

    @difference_in_variance.setter
    def difference_in_variance(self, value: float):
        self._pod['differenceInVariance'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class QuantilesDifference:
    def __init__(self,
        difference_in_p0_d1: float = None,
        difference_in_p1: float = None,
        difference_in_p25: float = None,
        difference_in_p5: float = None,
        difference_in_p50: float = None,
        difference_in_p75: float = None,
        difference_in_p95: float = None,
        difference_in_p99: float = None,
        difference_in_p99_d9: float = None,
    ):
        self._pod = {
            'differenceInP0D1': to_dprep_pod(difference_in_p0_d1),
            'differenceInP1': to_dprep_pod(difference_in_p1),
            'differenceInP25': to_dprep_pod(difference_in_p25),
            'differenceInP5': to_dprep_pod(difference_in_p5),
            'differenceInP50': to_dprep_pod(difference_in_p50),
            'differenceInP75': to_dprep_pod(difference_in_p75),
            'differenceInP95': to_dprep_pod(difference_in_p95),
            'differenceInP99': to_dprep_pod(difference_in_p99),
            'differenceInP99D9': to_dprep_pod(difference_in_p99_d9),
        }

    @property
    def difference_in_p0_d1(self) -> float:
        return self._pod['differenceInP0D1']

    @difference_in_p0_d1.setter
    def difference_in_p0_d1(self, value: float):
        self._pod['differenceInP0D1'] = to_dprep_pod(value)

    @property
    def difference_in_p1(self) -> float:
        return self._pod['differenceInP1']

    @difference_in_p1.setter
    def difference_in_p1(self, value: float):
        self._pod['differenceInP1'] = to_dprep_pod(value)

    @property
    def difference_in_p25(self) -> float:
        return self._pod['differenceInP25']

    @difference_in_p25.setter
    def difference_in_p25(self, value: float):
        self._pod['differenceInP25'] = to_dprep_pod(value)

    @property
    def difference_in_p5(self) -> float:
        return self._pod['differenceInP5']

    @difference_in_p5.setter
    def difference_in_p5(self, value: float):
        self._pod['differenceInP5'] = to_dprep_pod(value)

    @property
    def difference_in_p50(self) -> float:
        return self._pod['differenceInP50']

    @difference_in_p50.setter
    def difference_in_p50(self, value: float):
        self._pod['differenceInP50'] = to_dprep_pod(value)

    @property
    def difference_in_p75(self) -> float:
        return self._pod['differenceInP75']

    @difference_in_p75.setter
    def difference_in_p75(self, value: float):
        self._pod['differenceInP75'] = to_dprep_pod(value)

    @property
    def difference_in_p95(self) -> float:
        return self._pod['differenceInP95']

    @difference_in_p95.setter
    def difference_in_p95(self, value: float):
        self._pod['differenceInP95'] = to_dprep_pod(value)

    @property
    def difference_in_p99(self) -> float:
        return self._pod['differenceInP99']

    @difference_in_p99.setter
    def difference_in_p99(self, value: float):
        self._pod['differenceInP99'] = to_dprep_pod(value)

    @property
    def difference_in_p99_d9(self) -> float:
        return self._pod['differenceInP99D9']

    @difference_in_p99_d9.setter
    def difference_in_p99_d9(self, value: float):
        self._pod['differenceInP99D9'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ColumnProfileDifference:
    def __init__(self,
        column_type: 'FieldType' = None,
        difference_in_count_in_percent: float = None,
        difference_in_empty_value_rows_in_percent: float = None,
        difference_in_error_value_rows_in_percent: float = None,
        difference_in_histograms: float = None,
        difference_in_max: int = None,
        difference_in_median: float = None,
        difference_in_min: int = None,
        difference_in_missing_value_rows_in_percent: float = None,
        difference_in_moments: 'MomentsDifference' = None,
        difference_in_not_missing_value_rows_in_percent: float = None,
        difference_in_quantiles: 'QuantilesDifference' = None,
        difference_in_value_counts_in_percent: List['ValueCountDifference'] = None,
        name: str = None,
    ):
        self._pod = {
            'columnType': to_dprep_pod(column_type),
            'differenceInCountInPercent': to_dprep_pod(difference_in_count_in_percent),
            'differenceInEmptyValueRowsInPercent': to_dprep_pod(difference_in_empty_value_rows_in_percent),
            'differenceInErrorValueRowsInPercent': to_dprep_pod(difference_in_error_value_rows_in_percent),
            'differenceInHistograms': to_dprep_pod(difference_in_histograms),
            'differenceInMax': to_dprep_pod(difference_in_max),
            'differenceInMedian': to_dprep_pod(difference_in_median),
            'differenceInMin': to_dprep_pod(difference_in_min),
            'differenceInMissingValueRowsInPercent': to_dprep_pod(difference_in_missing_value_rows_in_percent),
            'differenceInMoments': to_dprep_pod(difference_in_moments),
            'differenceInNotMissingValueRowsInPercent': to_dprep_pod(difference_in_not_missing_value_rows_in_percent),
            'differenceInQuantiles': to_dprep_pod(difference_in_quantiles),
            'differenceInValueCountsInPercent': to_dprep_pod(difference_in_value_counts_in_percent),
            'name': to_dprep_pod(name),
        }

    @property
    def column_type(self) -> 'FieldType':
        return FieldType(self._pod['columnType']) if self._pod['columnType'] is not None else None

    @column_type.setter
    def column_type(self, value: 'FieldType'):
        self._pod['columnType'] = to_dprep_pod(value)

    @property
    def difference_in_count_in_percent(self) -> float:
        return self._pod['differenceInCountInPercent']

    @difference_in_count_in_percent.setter
    def difference_in_count_in_percent(self, value: float):
        self._pod['differenceInCountInPercent'] = to_dprep_pod(value)

    @property
    def difference_in_empty_value_rows_in_percent(self) -> float:
        return self._pod['differenceInEmptyValueRowsInPercent']

    @difference_in_empty_value_rows_in_percent.setter
    def difference_in_empty_value_rows_in_percent(self, value: float):
        self._pod['differenceInEmptyValueRowsInPercent'] = to_dprep_pod(value)

    @property
    def difference_in_error_value_rows_in_percent(self) -> float:
        return self._pod['differenceInErrorValueRowsInPercent']

    @difference_in_error_value_rows_in_percent.setter
    def difference_in_error_value_rows_in_percent(self, value: float):
        self._pod['differenceInErrorValueRowsInPercent'] = to_dprep_pod(value)

    @property
    def difference_in_histograms(self) -> float:
        return self._pod['differenceInHistograms']

    @difference_in_histograms.setter
    def difference_in_histograms(self, value: float):
        self._pod['differenceInHistograms'] = to_dprep_pod(value)

    @property
    def difference_in_max(self) -> int:
        return self._pod['differenceInMax']

    @difference_in_max.setter
    def difference_in_max(self, value: int):
        self._pod['differenceInMax'] = to_dprep_pod(value)

    @property
    def difference_in_median(self) -> float:
        return self._pod['differenceInMedian']

    @difference_in_median.setter
    def difference_in_median(self, value: float):
        self._pod['differenceInMedian'] = to_dprep_pod(value)

    @property
    def difference_in_min(self) -> int:
        return self._pod['differenceInMin']

    @difference_in_min.setter
    def difference_in_min(self, value: int):
        self._pod['differenceInMin'] = to_dprep_pod(value)

    @property
    def difference_in_missing_value_rows_in_percent(self) -> float:
        return self._pod['differenceInMissingValueRowsInPercent']

    @difference_in_missing_value_rows_in_percent.setter
    def difference_in_missing_value_rows_in_percent(self, value: float):
        self._pod['differenceInMissingValueRowsInPercent'] = to_dprep_pod(value)

    @property
    def difference_in_moments(self) -> 'MomentsDifference':
        return MomentsDifference.from_pod(self._pod['differenceInMoments']) if self._pod['differenceInMoments'] is not None else None

    @difference_in_moments.setter
    def difference_in_moments(self, value: 'MomentsDifference'):
        self._pod['differenceInMoments'] = to_dprep_pod(value)

    @property
    def difference_in_not_missing_value_rows_in_percent(self) -> float:
        return self._pod['differenceInNotMissingValueRowsInPercent']

    @difference_in_not_missing_value_rows_in_percent.setter
    def difference_in_not_missing_value_rows_in_percent(self, value: float):
        self._pod['differenceInNotMissingValueRowsInPercent'] = to_dprep_pod(value)

    @property
    def difference_in_quantiles(self) -> 'QuantilesDifference':
        return QuantilesDifference.from_pod(self._pod['differenceInQuantiles']) if self._pod['differenceInQuantiles'] is not None else None

    @difference_in_quantiles.setter
    def difference_in_quantiles(self, value: 'QuantilesDifference'):
        self._pod['differenceInQuantiles'] = to_dprep_pod(value)

    @property
    def difference_in_value_counts_in_percent(self) -> List['ValueCountDifference']:
        return [ValueCountDifference.from_pod(i) if i is not None else None for i in self._pod['differenceInValueCountsInPercent']] if self._pod['differenceInValueCountsInPercent'] is not None else None

    @difference_in_value_counts_in_percent.setter
    def difference_in_value_counts_in_percent(self, value: List['ValueCountDifference']):
        self._pod['differenceInValueCountsInPercent'] = to_dprep_pod(value)

    @property
    def name(self) -> str:
        return self._pod['name']

    @name.setter
    def name(self, value: str):
        self._pod['name'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DataProfileDifference:
    def __init__(self,
        column_profile_difference: List['ColumnProfileDifference'] = None,
        unmatched_column_profiles: Dict[str, int] = None,
    ):
        self._pod = {
            'columnProfileDifference': to_dprep_pod(column_profile_difference),
            'unmatchedColumnProfiles': to_dprep_pod(unmatched_column_profiles),
        }

    @property
    def column_profile_difference(self) -> List['ColumnProfileDifference']:
        return [ColumnProfileDifference.from_pod(i) if i is not None else None for i in self._pod['columnProfileDifference']] if self._pod['columnProfileDifference'] is not None else None

    @column_profile_difference.setter
    def column_profile_difference(self, value: List['ColumnProfileDifference']):
        self._pod['columnProfileDifference'] = to_dprep_pod(value)

    @property
    def unmatched_column_profiles(self) -> Dict[str, int]:
        return {k: v for k, v in self._pod['unmatchedColumnProfiles'].items()} if self._pod['unmatchedColumnProfiles'] is not None else None

    @unmatched_column_profiles.setter
    def unmatched_column_profiles(self, value: Dict[str, int]):
        self._pod['unmatchedColumnProfiles'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class Quantiles:
    def __init__(self,
        p0_d1: float = None,
        p1: float = None,
        p25: float = None,
        p5: float = None,
        p50: float = None,
        p75: float = None,
        p95: float = None,
        p99: float = None,
        p99_d9: float = None,
    ):
        self._pod = {
            'p0D1': to_dprep_pod(p0_d1),
            'p1': to_dprep_pod(p1),
            'p25': to_dprep_pod(p25),
            'p5': to_dprep_pod(p5),
            'p50': to_dprep_pod(p50),
            'p75': to_dprep_pod(p75),
            'p95': to_dprep_pod(p95),
            'p99': to_dprep_pod(p99),
            'p99D9': to_dprep_pod(p99_d9),
        }

    @property
    def p0_d1(self) -> float:
        return self._pod['p0D1']

    @p0_d1.setter
    def p0_d1(self, value: float):
        self._pod['p0D1'] = to_dprep_pod(value)

    @property
    def p1(self) -> float:
        return self._pod['p1']

    @p1.setter
    def p1(self, value: float):
        self._pod['p1'] = to_dprep_pod(value)

    @property
    def p25(self) -> float:
        return self._pod['p25']

    @p25.setter
    def p25(self, value: float):
        self._pod['p25'] = to_dprep_pod(value)

    @property
    def p5(self) -> float:
        return self._pod['p5']

    @p5.setter
    def p5(self, value: float):
        self._pod['p5'] = to_dprep_pod(value)

    @property
    def p50(self) -> float:
        return self._pod['p50']

    @p50.setter
    def p50(self, value: float):
        self._pod['p50'] = to_dprep_pod(value)

    @property
    def p75(self) -> float:
        return self._pod['p75']

    @p75.setter
    def p75(self, value: float):
        self._pod['p75'] = to_dprep_pod(value)

    @property
    def p95(self) -> float:
        return self._pod['p95']

    @p95.setter
    def p95(self, value: float):
        self._pod['p95'] = to_dprep_pod(value)

    @property
    def p99(self) -> float:
        return self._pod['p99']

    @p99.setter
    def p99(self, value: float):
        self._pod['p99'] = to_dprep_pod(value)

    @property
    def p99_d9(self) -> float:
        return self._pod['p99D9']

    @p99_d9.setter
    def p99_d9(self, value: float):
        self._pod['p99D9'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class TypeCount:
    def __init__(self,
        count: int = None,
        type: 'FieldType' = None,
    ):
        self._pod = {
            'count': to_dprep_pod(count),
            'type': to_dprep_pod(type),
        }

    @property
    def count(self) -> int:
        return self._pod['count']

    @count.setter
    def count(self, value: int):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def type(self) -> 'FieldType':
        return FieldType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'FieldType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ValueCount:
    def __init__(self,
        count: int = None,
        value: 'DataField' = None,
    ):
        self._pod = {
            'count': to_dprep_pod(count),
            'value': to_dprep_pod(value),
        }

    @property
    def count(self) -> int:
        return self._pod['count']

    @count.setter
    def count(self, value: int):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def value(self) -> 'DataField':
        return DataField.from_pod(self._pod['value']) if self._pod['value'] is not None else None

    @value.setter
    def value(self, value: 'DataField'):
        self._pod['value'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class HistogramBin:
    def __init__(self,
        count: float = None,
        lower_bound: float = None,
        upper_bound: float = None,
    ):
        self._pod = {
            'count': to_dprep_pod(count),
            'lowerBound': to_dprep_pod(lower_bound),
            'upperBound': to_dprep_pod(upper_bound),
        }

    @property
    def count(self) -> float:
        return self._pod['count']

    @count.setter
    def count(self, value: float):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def lower_bound(self) -> float:
        return self._pod['lowerBound']

    @lower_bound.setter
    def lower_bound(self, value: float):
        self._pod['lowerBound'] = to_dprep_pod(value)

    @property
    def upper_bound(self) -> float:
        return self._pod['upperBound']

    @upper_bound.setter
    def upper_bound(self, value: float):
        self._pod['upperBound'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class STypeCount:
    def __init__(self,
        count: int = None,
        s_type: 'SType' = None,
    ):
        self._pod = {
            'count': to_dprep_pod(count),
            'sType': to_dprep_pod(s_type),
        }

    @property
    def count(self) -> int:
        return self._pod['count']

    @count.setter
    def count(self, value: int):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def s_type(self) -> 'SType':
        return SType(self._pod['sType']) if self._pod['sType'] is not None else None

    @s_type.setter
    def s_type(self, value: 'SType'):
        self._pod['sType'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class StringLengthCount:
    def __init__(self,
        count: int = None,
        length: int = None,
    ):
        self._pod = {
            'count': to_dprep_pod(count),
            'length': to_dprep_pod(length),
        }

    @property
    def count(self) -> int:
        return self._pod['count']

    @count.setter
    def count(self, value: int):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def length(self) -> int:
        return self._pod['length']

    @length.setter
    def length(self, value: int):
        self._pod['length'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class Moments:
    def __init__(self,
        kurtosis: float = None,
        mean: float = None,
        skewness: float = None,
        standard_deviation: float = None,
        variance: float = None,
    ):
        self._pod = {
            'kurtosis': to_dprep_pod(kurtosis),
            'mean': to_dprep_pod(mean),
            'skewness': to_dprep_pod(skewness),
            'standardDeviation': to_dprep_pod(standard_deviation),
            'variance': to_dprep_pod(variance),
        }

    @property
    def kurtosis(self) -> float:
        return self._pod['kurtosis']

    @kurtosis.setter
    def kurtosis(self, value: float):
        self._pod['kurtosis'] = to_dprep_pod(value)

    @property
    def mean(self) -> float:
        return self._pod['mean']

    @mean.setter
    def mean(self, value: float):
        self._pod['mean'] = to_dprep_pod(value)

    @property
    def skewness(self) -> float:
        return self._pod['skewness']

    @skewness.setter
    def skewness(self, value: float):
        self._pod['skewness'] = to_dprep_pod(value)

    @property
    def standard_deviation(self) -> float:
        return self._pod['standardDeviation']

    @standard_deviation.setter
    def standard_deviation(self, value: float):
        self._pod['standardDeviation'] = to_dprep_pod(value)

    @property
    def variance(self) -> float:
        return self._pod['variance']

    @variance.setter
    def variance(self, value: float):
        self._pod['variance'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ProfileResult:
    def __init__(self,
        average_spaces_count: float = None,
        column_name: str = None,
        count: int = None,
        empty_count: int = None,
        error_count: int = None,
        histogram: List['HistogramBin'] = None,
        max: 'DataField' = None,
        min: 'DataField' = None,
        missing_count: int = None,
        moments: 'Moments' = None,
        not_missing_count: int = None,
        percent_missing: float = None,
        quantiles: 'Quantiles' = None,
        string_lengths: List['StringLengthCount'] = None,
        s_type_counts: List['STypeCount'] = None,
        type: 'FieldType' = None,
        type_counts: List['TypeCount'] = None,
        unique_values: int = None,
        value_counts: List['ValueCount'] = None,
    ):
        self._pod = {
            'averageSpacesCount': to_dprep_pod(average_spaces_count),
            'columnName': to_dprep_pod(column_name),
            'count': to_dprep_pod(count),
            'emptyCount': to_dprep_pod(empty_count),
            'errorCount': to_dprep_pod(error_count),
            'histogram': to_dprep_pod(histogram),
            'max': to_dprep_pod(max),
            'min': to_dprep_pod(min),
            'missingCount': to_dprep_pod(missing_count),
            'moments': to_dprep_pod(moments),
            'notMissingCount': to_dprep_pod(not_missing_count),
            'percentMissing': to_dprep_pod(percent_missing),
            'quantiles': to_dprep_pod(quantiles),
            'stringLengths': to_dprep_pod(string_lengths),
            'sTypeCounts': to_dprep_pod(s_type_counts),
            'type': to_dprep_pod(type),
            'typeCounts': to_dprep_pod(type_counts),
            'uniqueValues': to_dprep_pod(unique_values),
            'valueCounts': to_dprep_pod(value_counts),
        }

    @property
    def average_spaces_count(self) -> float:
        return self._pod['averageSpacesCount']

    @average_spaces_count.setter
    def average_spaces_count(self, value: float):
        self._pod['averageSpacesCount'] = to_dprep_pod(value)

    @property
    def column_name(self) -> str:
        return self._pod['columnName']

    @column_name.setter
    def column_name(self, value: str):
        self._pod['columnName'] = to_dprep_pod(value)

    @property
    def count(self) -> int:
        return self._pod['count']

    @count.setter
    def count(self, value: int):
        self._pod['count'] = to_dprep_pod(value)

    @property
    def empty_count(self) -> int:
        return self._pod['emptyCount']

    @empty_count.setter
    def empty_count(self, value: int):
        self._pod['emptyCount'] = to_dprep_pod(value)

    @property
    def error_count(self) -> int:
        return self._pod['errorCount']

    @error_count.setter
    def error_count(self, value: int):
        self._pod['errorCount'] = to_dprep_pod(value)

    @property
    def histogram(self) -> List['HistogramBin']:
        return [HistogramBin.from_pod(i) if i is not None else None for i in self._pod['histogram']] if self._pod['histogram'] is not None else None

    @histogram.setter
    def histogram(self, value: List['HistogramBin']):
        self._pod['histogram'] = to_dprep_pod(value)

    @property
    def max(self) -> 'DataField':
        return DataField.from_pod(self._pod['max']) if self._pod['max'] is not None else None

    @max.setter
    def max(self, value: 'DataField'):
        self._pod['max'] = to_dprep_pod(value)

    @property
    def min(self) -> 'DataField':
        return DataField.from_pod(self._pod['min']) if self._pod['min'] is not None else None

    @min.setter
    def min(self, value: 'DataField'):
        self._pod['min'] = to_dprep_pod(value)

    @property
    def missing_count(self) -> int:
        return self._pod['missingCount']

    @missing_count.setter
    def missing_count(self, value: int):
        self._pod['missingCount'] = to_dprep_pod(value)

    @property
    def moments(self) -> 'Moments':
        return Moments.from_pod(self._pod['moments']) if self._pod['moments'] is not None else None

    @moments.setter
    def moments(self, value: 'Moments'):
        self._pod['moments'] = to_dprep_pod(value)

    @property
    def not_missing_count(self) -> int:
        return self._pod['notMissingCount']

    @not_missing_count.setter
    def not_missing_count(self, value: int):
        self._pod['notMissingCount'] = to_dprep_pod(value)

    @property
    def percent_missing(self) -> float:
        return self._pod['percentMissing']

    @percent_missing.setter
    def percent_missing(self, value: float):
        self._pod['percentMissing'] = to_dprep_pod(value)

    @property
    def quantiles(self) -> 'Quantiles':
        return Quantiles.from_pod(self._pod['quantiles']) if self._pod['quantiles'] is not None else None

    @quantiles.setter
    def quantiles(self, value: 'Quantiles'):
        self._pod['quantiles'] = to_dprep_pod(value)

    @property
    def string_lengths(self) -> List['StringLengthCount']:
        return [StringLengthCount.from_pod(i) if i is not None else None for i in self._pod['stringLengths']] if self._pod['stringLengths'] is not None else None

    @string_lengths.setter
    def string_lengths(self, value: List['StringLengthCount']):
        self._pod['stringLengths'] = to_dprep_pod(value)

    @property
    def s_type_counts(self) -> List['STypeCount']:
        return [STypeCount.from_pod(i) if i is not None else None for i in self._pod['sTypeCounts']] if self._pod['sTypeCounts'] is not None else None

    @s_type_counts.setter
    def s_type_counts(self, value: List['STypeCount']):
        self._pod['sTypeCounts'] = to_dprep_pod(value)

    @property
    def type(self) -> 'FieldType':
        return FieldType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'FieldType'):
        self._pod['type'] = to_dprep_pod(value)

    @property
    def type_counts(self) -> List['TypeCount']:
        return [TypeCount.from_pod(i) if i is not None else None for i in self._pod['typeCounts']] if self._pod['typeCounts'] is not None else None

    @type_counts.setter
    def type_counts(self, value: List['TypeCount']):
        self._pod['typeCounts'] = to_dprep_pod(value)

    @property
    def unique_values(self) -> int:
        return self._pod['uniqueValues']

    @unique_values.setter
    def unique_values(self, value: int):
        self._pod['uniqueValues'] = to_dprep_pod(value)

    @property
    def value_counts(self) -> List['ValueCount']:
        return [ValueCount.from_pod(i) if i is not None else None for i in self._pod['valueCounts']] if self._pod['valueCounts'] is not None else None

    @value_counts.setter
    def value_counts(self, value: List['ValueCount']):
        self._pod['valueCounts'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ReplaceBoolValues(Enum):
    FALSE = 0
    TRUE = 1


class ReplaceValueFunction(Enum):
    CUSTOM = 0
    MIN = 1
    MAX = 2
    MEAN = 3


class StringMissingReplacementOption(Enum):
    NOTHING = 0
    NULLS = 1
    EMPTY = 2
    NULLSANDEMPTY = 3


class ColumnsSelectorType(Enum):
    STATICLIST = 0
    DYNAMIC = 1
    SINGLECOLUMN = 2


class ColumnsSelectorDetails:
    """Empty class"""

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ColumnsSelector:
    def __init__(self,
        details: 'ColumnsSelectorDetails' = None,
        type: 'ColumnsSelectorType' = None,
    ):
        self._pod = {
            'details': to_dprep_pod(details),
            'type': to_dprep_pod(type),
        }

    @property
    def details(self) -> 'ColumnsSelectorDetails':
        return ColumnsSelectorDetails.from_pod(self._pod['details']) if self._pod['details'] is not None else None

    @details.setter
    def details(self, value: 'ColumnsSelectorDetails'):
        self._pod['details'] = to_dprep_pod(value)

    @property
    def type(self) -> 'ColumnsSelectorType':
        return ColumnsSelectorType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'ColumnsSelectorType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class StaticColumnsSelectorDetails:
    def __init__(self,
        selected_columns: List[str] = None
    ):
        self._pod = {
            'selectedColumns': to_dprep_pod(selected_columns),
        }

    @property
    def selected_columns(self) -> List[str]:
        return [i for i in self._pod['selectedColumns']] if self._pod['selectedColumns'] is not None else None

    @selected_columns.setter
    def selected_columns(self, value: List[str]):
        self._pod['selectedColumns'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class SingleColumnSelectorDetails:
    def __init__(self,
        selected_column: str = None
    ):
        self._pod = {
            'selectedColumn': to_dprep_pod(selected_column),
        }

    @property
    def selected_column(self) -> str:
        return self._pod['selectedColumn']

    @selected_column.setter
    def selected_column(self, value: str):
        self._pod['selectedColumn'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DynamicColumnsSelectorDetails:
    def __init__(self,
        ignore_case: bool = None,
        invert: bool = None,
        match_whole_word: bool = None,
        term: str = None,
        use_regex: bool = None,
    ):
        self._pod = {
            'ignoreCase': to_dprep_pod(ignore_case),
            'invert': to_dprep_pod(invert),
            'matchWholeWord': to_dprep_pod(match_whole_word),
            'term': to_dprep_pod(term),
            'useRegex': to_dprep_pod(use_regex),
        }

    @property
    def ignore_case(self) -> bool:
        return self._pod['ignoreCase']

    @ignore_case.setter
    def ignore_case(self, value: bool):
        self._pod['ignoreCase'] = to_dprep_pod(value)

    @property
    def invert(self) -> bool:
        return self._pod['invert']

    @invert.setter
    def invert(self, value: bool):
        self._pod['invert'] = to_dprep_pod(value)

    @property
    def match_whole_word(self) -> bool:
        return self._pod['matchWholeWord']

    @match_whole_word.setter
    def match_whole_word(self, value: bool):
        self._pod['matchWholeWord'] = to_dprep_pod(value)

    @property
    def term(self) -> str:
        return self._pod['term']

    @term.setter
    def term(self, value: str):
        self._pod['term'] = to_dprep_pod(value)

    @property
    def use_regex(self) -> bool:
        return self._pod['useRegex']

    @use_regex.setter
    def use_regex(self, value: bool):
        self._pod['useRegex'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class SelectorDomainType(Enum):
    SINGLECOLUMN = 0
    MULTICOLUMN = 1
    STATICMULTICOLUMN = 2


class ColumnsSelectorDomainDetails:
    def __init__(self,
        field_types: List['FieldType'] = None,
        selector_domain_type: 'SelectorDomainType' = None,
    ):
        self._pod = {
            'fieldTypes': to_dprep_pod(field_types),
            'selectorDomainType': to_dprep_pod(selector_domain_type),
        }

    @property
    def field_types(self) -> List['FieldType']:
        return [FieldType(i) if i is not None else None for i in self._pod['fieldTypes']] if self._pod['fieldTypes'] is not None else None

    @field_types.setter
    def field_types(self, value: List['FieldType']):
        self._pod['fieldTypes'] = to_dprep_pod(value)

    @property
    def selector_domain_type(self) -> 'SelectorDomainType':
        return SelectorDomainType(self._pod['selectorDomainType']) if self._pod['selectorDomainType'] is not None else None

    @selector_domain_type.setter
    def selector_domain_type(self, value: 'SelectorDomainType'):
        self._pod['selectorDomainType'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ColumnsSelectorDomain:
    def __init__(self,
        details: object = None,
        type: 'DomainType' = None,
    ):
        self._pod = {
            'details': to_dprep_pod(details),
            'type': to_dprep_pod(type),
        }

    @property
    def details(self) -> object:
        return self._pod['details']

    @details.setter
    def details(self, value: object):
        self._pod['details'] = to_dprep_pod(value)

    @property
    def type(self) -> 'DomainType':
        return DomainType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'DomainType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ResourceDetails:
    """Empty class"""

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DataSourceTarget(Enum):
    LOCAL = 0
    AZUREBLOBSTORAGE = 1
    AZUREDATALAKESTORAGE = 2


class DataSourcePropertyValue:
    def __init__(self,
        resource_details: List['ResourceDetails'] = None,
        target: 'DataSourceTarget' = None,
    ):
        self._pod = {
            'resourceDetails': to_dprep_pod(resource_details),
            'target': to_dprep_pod(target),
        }

    @property
    def resource_details(self) -> List['ResourceDetails']:
        return [ResourceDetails.from_pod(i) if i is not None else None for i in self._pod['resourceDetails']] if self._pod['resourceDetails'] is not None else None

    @resource_details.setter
    def resource_details(self, value: List['ResourceDetails']):
        self._pod['resourceDetails'] = to_dprep_pod(value)

    @property
    def target(self) -> 'DataSourceTarget':
        return DataSourceTarget(self._pod['target']) if self._pod['target'] is not None else None

    @target.setter
    def target(self, value: 'DataSourceTarget'):
        self._pod['target'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class SampleType(Enum):
    NONE = 0
    TOP1000 = 1
    TOP10000 = 2
    RANDOM1000 = 3
    RANDOM10000 = 4


class StorageSources(Enum):
    LOCAL = 0
    BLOB = 1
    ADLS = 2


class SourceType(Enum):
    FILE = 0
    DIRECTORY = 1
    MIX = 2


class FileSourcesDomainDetails:
    def __init__(self,
        allowed_sources: List['StorageSources'] = None,
        allowed_source_type: 'SourceType' = None,
        allow_multiple: bool = None,
    ):
        self._pod = {
            'allowedSources': to_dprep_pod(allowed_sources),
            'allowedSourceType': to_dprep_pod(allowed_source_type),
            'allowMultiple': to_dprep_pod(allow_multiple),
        }

    @property
    def allowed_sources(self) -> List['StorageSources']:
        return [StorageSources(i) if i is not None else None for i in self._pod['allowedSources']] if self._pod['allowedSources'] is not None else None

    @allowed_sources.setter
    def allowed_sources(self, value: List['StorageSources']):
        self._pod['allowedSources'] = to_dprep_pod(value)

    @property
    def allowed_source_type(self) -> 'SourceType':
        return SourceType(self._pod['allowedSourceType']) if self._pod['allowedSourceType'] is not None else None

    @allowed_source_type.setter
    def allowed_source_type(self, value: 'SourceType'):
        self._pod['allowedSourceType'] = to_dprep_pod(value)

    @property
    def allow_multiple(self) -> bool:
        return self._pod['allowMultiple']

    @allow_multiple.setter
    def allow_multiple(self, value: bool):
        self._pod['allowMultiple'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class FileSourcesDomain:
    def __init__(self,
        details: 'FileSourcesDomainDetails' = None,
        type: 'DomainType' = None,
    ):
        self._pod = {
            'details': to_dprep_pod(details),
            'type': to_dprep_pod(type),
        }

    @property
    def details(self) -> 'FileSourcesDomainDetails':
        return FileSourcesDomainDetails.from_pod(self._pod['details']) if self._pod['details'] is not None else None

    @details.setter
    def details(self, value: 'FileSourcesDomainDetails'):
        self._pod['details'] = to_dprep_pod(value)

    @property
    def type(self) -> 'DomainType':
        return DomainType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'DomainType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class OutputFileDestination(Enum):
    LOCAL = 0
    AZUREBLOB = 1
    AZUREDATALAKE = 2


class OutputFilePropertyValue:
    def __init__(self,
        resource_details: List['ResourceDetails'] = None,
        target: 'OutputFileDestination' = None,
    ):
        self._pod = {
            'resourceDetails': to_dprep_pod(resource_details),
            'target': to_dprep_pod(target),
        }

    @property
    def resource_details(self) -> List['ResourceDetails']:
        return [ResourceDetails.from_pod(i) if i is not None else None for i in self._pod['resourceDetails']] if self._pod['resourceDetails'] is not None else None

    @resource_details.setter
    def resource_details(self, value: List['ResourceDetails']):
        self._pod['resourceDetails'] = to_dprep_pod(value)

    @property
    def target(self) -> 'OutputFileDestination':
        return OutputFileDestination(self._pod['target']) if self._pod['target'] is not None else None

    @target.setter
    def target(self, value: 'OutputFileDestination'):
        self._pod['target'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class OutputFileTypeDomainDetails:
    def __init__(self,
        allowed_extensions: List[str] = None,
        allow_others: bool = None,
    ):
        self._pod = {
            'allowedExtensions': to_dprep_pod(allowed_extensions),
            'allowOthers': to_dprep_pod(allow_others),
        }

    @property
    def allowed_extensions(self) -> List[str]:
        return [i for i in self._pod['allowedExtensions']] if self._pod['allowedExtensions'] is not None else None

    @allowed_extensions.setter
    def allowed_extensions(self, value: List[str]):
        self._pod['allowedExtensions'] = to_dprep_pod(value)

    @property
    def allow_others(self) -> bool:
        return self._pod['allowOthers']

    @allow_others.setter
    def allow_others(self, value: bool):
        self._pod['allowOthers'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class OutputFileTypeDomain:
    def __init__(self,
        details: 'OutputFileTypeDomainDetails' = None,
        type: 'DomainType' = None,
    ):
        self._pod = {
            'details': to_dprep_pod(details),
            'type': to_dprep_pod(type),
        }

    @property
    def details(self) -> 'OutputFileTypeDomainDetails':
        return OutputFileTypeDomainDetails.from_pod(self._pod['details']) if self._pod['details'] is not None else None

    @details.setter
    def details(self, value: 'OutputFileTypeDomainDetails'):
        self._pod['details'] = to_dprep_pod(value)

    @property
    def type(self) -> 'DomainType':
        return DomainType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'DomainType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class LocalResourceDetails:
    def __init__(self,
        path: str = None
    ):
        self._pod = {
            'path': to_dprep_pod(path),
        }

    @property
    def path(self) -> str:
        return self._pod['path']

    @path.setter
    def path(self, value: str):
        self._pod['path'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AzureBlobResourceDetails:
    def __init__(self,
        path: str = None,
        sas: 'Secret' = None,
        storage_account_key: 'Secret' = None,
        storage_account_name: str = None,
    ):
        self._pod = {
            'path': to_dprep_pod(path),
            'sas': to_dprep_pod(sas),
            'storageAccountKey': to_dprep_pod(storage_account_key),
            'storageAccountName': to_dprep_pod(storage_account_name),
        }

    @property
    def path(self) -> str:
        return self._pod['path']

    @path.setter
    def path(self, value: str):
        self._pod['path'] = to_dprep_pod(value)

    @property
    def sas(self) -> 'Secret':
        return Secret.from_pod(self._pod['sas']) if self._pod['sas'] is not None else None

    @sas.setter
    def sas(self, value: 'Secret'):
        self._pod['sas'] = to_dprep_pod(value)

    @property
    def storage_account_key(self) -> 'Secret':
        return Secret.from_pod(self._pod['storageAccountKey']) if self._pod['storageAccountKey'] is not None else None

    @storage_account_key.setter
    def storage_account_key(self, value: 'Secret'):
        self._pod['storageAccountKey'] = to_dprep_pod(value)

    @property
    def storage_account_name(self) -> str:
        return self._pod['storageAccountName']

    @storage_account_name.setter
    def storage_account_name(self, value: str):
        self._pod['storageAccountName'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ValueOption:
    def __init__(self,
        id: object = None,
        value: object = None,
    ):
        self._pod = {
            'id': to_dprep_pod(id),
            'value': to_dprep_pod(value),
        }

    @property
    def id(self) -> object:
        return self._pod['id']

    @id.setter
    def id(self, value: object):
        self._pod['id'] = to_dprep_pod(value)

    @property
    def value(self) -> object:
        return self._pod['value']

    @value.setter
    def value(self, value: object):
        self._pod['value'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class AzureDataLakeResourceDetails:
    def __init__(self,
        o_auth_token: 'Secret' = None,
        path: str = None,
    ):
        self._pod = {
            'oAuthToken': to_dprep_pod(o_auth_token),
            'path': to_dprep_pod(path),
        }

    @property
    def o_auth_token(self) -> 'Secret':
        return Secret.from_pod(self._pod['oAuthToken']) if self._pod['oAuthToken'] is not None else None

    @o_auth_token.setter
    def o_auth_token(self, value: 'Secret'):
        self._pod['oAuthToken'] = to_dprep_pod(value)

    @property
    def path(self) -> str:
        return self._pod['path']

    @path.setter
    def path(self, value: str):
        self._pod['path'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ValuesFromSetDomainDetails:
    def __init__(self,
        allow_custom: bool = None,
        custom_enum_value: object = None,
        values: List['ValueOption'] = None,
    ):
        self._pod = {
            'allowCustom': to_dprep_pod(allow_custom),
            'customEnumValue': to_dprep_pod(custom_enum_value),
            'values': to_dprep_pod(values),
        }

    @property
    def allow_custom(self) -> bool:
        return self._pod['allowCustom']

    @allow_custom.setter
    def allow_custom(self, value: bool):
        self._pod['allowCustom'] = to_dprep_pod(value)

    @property
    def custom_enum_value(self) -> object:
        return self._pod['customEnumValue']

    @custom_enum_value.setter
    def custom_enum_value(self, value: object):
        self._pod['customEnumValue'] = to_dprep_pod(value)

    @property
    def values(self) -> List['ValueOption']:
        return [ValueOption.from_pod(i) if i is not None else None for i in self._pod['values']] if self._pod['values'] is not None else None

    @values.setter
    def values(self, value: List['ValueOption']):
        self._pod['values'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ValuesFromSetDomain:
    def __init__(self,
        details: 'ValuesFromSetDomainDetails' = None,
        type: 'DomainType' = None,
    ):
        self._pod = {
            'details': to_dprep_pod(details),
            'type': to_dprep_pod(type),
        }

    @property
    def details(self) -> 'ValuesFromSetDomainDetails':
        return ValuesFromSetDomainDetails.from_pod(self._pod['details']) if self._pod['details'] is not None else None

    @details.setter
    def details(self, value: 'ValuesFromSetDomainDetails'):
        self._pod['details'] = to_dprep_pod(value)

    @property
    def type(self) -> 'DomainType':
        return DomainType(self._pod['type']) if self._pod['type'] is not None else None

    @type.setter
    def type(self, value: 'DomainType'):
        self._pod['type'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class LexErrorCode:
    """Empty class"""

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ValueKind(Enum):
    NULL = 0
    BOOLEAN = 1
    LONG = 2
    DOUBLE = 3
    STRING = 4
    DATETIME = 5
    BINARY = 6
    LIST = 7
    RECORD = 8
    FUNCTION = 9
    ERROR = 10
    STREAMINFO = 11


class SplitFillStrategyConstraint(Enum):
    NONE = 0
    LEFTTORIGHT = 1
    RIGHTTOLEFT = 2


class SummaryFunction(Enum):
    MIN = 0
    MAX = 1
    MEAN = 2
    MEDIAN = 3
    VAR = 4
    SD = 5
    COUNT = 8
    SUM = 11
    COUNTWITHNULLS = 12
    QUARTILES = 13
    HISTOGRAM = 14
    KERNELDENSITY = 15
    QUANTILES = 16
    STATISTICALMOMENTS = 17
    SKEWNESS = 18
    KURTOSIS = 19
    VALUECOUNTSLIMITED = 20
    VALUEKINDS = 21
    MISSINGANDEMPTY = 22
    TIMEDIGEST = 23
    STYPECOUNTS = 24
    TOLIST = 25
    TYPEINFERENCE = 26
    AVERAGESPACESCOUNT = 27
    STRINGLENGTHS = 28


class SingleSideJoinSuggestion:
    def __init__(self,
        activity_reference_to_use: 'ActivityReference' = None,
        column_names: List[str] = None,
        joined_rows_percentage: float = None,
        needs_transform: bool = None,
        python_transformation_script: List[str] = None,
    ):
        self._pod = {
            'activityReferenceToUse': to_dprep_pod(activity_reference_to_use),
            'columnNames': to_dprep_pod(column_names),
            'joinedRowsPercentage': to_dprep_pod(joined_rows_percentage),
            'needsTransform': to_dprep_pod(needs_transform),
            'pythonTransformationScript': to_dprep_pod(python_transformation_script),
        }

    @property
    def activity_reference_to_use(self) -> 'ActivityReference':
        return ActivityReference.from_pod(self._pod['activityReferenceToUse']) if self._pod['activityReferenceToUse'] is not None else None

    @activity_reference_to_use.setter
    def activity_reference_to_use(self, value: 'ActivityReference'):
        self._pod['activityReferenceToUse'] = to_dprep_pod(value)

    @property
    def column_names(self) -> List[str]:
        return [i for i in self._pod['columnNames']] if self._pod['columnNames'] is not None else None

    @column_names.setter
    def column_names(self, value: List[str]):
        self._pod['columnNames'] = to_dprep_pod(value)

    @property
    def joined_rows_percentage(self) -> float:
        return self._pod['joinedRowsPercentage']

    @joined_rows_percentage.setter
    def joined_rows_percentage(self, value: float):
        self._pod['joinedRowsPercentage'] = to_dprep_pod(value)

    @property
    def needs_transform(self) -> bool:
        return self._pod['needsTransform']

    @needs_transform.setter
    def needs_transform(self, value: bool):
        self._pod['needsTransform'] = to_dprep_pod(value)

    @property
    def python_transformation_script(self) -> List[str]:
        return [i for i in self._pod['pythonTransformationScript']] if self._pod['pythonTransformationScript'] is not None else None

    @python_transformation_script.setter
    def python_transformation_script(self, value: List[str]):
        self._pod['pythonTransformationScript'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class JoinSuggestionResult:
    def __init__(self,
        join_keys: Dict[str, str] = None,
        left_suggestion: 'SingleSideJoinSuggestion' = None,
        right_suggestion: 'SingleSideJoinSuggestion' = None,
    ):
        self._pod = {
            'joinKeys': to_dprep_pod(join_keys),
            'leftSuggestion': to_dprep_pod(left_suggestion),
            'rightSuggestion': to_dprep_pod(right_suggestion),
        }

    @property
    def join_keys(self) -> Dict[str, str]:
        return {k: v for k, v in self._pod['joinKeys'].items()} if self._pod['joinKeys'] is not None else None

    @join_keys.setter
    def join_keys(self, value: Dict[str, str]):
        self._pod['joinKeys'] = to_dprep_pod(value)

    @property
    def left_suggestion(self) -> 'SingleSideJoinSuggestion':
        return SingleSideJoinSuggestion.from_pod(self._pod['leftSuggestion']) if self._pod['leftSuggestion'] is not None else None

    @left_suggestion.setter
    def left_suggestion(self, value: 'SingleSideJoinSuggestion'):
        self._pod['leftSuggestion'] = to_dprep_pod(value)

    @property
    def right_suggestion(self) -> 'SingleSideJoinSuggestion':
        return SingleSideJoinSuggestion.from_pod(self._pod['rightSuggestion']) if self._pod['rightSuggestion'] is not None else None

    @right_suggestion.setter
    def right_suggestion(self, value: 'SingleSideJoinSuggestion'):
        self._pod['rightSuggestion'] = to_dprep_pod(value)

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class ProseOutputTypeConstraint(Enum):
    NUMBER = 0
    DATE = 1
    STRING = 2


class DatabaseType(Enum):
    MSSQL = 0
    POSTGRESQL = 1


class MismatchAsOption(Enum):
    ASTRUE = 0
    ASFALSE = 1
    ASERROR = 2


class DecimalMark(Enum):
    DOT = 0
    COMMA = 1


class TrimType(Enum):
    WHITESPACE = 0
    CUSTOM = 1


class JoinType(Enum):
    NONE = 0
    MATCH = 2
    INNER = 2
    UNMATCHLEFT = 4
    LEFTANTI = 4
    LEFTOUTER = 6
    UNMATCHRIGHT = 8
    RIGHTANTI = 8
    RIGHTOUTER = 10
    FULLANTI = 12
    FULL = 14


class DataPrepErrorCode:
    """Empty class"""

    @classmethod
    def from_pod(cls, pod):
        obj = cls()
        obj._pod = pod
        return obj

    def to_pod(self):
        return self._pod

    def __repr__(self):
        return self.__class__.__name__ + '(' + json.dumps(self._pod, indent=2) + ')'


class DatabaseAuthType(Enum):
    SERVER = 0
    WINDOWS = 1
    AAD = 2

