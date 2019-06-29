import requests


task_status_registry = {}


def get_task_status_class(config):
    return task_status_registry[config.get('task_status_schema', 'raw')]


def registry_task_status_class(schema, class_):
    task_status_registry[schema] = class_


class BaseTaskStatus(object):
    def __init__(self, config):
        self.config = config

    def send_status(self, status):
        raise NotImplementedError


class RawTaskStatus(BaseTaskStatus):
    def __init__(self, config):
        self.DONE = 10
        self.START = 1
        super().__init__(config)

    def send_status(self, status):
        print('{}:{}'.format(self.__class__, status))


registry_task_status_class('raw', RawTaskStatus)


class HttpTaskStatus(BaseTaskStatus):
    def __init__(self, config):
        self.DONE = 10
        self.START = 1

        super().__init__(config)

    def send_status(self, status):
        print('{}:{}'.format(self.__class__, status))

        code_to_str = {
            self.DONE: 'done',
            self.START: 'start'
        }
        if status in code_to_str:
            data = {'progress': code_to_str[status]}
        else:
            data = status

        json_data = {'id': self.config['task_id']}
        json_data.update(data)

        r = requests.post(self.config['progress_report_url'], json=json_data)
        assert r.status_code == 200


registry_task_status_class('http', HttpTaskStatus)


if __name__ == "__main__":
    task_status_class = get_task_status_class({})
    config = {
        "progress_report_url": "http://10.43.13.8:25005/redis",
        "task_id": "121554"
    }

    ts = task_status_class(config)
    ts.send_status(ts.START)
