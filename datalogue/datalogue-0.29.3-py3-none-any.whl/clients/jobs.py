from typing import List, Union
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.job import Job, _job_from_payload
from datalogue.utils import _parse_list
from datalogue.errors import DtlError


class _JobsClient:
    """
    Client to interact with the Scheduled pipelines
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Job]]:
        """
        List the scheduled jobs

        TODO Pagination

        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available Datastores or an error message as a string
        """
        res = self.http_client.make_authed_request(
            self.service_uri + '/stream-collections/schedules', HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(_job_from_payload)(res)

    def cancel(self, job_id) -> Union[DtlError, Job]:
        """"
        Cancel a Job given job_id.

        :param job_id:
        :return: Returns the Job object canceled or an error
        """

        res = self.http_client.make_authed_request(
            self.service_uri + f"/v2/jobs/{job_id}/cancel", HttpMethod.POST,
        )

        if isinstance(res, DtlError):
            return res

        return _job_from_payload(res)
