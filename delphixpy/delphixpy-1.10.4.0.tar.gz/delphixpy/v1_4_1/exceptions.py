# 
# Copyright 2014, 2019 by Delphix
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

class RequestError(Exception):
    """
    Raised if the response to a Delphix REST API request is not "OK"
    """
    def __init__(self, error):
        super(RequestError, self).__init__(error)
        self._error = error

    @property
    def error(self):
        """
        Return an ErrorResult object describing this request error.
        """
        return self._error


class JobError(Exception):
    """
    Raised when a job fails
    """
    def __init__(self, value, job):
        super(JobError, self).__init__(value)
        self._job = job

    @property
    def job(self):
        """
        Return a Job object describing this job error.
        """
        return self._job


class HttpError(Exception):
    """
    Raised when a HTTP response has any other status than 200 (OK) or
    202 (ACCEPTED)
    """
    def __init__(self, value, status=None, data=None):
        """
        Creates a new HttpError object

        :param value: The value of the exception (mostly a string describing
                      the exception)
        :param status: The status of the HTTP Error (400, 403, 404, etc...)
        :param data: HTTP data as raw data.
        """
        super(HttpError, self).__init__(value)
        self.status = status
        self.data = data