import re
import logging
import pandas as pd
from pandas.io.json import json_normalize
from pyark.rest_client import RestClient
import multiprocessing


class CvaClient(RestClient):

    _regx = re.compile("^test_", re.IGNORECASE)

    _ENDPOINT_BASE = "cva/api/0"

    _LIMIT_PARAM = 'limit'
    _MARKER_PARAM = 'marker'
    _LIMIT_HEADER = 'X-Pagination-Limit'
    _MARKER_HEADER = 'X-Pagination-Marker'

    # authentication endpoint
    _AUTHENTICATION_ENDPOINT = "authentication"

    _INCLUDE_ALL = "__all"

    def __init__(self, url_base, token=None, user=None, password=None,
                 disable_validation=True, disable_annotation=False, retries=10):

        if not (token or (user and password is not None)):
            logging.error("Credentials are required. Either token or user/password.")
            raise ValueError("Missing credentials")
        RestClient.__init__(self, url_base, self._ENDPOINT_BASE, retries=retries)
        self._disable_validation = disable_validation
        self._disable_annotation = disable_annotation
        self._push_data_params = {'disable_validation': self._disable_validation,
                                 'disable_annotation': self._disable_annotation}
        self._token = "Bearer {}".format(token.replace("Bearer ", "")) if token else None
        self._user = user
        self._password = password
        if self._token or (self._user is not None and self._password is not None):
            self._set_authenticated_header()
        # initialise subclients
        self._report_events_client = None
        self._entities_client = None
        self._cases_client = None
        self._pedigrees_client = None
        self._variants_client = None
        self._lift_overs_client = None
        self._data_intake_client = None
        self._transactions_client = None
        self._evidences_client = None

    def _get_token(self):
        results, _ = self._post(self._AUTHENTICATION_ENDPOINT, payload={
            'username': self._user,
            'password': self._password
        })
        return "Bearer {}".format(results[0]['token'])

    def _post(self, endpoint, payload, session=True, **params):
        response, headers = super(CvaClient, self)._post(endpoint, payload, session, **params)
        return CvaClient._parse_result(response), CvaClient._build_next_page_params(headers)

    def _get(self, endpoint, session=True, **params):
        response, headers = super(CvaClient, self)._get(endpoint, session, **params)
        return CvaClient._parse_result(response), CvaClient._build_next_page_params(headers)

    def _delete(self, endpoint, **params):
        response, headers = super(CvaClient, self)._delete(endpoint, **params)
        return CvaClient._parse_result(response), CvaClient._build_next_page_params(headers)

    @staticmethod
    def run_parallel_requests(method, parameters):
        """
        :type method: function
        :type parameters: list
        :rtype: object
        """
        pool = multiprocessing.Pool(processes=10)
        results = list(pool.map(method, parameters))
        pool.close()
        pool.join()
        return results

    def report_events(self):
        """

        :return:
        :rtype: ReportEventsClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.report_events_client
        if self._report_events_client is None:
            # initialise subclients
            self._report_events_client = pyark.subclients.report_events_client.ReportEventsClient(
                self._url_base, self._token)
        return self._report_events_client

    def entities(self):
        """

        :return:
        :rtype: PanelsClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.entities_client
        if self._entities_client is None:
            # initialise subclients
            self._entities_client = pyark.subclients.entities_client.EntitiesClient(self._url_base, self._token)
        return self._entities_client

    def cases(self):
        """

        :return:
        :rtype: CasesClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.cases_client
        if self._cases_client is None:
            # initialise subclients
            self._cases_client = pyark.subclients.cases_client.CasesClient(
                self._url_base, self._token)
        return self._cases_client

    def pedigrees(self):
        """

        :return:
        :rtype: CasesClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.pedigrees_client
        if self._pedigrees_client is None:
            # initialise subclients
            self._pedigrees_client = pyark.subclients.pedigrees_client.PedigreesClient(
                self._url_base, self._token)
        return self._pedigrees_client

    def variants(self):
        """

        :return:
        :rtype: VariantsClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.variants_client
        if self._variants_client is None:
            # initialise subclients
            self._variants_client = pyark.subclients.variants_client.VariantsClient(
                self._url_base, self._token)
        return self._variants_client

    def transactions(self):
        """

        :return:
        :rtype: VariantsClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.transactions_client
        if self._transactions_client is None:
            # initialise subclients
            self._transactions_client = pyark.subclients.transactions_client.TransactionsClient(
                self._url_base, self._token)
        return self._transactions_client

    def evidences(self):
        import pyark.subclients.evidences_client
        if self._evidences_client is None:
            # initialise subclients
            self._evidences_client = pyark.subclients.evidences_client.EvidencesClient(
                self._url_base, self._token)
        return self._evidences_client

    def lift_overs(self):
        """

        :return:
        :rtype: LiftOverClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.lift_over_client
        if self._lift_overs_client is None:
            # initialise subclients
            self._lift_overs_client = pyark.subclients.lift_over_client.LiftOverClient(
                self._url_base, self._token)
        return self._lift_overs_client

    def data_intake(self):
        """

        :return:
        :rtype: DataIntakeClient
        """
        # NOTE: this import needs to be here due to circular imports
        import pyark.subclients.data_intake_client
        if self._data_intake_client is None:
            # initialise subclients
            self._data_intake_client = pyark.subclients.data_intake_client.DataIntakeClient(
                self._url_base, self._token)
        return self._data_intake_client

    @staticmethod
    def _build_next_page_params(headers):
        next_page_params = {}
        limit = headers.get(CvaClient._LIMIT_HEADER, None)
        marker = headers.get(CvaClient._MARKER_HEADER, None)
        if marker:
            next_page_params[CvaClient._LIMIT_PARAM] = limit
            next_page_params[CvaClient._MARKER_PARAM] = marker
        return next_page_params

    @staticmethod
    def _parse_result(response):
        logging.info("Response time : {} ms".format(response.get('time', None)))
        error = response.get('error', None)
        if error:
            logging.error(error)
            raise ValueError(error)
        warning = response.get('warning', None)
        if warning:
            logging.warning(warning)
        if 'response' in response and len(response['response']) > 0 and 'result' in response['response'][0]:
            return response['response'][0]['result']
        else:
            return []

    def _render_single_result(self, results, as_data_frame=False, indexes={}):
        if results is None or len(results) == 0:
            return None
        first = results[0]
        return self._render(first, as_data_frame=as_data_frame, indexes=indexes)

    def _render_multiple_results(self, results, as_data_frame=False):
        if results is None or len(results) == 0:
            return None
        if as_data_frame:
            return pd.concat(results)
        else:
            return results

    @staticmethod
    def _render(results, as_data_frame=False, indexes={}):
        if as_data_frame:
            if results:
                df = json_normalize(results)
                if indexes:
                    df.index = pd.MultiIndex.from_arrays(
                        [[values] if type(values) != list else indexes.values() for values in indexes.values()],
                        names=list(indexes.keys()))
                return df
            else:
                return pd.DataFrame()
        else:
            return results

    def _paginate(self, endpoint, as_data_frame=False, max_results=None, transformer=None, **params):
        more_results = True
        count_returned = 0
        while more_results:
            if max_results and count_returned >= max_results:
                return
            results, next_page_params = self._get(endpoint, **params)
            results = list(results)
            if transformer:
                results = list(map(transformer, results))
            if next_page_params:
                params[CvaClient._LIMIT_PARAM] = next_page_params[CvaClient._LIMIT_PARAM]
                params[CvaClient._MARKER_PARAM] = next_page_params[CvaClient._MARKER_PARAM]
            else:
                more_results = False
            if max_results and len(results) > max_results - count_returned:
                # removes those elements in the page that overflow the maximum parameter
                results = results[0:max_results-count_returned]
            # NOTE: when returning a data frame we want all results in a batch in the
            # same data frame, otherwise we want to iterate through them one by one
            if as_data_frame:
                df = self._render(results, as_data_frame=as_data_frame)
                df['_index'] = list(range(count_returned, count_returned + len(results)))
                df.set_index('_index', drop=True, inplace=True)
                count_returned += len(results)
                yield df
            else:
                for r in results:
                    count_returned += 1
                    yield r
