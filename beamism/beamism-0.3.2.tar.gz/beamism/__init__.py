# -*- coding: utf-8 -*-

import json
import uuid
from functools import partial
from datetime import datetime
import apache_beam as beam
from beamism.utils import *


BASE_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ['results', 'is_func_success', 'func_msg'],
    "properties": {
        "is_func_success": { "type": "boolean"},
        "func_msg": { "type": "string"},
        "results": { "type": ["array", "object", "null"] }
    }
}

class Outcome():
    def __init__(self,
                 pipeline='',
                 params={},
                 element_id='',
                 sender_element_id='',
                 data=None,
                 succeeded=False,
                 message='',
                 start_utc_time=None,
                 end_utc_time=None,
                 processing_time=None,
                 func_version=None):
        self.pipeline_name = pipeline
        self.params = params
        self.element_id = element_id
        self.sender_element_id = sender_element_id
        self.data = data
        self.succeeded = succeeded
        self.message = message
        self.start_utc_time = start_utc_time
        self.end_utc_time = end_utc_time
        self.processing_time = processing_time
        self.func_version = func_version

    def to_json(self):
        return {
            "pipeline": self.pipeline_name,
            "params": self.params,
            "element_id": self.element_id,
            "sender_element_id": self.sender_element_id,
            "data": self.data,
            "succeeded": self.succeeded,
            "message": self.message,
            "start_utc_time": self.start_utc_time,
            "end_utc_time": self.end_utc_time,
            "processing_time": self.processing_time,
            "func_version": self.func_version
        }

class Lambda(beam.DoFn):
    '''
    Parameters:
        func:
            function(dict => (dict, bool, str))
        save_func:
            function(dict => bool)
        pipeline_name: str
        func_version: str
    '''
    def __init__(self,
                 func,
                 input_schema,
                 save_func=None,
                 pipeline_name='',
                 func_version=None,
                 notificator=SilentNotificator()):
        self.func = func
        self.input_schema = input_schema
        self.pipeline_name = pipeline_name
        self.save_func = save_func
        self.func_version = func_version
        self.notificator = notificator

    def process(self, msg_text, save_mode=True):
        element_id = str(uuid.uuid4()) # Pipelineが処理する一つ一つのJob固有のID( ≠ message_id)
        start_utc_time = datetime.utcnow()
        input_json = parse_json_message(msg_text)
        if input_json is None: # インプットがJSON形式ではないケース
            output_json = self.create_output_json_when_input_is_not_json(start_utc_time, msg_text, element_id)
            self.notificator.parse_error(msg_text)
            self.save(output_json, save_mode)
            return data_packing(output_json)

        self.notificator.start(msg_text, input_json)

        if self.input_schema is not None: # インプットが与えられたスキーマに従っていないケース
            input_validation_err = validate_json_based_on_schema(input_json, self.input_schema)
            if input_validation_err is not None:
                error_msg = "{0}@{1}".format(input_validation_err.message, ''.join(str(input_validation_err.absolute_path)))
                output_json = self.create_output_json_when_validation_fail(start_utc_time, msg_text, element_id, error_msg, input_json)
                self.notificator.validation_error(msg_text, input_json)
                self.save(output_json, save_mode)
                return data_packing(output_json)

        if not "succeeded" in input_json or not input_json["succeeded"]: # 一つ前のJOBが成功していないケース
            output_json = self.create_output_json_when_previous_job_failed(start_utc_time, msg_text, element_id, input_json)
            self.notificator.previous_job_failed(msg_text, input_json)
            self.save(output_json, save_mode)
            return data_packing(output_json)

        if not "data" in input_json or input_json["data"] is None: # データが存在しないケース
            output_json = self.create_output_json_when_data_not_found(start_utc_time, msg_text, element_id, input_json)
            self.notificator.data_not_found(msg_text, input_json)
            self.save(output_json, save_mode)
            return data_packing(output_json)

        indata = input_json["data"]
        main_output = self.func(indata)

        if validate_json_based_on_schema(main_output, BASE_OUTPUT_SCHEMA):
            func_msg = 'Output of main_func should follow the BASE_OUTPUT_SCHEMA. The output is follows: ' + str(main_output)
            results = [{}]
            is_func_success = False
        else:
            results, is_func_success, func_msg = (main_output['results'], main_output['is_func_success'], main_output['func_msg'])

        if type(results) != list:
            results = [{}] if results is None else [results]

        output_json_for_save_func = self.create_output_json_when_msg_is_valid(start_utc_time,
                                                                              msg_text,
                                                                              element_id,
                                                                              input_json,
                                                                              is_func_success,
                                                                              func_msg,
                                                                              results)
        self.save(output_json_for_save_func, save_mode)
        outdatas = [merge_jsons(indata, result) for result in results]
        output_jsons = [self.create_output_json_when_msg_is_valid(start_utc_time,
                                                                  msg_text,
                                                                  element_id,
                                                                  input_json,
                                                                  is_func_success,
                                                                  func_msg,
                                                                  outdata) for outdata in outdatas]
        self.notificator.finish(msg_text, input_json)
        return data_packing(output_jsons)

    def save(self, output_json, save_mode=True):
        if self.save_func is not None and save_mode:
            is_acknowledged = self.save_func(output_json)
            return is_acknowledged
        return False

    def create_output_json_when_input_is_not_json(self, start_utc_time, msg_text, element_id):
        return Outcome(pipeline=self.pipeline_name,
                       params={ "input_text": msg_text, "error": "parse error" },
                       element_id=element_id,
                       data=None,
                       succeeded=False,
                       message="Cannot parse this message as json",
                       start_utc_time=str(start_utc_time),
                       end_utc_time=str(datetime.utcnow()),
                       processing_time=(datetime.utcnow() - start_utc_time).total_seconds(),
                       func_version=self.func_version).to_json()

    def create_output_json_when_validation_fail(self, start_utc_time, msg_text, element_id, error_msg, input_json):
        return Outcome(pipeline=self.pipeline_name,
                       params=input_json["data"],
                       element_id=element_id,
                       data=None,
                       succeeded=False,
                       message=error_msg,
                       start_utc_time=str(start_utc_time),
                       end_utc_time=str(datetime.utcnow()),
                       processing_time=(datetime.utcnow() - start_utc_time).total_seconds(),
                       func_version=self.func_version).to_json()

    def create_output_json_when_previous_job_failed(self, start_utc_time, msg_text, element_id, input_json):
        return Outcome(pipeline=self.pipeline_name,
                       params=input_json["data"],
                       element_id=element_id,
                       sender_element_id=input_json["element_id"] if "element_id" in input_json else None,
                       data=None,
                       succeeded=False,
                       message="Previous job failed",
                       start_utc_time=str(start_utc_time),
                       end_utc_time=str(datetime.utcnow()),
                       processing_time=(datetime.utcnow() - start_utc_time).total_seconds(),
                       func_version=self.func_version).to_json()

    def create_output_json_when_data_not_found(self, start_utc_time, msg_text, element_id, input_json):
        return Outcome(pipeline=self.pipeline_name,
                       params=input_json["data"],
                       element_id=element_id,
                       sender_element_id=input_json["element_id"] if "element_id" in input_json else None,
                       data=None,
                       succeeded=False,
                       message="Data not found",
                       start_utc_time=str(start_utc_time),
                       end_utc_time=str(datetime.utcnow()),
                       processing_time=(datetime.utcnow() - start_utc_time).total_seconds(),
                       func_version=self.func_version).to_json()

    def create_output_json_when_msg_is_valid(self,
                                             start_utc_time,
                                             msg_text,
                                             element_id,
                                             input_json,
                                             is_func_success,
                                             func_msg,
                                             data):
        return Outcome(pipeline=self.pipeline_name,
                       params=input_json["data"],
                       element_id=element_id,
                       sender_element_id=input_json["element_id"] if "element_id" in input_json else None,
                       data=data,
                       succeeded=is_func_success,
                       message=func_msg,
                       start_utc_time=str(start_utc_time),
                       end_utc_time=str(datetime.utcnow()),
                       processing_time=(datetime.utcnow() - start_utc_time).total_seconds(),
                       func_version=self.func_version).to_json()
