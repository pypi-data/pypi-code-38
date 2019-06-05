from strongr.clouddomain.query import ListDeployedVms, RequestJidStatus

from strongr.core.exception import InvalidParameterException

class QueryFactory:
    def newListDeployedVms(self):
        """ Generates a new ListDeployedVms query

        :returns: A ListDeployedVms query object
        :rtype: ListDeployedVms
        """
        return ListDeployedVms()

    def newRequestJidStatus(self, jid):
        """ Generates a new RequestJidStatusquery

        :returns: A RequestJidStatus query object
        :rtype: RequestJidStatus
        """
        return RequestJidStatus(jid)

