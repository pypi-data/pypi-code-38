import json
from datetime import datetime
import uuid
from os.path import exists
from time import sleep

from common.util.common_utils import request_server


class UserLogStream:
    def __init__(self, task_context, job_uuid, task_uuid, master_server_endpoint, auth_token):
        """
        class for streaming upload user log
        :param task_context: context for user process
        :param job_uuid: current task's job uuid
        :param task_uuid: current task uuid
        :param master_server_endpoint: master server to upload the log
        """
        self.task_context = task_context
        self.job_uuid = job_uuid
        self.task_uuid = task_uuid
        self.master_endpoint = master_server_endpoint
        self.auth_token = auth_token

    def stream_log(self, log_type, file_path) -> None:
        """
        read the log file and construct a list of dict each represents record in user_log
        keep reading until task_context signal process is dead
        :param file_path: log_file or error_file from user code
        :param log_type: log or error
        :return: None
        """
        alive = self.task_context.is_alive
        while alive:
            if exists(file_path):
                with open(file_path, "r") as log_f:
                    while alive:
                        log_line = log_f.readline()
                        logs = []
                        while log_line:
                            # construct list of dict
                            log = {
                                'log': log_line,
                                'timestamp': str(datetime.utcnow()),
                                'task_uuid': self.task_uuid,
                                'job_uuid': self.job_uuid,
                                'log_type': log_type
                            }
                            logs.append(log)
                            log_line = log_f.readline()

                        if len(logs) > 0:
                            self.upload_user_log(logs)
                            sleep(2)
                            alive = self.task_context.is_alive
            else:
                sleep(2)
                alive = self.task_context.is_alive

    def upload_user_log(self, logs) -> bool:
        """
        upload current batch logs to master server
        :param logs: logs should be a list of dict each represent a record in user_log table
        :return: bool, indicates if operation is successful
        """
        retries = 3
        while retries > 0:
            for log in logs:
                is_valid, message = validate_log(log)
                if not is_valid:
                    logs.remove(log)

            if len(logs) == 0:
                return False

            request_body = {
                'logs': json.dumps(logs)
            }
            success, status_code, response_body, error_message = request_server(
                self.master_endpoint + "/api/v1/worker/stream/",
                'post',
                **{"data": request_body,
                   "auth": self.auth_token})

            if success:
                return True
            else:
                retries -= 1

        return False


def validate_log(log) -> (bool, str):
    """
    validate the structure of log to see if that match the structure of record in tbl_user_log
    :param log: represents a record in tbl_user_log
    :return: bool, if the log is a valid record
    :return: str, message for error else None
    """
    required_attr_list = ['log', 'task_uuid', 'job_uuid', 'timestamp', 'log_type']
    for attr in required_attr_list:
        if attr not in log:
            return False, "Cannot find {} in log".format(log)

    try:
        uuid.UUID(log["task_uuid"], version=4)
    except:
        return False, "log contains invalid task_uuid: {}".format(log["task_uuid"])

    try:
        uuid.UUID(log["job_uuid"], version=4)
    except:
        return False, "log contains invalid job_uuid: {}".format(log["job_uuid"])

    if log['log_type'] not in ["user", "worker"]:
        return False, "log contains invalid log_type: {}".format(log['log_type'])

    if not validate_utctime_without_timezone(log["timestamp"]):
        return False, "log contains invalid timestamp: {}".format(log["timestamp"])

    if len(log['log']) > 1000:
        log['log'] = log['log'][0:1000]

    return True, None


def validate_utctime_without_timezone(time) -> bool:
    """
    validate if the string version of time is validate time without timezone
    :param time: str, generated from datetime.utcnow()
    :return: bool, indicates if this is valid
    """
    try:
        datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        return True
    except:
        return False
