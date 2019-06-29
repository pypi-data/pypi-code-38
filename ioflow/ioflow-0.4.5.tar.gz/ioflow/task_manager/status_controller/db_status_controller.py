import time

import requests

from ioflow.task_manager.status_controller.status_controller_base import \
    StatusControllerBase


class DbStatusController(StatusControllerBase):
    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.time_interval = config.get('db_status_check_interval', 10)

        self.code_mapping = {
            None: "",
            "1": self.PAUSE,
            "2": self.CONTINUE,
            "3": self.STOP
        }

        self.last_cmd = None

        super().__init__(*args, **kwargs)

    def main(self, pause_event, stop_event):
        last_check_timestamp = time.time()

        while True:
            # only check if time longer than time interval
            if last_check_timestamp + self.time_interval > time.time():
                time.sleep(self.time_interval / 10)
                continue

            last_check_timestamp = time.time()

            cmd = self.get_cmd()

            if not cmd or cmd == self.last_cmd:
                # cmd is not changed
                continue

            self.last_cmd = cmd

            self.exec(cmd, pause_event, stop_event)

    def get_cmd(self):
        r = requests.get(self.config['task_info_url'], params={'taskId': self.config['task_id']})
        data = r.json()

        operation = data['data'].get('operation', None)

        return self.code_mapping[operation]
