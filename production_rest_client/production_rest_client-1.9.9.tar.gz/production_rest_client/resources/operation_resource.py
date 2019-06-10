# coding=utf-8
# pylint: disable=import-error, broad-except
import os
import json
from resources.models.helper import rest_post_json_call
from resources.models.helper import State
from resources.models.ftp_client import FtpClient

class OperationResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def _upload_fw_bin(self, fw_path):
        ret = False
        try:
            ftp_client = FtpClient(self.host, 10021, "ftp_user", "Cnex!321")
            ret = ftp_client.upload_binary_file(fw_path)
        except Exception as exceptions:
            print(exceptions)
        return ret

    def upgrade(self, fw_path, device_index=1, slot=2):
        if self._upload_fw_bin(fw_path) is True:
            file_name = os.path.basename(fw_path)
            data = {"operate_name":"upgrade", "fw": file_name, "device_index":device_index, "slot":slot}
            url_ = "http://{0}:{1}/operation".format(self.host, self.port)
            result = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
        else:
            result = dict()
            result["resource"] = {"data": None, "state": State.ERROR_BASE_EXCEPTION,
                                  "msg": "Send fw bin to test environment failed."}
        return result["resource"]
