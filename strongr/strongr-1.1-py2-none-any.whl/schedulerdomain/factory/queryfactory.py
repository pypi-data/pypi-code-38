from strongr.schedulerdomain.model import VmState
from strongr.schedulerdomain.query import RequestScheduledJobs, RequestFinishedJobs, RequestJobInfo, FindNodeWithAvailableResources, RequestResourcesRequired, RequestVmsByState

from strongr.core.exception import InvalidParameterException

import re

class QueryFactory:
    """ This factory instantiates query objects to be sent to a scheduler querybus. """

    def newRequestVms(self, states):
        """ Generates a new RequestVms query
        :returns: A RequestVms query object
        :rtype: RequestVmsByState
        """
        if not isinstance(states, list):
            raise InvalidParameterException("states invalid")

        for state in states:
            if state not in VmState:
                raise InvalidParameterException("{} is not a valid VmState".format(state))

        return RequestVmsByState(states)

    def newRequestResourcesRequired(self):
        """ Generates a new RequestResourcesRequired query
        :returns: A RequestResourcesRequired query object
        :rtype: RequestResourcesRequired
        """
        return RequestResourcesRequired()

    def newFindNodeWithAvailableResources(self, cores, ram):
        """ Generates a new FindNodeWithAvailableResources query

        :param cores: the amount of cores needed to complete the task
        :type cores: int
        :param ram: the amount of ram needed to complete the task in GiB
        :type ram: int

        :returns: A FindNodeWithAvailableResources query object
        :rtype: FindNodeWithAvailableResources
        """
        return FindNodeWithAvailableResources(cores=cores, ram=ram)

    def newRequestScheduledJobs(self):
        """ Generates a new RequestScheduledJobs query

        :returns: A RequestScheduledJobs query object
        :rtype: RequestScheduledJobs
        """
        return RequestScheduledJobs()

    def newRequestFinishedJobs(self, jobs=None):
        """ Generates a new RequestFinishedJobs query

        :param jobs: a list of job id's

        :returns: A RequestFinishedJobs query object
        :rtype: RequestFinishedJobs
        """
        jobs_sanitized = [re.sub('[^a-zA-Z0-9-]', '', x) for x in jobs] # sanitize inputs


        return RequestFinishedJobs(jobs_sanitized)

    def newRequestJobInfo(self, jobs=None):
        """ Generates a new RequestFinishedJobs query

        :param jobs: a list of job id's

        :returns: A RequestFinishedJobs query object
        :rtype: RequestFinishedJobs
        """
        jobs_sanitized = [re.sub('[^a-zA-Z0-9-]', '', x) for x in jobs] # sanitize inputs


        return RequestJobInfo(jobs_sanitized)

    def newRequestTaskInfo(self, taskid):
        """ Generates a new RequestTaskInfo query

        :param taskid: the taskid
        :type taskid: string

        :returns: A RequestTaskInfo query object
        :rtype: RequestJobInfo
        """
        return RequestJobInfo(taskid)
