""" Shared classes used in other tests. For generating test data """
from unittest.mock import Mock
from requests.models import Response


class RequestsMock:
    """ Can be put in place of the requests module. Does not hit any server but returns kind of realistic arbitrary
    responses

    """

    def __init__(self):
        self.requests = Mock()  # for keeping track of past requests

    def set_response(self, text, status_code=200):
        """Any call to get() or post() will yield a Response() object with the given parameters

        Parameters
        ----------
        text: str
            content to return
        status_code: int, optional
            http return code. Defaults to 200

        """
        response = Response()
        response.encoding = "utf-8"
        response.status_code = status_code
        response._content = bytes(text, response.encoding)

        self.requests.get.return_value = response
        self.requests.post.return_value = response

    def set_response_exception(self, exception):
        """Any call to get() or post() will yield the given exception
        """
        self.requests.get.side_effect = exception
        self.requests.post.side_effect = exception

    def get(self, *args, **kwargs):
        return self.requests.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.requests.post(*args, **kwargs)

    def reset(self):
        self.requests.reset_mock()

    def called(self):
        """True if either get() or post() was called"""
        return self.requests.get.called or self.requests.post.called


class RequestsMockResponseExamples:
    """Some examples of http response texts that an anonymization web API server might send back. Harvested and
    simplified these from a live API server running git revision 9c36082e3dafab5fac0fb9d34963970493b20776 in diag repo

    """

    API_CALL_NOT_DEFINED = (
        r'{"404": "The API call you tried to make is not defined, here is some documentation", '
        r'"documentation":{"overview":"some docs"}}'
    )

    JOBS_LIST_GET_JOBS = (
        '{"1": {"job_id": 1, "date": "2018-10-26T14:56:34", "user_name": "z123sandbox", "status":'
        ' "INACTIVE", "error": null, "description": null, "project_name": "Wetenschap-Algemeen", "priority": 0,'
        ' "files_downloaded": null, "files_processed": null}, "2": {"job_id": 2, '
        '"date": "2018-09-19T11:16:57", "user_name": "z123sandbox", "status": "ACTIVE", "error": null,'
        ' "description": "For RSNA2018. see ticket #1672", "project_name": "ProCAD", "priority": 0,'
        ' "files_downloaded": null, "files_processed": null}}'
    )  # Response to 'get_jobs'

    JOBS_LIST_GET_JOBS_LIST = (
        '{"1000": {"job_id": 1000, "date": "2016-08-26T15:04:44", "user_name": "Z495159", '
        '"status": "DONE", "error": null, "description": null, "project_name": "testproject", "priority": 1,'
        ' "files_downloaded": 0, "files_processed": 0}, "1002": {"job_id": 1002, "date": "2016-08-26T15:04:44",'
        ' "user_name": "Z495159", "status": "UPLOADED", "error": null, "description": null, '
        '"project_name": "testproject", "priority": 1, "files_downloaded": 0, "files_processed": 0},'
        ' "5000": {"job_id": 5000, "date": "2016-09-23T20:46:51", "user_name": "Z495159", "status": '
        '"UPLOADED", "error": null, "description": null, "project_name": "testproject", "priority": 1,'
        ' "files_downloaded": 3, "files_processed": 3}}'
    )  # Response to 'get_jobs_list'

    JOBS_LIST_GET_JOBS_LIST_WITH_ERROR = (
        '{"1": {"job_id": 1, "date": "2016-08-26T15:04:44", "user_name": "Z495159", '
        '"status": "ERROR", "error": "Something wrong", "description": null, "project_name": "testproject", '
        '"priority": 1, "files_downloaded": 0, "files_processed": 0}, "2": {"job_id": 2, "date": "2016-08-26T15:04:44",'
        ' "user_name": "Z495159", "status": "UPLOADED", "error": null, "description": null, '
        '"project_name": "testproject", "priority": 1, "files_downloaded": 0, "files_processed": 0},'
        ' "3": {"job_id": 3, "date": "2016-09-23T20:46:51", "user_name": "Z495159", "status": '
        '"ERROR", "error": "Terrible error", "description": null, "project_name": "testproject", "priority": 1,'
        ' "files_downloaded": 3, "files_processed": 3}}'
    )  # Response to 'get_jobs_list'

    JOB_INFO = (
        r'{"job_id": 3, "date": "2018-08-31T11:11:05", "user_name": "z123sandbox", "status": "INACTIVE",'
        r' "error": null, "description": null, "project_name": "Wetenschap-Algemeen", "priority": 10,'
        r' "files_downloaded": null, "files_processed": null, "destination_id": 44777, '
        r'"destination_name": null, "destination_path": "\\\\resfilsp10\\imaging\\temp\\test_output",'
        r' "destination_network": null, "destination_status": "BASE", "destination_type": "PATH",'
        r' "source_id": 44777, "source_instance_id": null, "source_status": "NEW", "source_type": "PATH",'
        r' "source_anonymizedpatientid": null, "source_anonymizedpatientname": null, "source_name": null,'
        r' "source_path": "f", "source_protocol": 3178, "source_subject": 3178}'
    )

    JOB_DOES_NOT_EXIST = r'{"errors": {"job_id": "Job with id 447783 does not exist"}}'

    REQUIRED_PARAMETER_NOT_SUPPLIED = (
        r'{"errors": {"job_id": "Required parameter job_id not supplied"}}'
    )
