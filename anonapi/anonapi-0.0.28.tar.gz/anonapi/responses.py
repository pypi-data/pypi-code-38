"""Models things that an API server can send back. Bridge between raw json and actual python objects

It would be much nicer to use an existing library that does serialization of python models on the server side and the
client side. But we're not using django yet.

"""

from collections import UserList


class JobStatus:
    """ Job status string the API server uses
    """
    ERROR = 'ERROR'
    DONE = 'DONE'
    UPLOADED = 'UPLOADED'
    INACTIVE = 'INACTIVE'
    ACTIVE = 'ACTIVE'


class APIResponse:
    """A response from the Anonymizationserver web API
    """
    pass


def format_job_info_list(job_infos):
    """To list that can be printed to console

    Parameters
    ----------
    job_infos: List(JobShortInfo)
        List of short infos

    Returns
    -------
    str:
        Nice string representation of this list

    """

    header = (
        "id     date                 status   downloaded processed  user\n"
        "---------------------------------------------------------------"
    )
    info_string = header

    for job_info in job_infos:
        x: JobShortInfo = job_info
        info_line = (
            f"{x.job_id:<6} {x.date:<20} {x.status:<8} {str(x.files_downloaded):<10} "
            f"{str(x.files_processed):<10} {x.user_name}"
        )
        info_string += "\n" + info_line

    return info_string


def parse_job_infos_response(response):
    """

    Parameters
    ----------
    response: dict
        API Response to 'get_jobs' method

    Raises
    ------
    APIParseResponseException:
        When response cannot be parsed

    Returns
    -------
    List(job_infos)

    """
    try:
        return [JobShortInfo(x) for x in response.values()]
    except (KeyError, AttributeError) as e:
        raise APIParseResponseException(f"Error parsing server response as job info: {e}")


class JobShortInfo:
    """Info on a single job, with some easy to retrieve data
    """

    def __init__(self, json_raw):
        self.job_id = json_raw['job_id']
        self.date = json_raw['date']
        self.user_name = json_raw['user_name']
        self.status = json_raw['status']
        self.error = json_raw['error']
        self.description = json_raw['description']
        self.project_name = json_raw['project_name']
        self.priority = json_raw['priority']
        self.files_downloaded = json_raw['files_downloaded']
        self.files_processed = json_raw['files_processed']


class JobsInfoList(UserList):

    def __init__(self, job_infos):
        """A list job infos that can be conveniently printed

        Parameters
        ----------
        job_infos: List(JobShortInfo)

        """
        self.data = job_infos

    def as_table_string(self):
        """As a string with newlines, forming a neat table

        Returns
        -------
        str:
            string with newlines

        """
        return format_job_info_list(self.data)


class APIParseResponseException(Exception):
    pass
