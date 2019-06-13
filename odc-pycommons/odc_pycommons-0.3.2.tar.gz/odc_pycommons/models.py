# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from warnings import warn
import json
import hashlib
from datetime import datetime
import traceback
from decimal import Decimal


class CommsRequest:

    def __init__(self, uri: str, trace_id: str=None):
        self.trace_id = None
        self._validate(uri=uri, trace_id=trace_id)        

    def _validate(self, uri: str, trace_id: str=None):
        if uri is None:
            raise Exception('the URI cannot be None. It is used for connecting to a remote host or some destination.')
        if not isinstance(uri, str):
            raise Exception('The URI must be a string')
        if len(uri) < 1:
            raise Exception('The URI must be a string containing a valid destination')
        self.uri = uri
        if trace_id is not None:
            if isinstance(trace_id, str):
                self.trace_id = trace_id
            else:
                warn('The Trace ID, when supplied, must be a string')

    def to_dict(self)->dict:
        raise Exception('Not implemented')


class CommsRestFulRequest(CommsRequest):

    def __init__(self, uri: str, data: dict=None, trace_id: str=None):
        self._validate_data(data=data)
        super().__init__(uri=uri, trace_id=trace_id)

    def _validate_data(self, data: dict):
        if data is None:
            raise Exception('Data must be supplied')
        if not type(data) in (dict, list, tuple):
            raise Exception('Unsupported data type: expected a dict or a list or a tuple')
        self.data = data

    def to_dict(self):
        data_value = dict()
        if self.data is not None:
            if type(self.data) in (dict, list):
                data_value = self.data
            elif isinstance(self.data, tuple):
                data_value = list(self.data)
            else:
                warn('Unsupported data type. The dictionary will be empty')
        return data_value

    def to_json(self):
        return json.dumps(self.to_dict())


class CommsResponse:

    def __init__(
        self,
        is_error: bool=True,
        response_code: int=-1,
        response_code_description: str='Response code undefined',
        response_data: str=None,
        trace_id: str=None
    ):
        self._validate(
            is_error=is_error,
            response_code=response_code,
            response_code_description=response_code_description,
            response_data=response_data,
            trace_id=trace_id
        )
        self.warnings = list()

    def _validate(
        self,
        is_error: bool,
        response_code: int,
        response_code_description: str,
        response_data: str,
        trace_id: str
    ):
        if is_error is None:
            raise Exception('Error flag must be a bool type [1]')
        if not isinstance(is_error, bool):
            raise Exception('Error flag must be a bool type [2]')
        self.is_error = is_error
        if response_code is None:
            raise Exception('A response code must be provided as an integer [1]')
        if not isinstance(response_code, int):
            raise Exception('A response code must be provided as an integer [2]')
        self.response_code = response_code
        if response_code_description is not None:
            if not isinstance(response_code_description, str):
                raise Exception('When supplying a response code description, the description must be a string')
        self.response_code_description = response_code_description
        if response_data is not None:
            if not isinstance(response_data, str):
                raise Exception('When supplying response data, the value must be a string')
        self.response_data = response_data
        if trace_id is not None:
            if not isinstance(trace_id, str):
                raise Exception('When supplying a trace ID, the value must be a string')
        self.trace_id = trace_id

    def to_dict(self):
        response_data_value = None
        if self.response_data is not None:
            response_data_type = type(self.response_data)
            if response_data_type in (str, int, dict, list):
                response_data_value = self.response_data
            elif isinstance(self.response_data, tuple):
                response_data_value = list(self.response_data)
            else:
                response_data_value = str(self.response_data)
        return {
            'IsError': self.is_error,
            'ResponseCode': self.response_code,
            'ResponseDescription': self.response_code_description,
            'Data': response_data_value,
            'TraceId': self.trace_id,
            'Warnings': self.warnings
        }


AXIS_DATA_TYPES = {
    'STRING': str,
    'NUMBER': Decimal,
    'BOOLEAN': bool
}


# EOF
