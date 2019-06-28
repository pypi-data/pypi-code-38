from ._OncService import _OncService

class _OncRealTime(_OncService):
    """
    Near real-time services methods
    """

    def __init__(self, config: dict):
        super().__init__(config)
    

    def getDirectScalar(self, filters: dict, allPages: bool):
        '''
        Method to return scalar data from the scalardata service in JSON Object format
        which match filter criteria defined by a dictionary of filters.
        see https://wiki.oceannetworks.ca/display/help/scalardata+service for usage and available filters
        '''
        return self._getDirectAllPages(filters, 'scalardata', 'getByLocation', allPages)


    def getDirectRawByLocation(self, filters: dict, allPages: bool):
        '''
        Method to return raw data from an instrument, in the payload, in JSON format from the rawdata service 
        which match filter criteria defined by a dictionary of filters
        see https://wiki.oceannetworks.ca/display/help/rawdata+service for usage and available filters
        '''
        return self._getDirectAllPages(filters, 'rawdata', 'getByLocation', allPages)


    def getDirectRawByDevice(self, filters: dict, allPages: bool):
        '''
        Method to return raw data from an instrument, in the payload, in JSON format from the rawdata service 
        which match filter criteria defined by a dictionary of filters
        see https://wiki.oceannetworks.ca/display/help/rawdata+service for usage and available filters
        '''
        return self._getDirectAllPages(filters, 'rawdata', 'getByDevice', allPages)


    def _getDirectAllPages(self, filters: dict, service: str, method: str, allPages: bool):
        '''
        Keeps downloading all scalar or raw data pages until finished
        Return the full stitched data
        '''
        # prepare filters for first page request
        filters = filters or {}
        url = '{:s}api/{:s}'.format(self.baseUrl, service)
        filters['method'] = method
        filters['token'] = self.token

        try:
            fullResponse = self._doRequest(url, filters)

            # Grab the next pages if needed
            # if allPages and 'next' in fullResponse:
            #     while fullResponse['next'] != None:
            #         nextResponse = self._doRequest(fullResponse['next']['url'])
            #         fullResponse


            return fullResponse
        except Exception: raise