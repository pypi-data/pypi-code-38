# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""helper to create contracts of events"""
from .utils import get_timestamp
from ..models.base_event import BaseEvent
from ..models import ErrorResponse, RootError, DebugInfoResponse

RUNID = "RunId"
HEARTBEAT_NAME = "Microsoft.MachineLearning.Run.Heartbeat"
STARTNAME = "Microsoft.MachineLearning.Run.Start"
FAILEDNAME = "Microsoft.MachineLearning.Run.Failed"
COMPLETEDNAME = "Microsoft.MachineLearning.Run.Completed"
CANCELEDNAME = "Microsoft.MachineLearning.Run.Canceled"
WARNINGNAME = "Microsoft.MachineLearning.Run.Warning"
ERRORNAME = "Microsoft.MachineLearning.Run.Error"
HEARTBEAT_DATA_PROP = "TimeToLiveSeconds"
START_DATA_PROP = "StartTime"
END_DATA_PROP = "EndTime"
WARNING_SOURCE = "Source"
WARNING_MESSAGE = "Message"
ERROR_RESPONSE = "ErrorResponse"


def create_heartbeat_event(run_id, timeout_sec):
    """create heartbeat event"""
    time = get_timestamp()
    event_data = {RUNID: run_id,
                  HEARTBEAT_DATA_PROP: timeout_sec}

    return BaseEvent(timestamp=time,
                     name=HEARTBEAT_NAME,
                     data=event_data)


def create_warning_event(run_id, source, message):
    """create warning event"""
    time = get_timestamp()
    event_data = {RUNID: run_id,
                  WARNING_SOURCE: source,
                  WARNING_MESSAGE: message}

    return BaseEvent(timestamp=time,
                     name=WARNINGNAME,
                     data=event_data)


def create_error_event(run_id, error_dict):
    """create error event"""
    time = get_timestamp()
    debug_info = DebugInfoResponse(error_dict.get("debug_type"),
                                   error_dict.get("debug_message"),
                                   error_dict.get("debug_stack_trace"))
    root_error = RootError(code=error_dict.get("code"), message=error_dict.get("message"), debug_info=debug_info)
    error_response = ErrorResponse(root_error)
    event_data = {RUNID: run_id,
                  ERROR_RESPONSE: error_response}

    return BaseEvent(timestamp=time,
                     name=ERRORNAME,
                     data=event_data)


def create_run_event(run_id, name, data_prop):
    """create run event"""
    time = get_timestamp()
    event_data = {RUNID: run_id, data_prop: time}

    return BaseEvent(timestamp=time,
                     name=name,
                     data=event_data)


def create_start_event(run_id):
    """create start run event"""
    return create_run_event(run_id, STARTNAME, START_DATA_PROP)


def create_failed_event(run_id):
    """create failed run event"""
    return create_run_event(run_id, FAILEDNAME, END_DATA_PROP)


def create_completed_event(run_id):
    """create completed run event"""
    return create_run_event(run_id, COMPLETEDNAME, END_DATA_PROP)


def create_canceled_event(run_id):
    """create canceled run event"""
    return create_run_event(run_id, CANCELEDNAME, END_DATA_PROP)
