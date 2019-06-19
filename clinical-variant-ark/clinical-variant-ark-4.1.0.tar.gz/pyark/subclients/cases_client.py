import pyark.cva_client as cva_client
from protocols.protocol_7_2.cva import ReportEventType, Transaction
import logging
import pandas as pd


REPORT_EVENT_TYPES = [ReportEventType.genomics_england_tiering, ReportEventType.candidate, ReportEventType.reported,
                      ReportEventType.questionnaire]


class CasesClient(cva_client.CvaClient):

    _BASE_ENDPOINT = "cases"

    def __init__(self, url_base, token):
        cva_client.CvaClient.__init__(self, url_base, token=token)

    def count(self, **params):
        """
        :type params: dict
        :rtype: int
        """
        params['count'] = True
        return self.get_cases(**params)

    def get_cases_ids(self, as_data_frame=False, max_results=None, **params):
        """
        :type as_data_frame: bool
        :type max_results: int
        :type params: dict
        :rtype: generator
        """
        params['include'] = ["identifier", "version"]
        return self._paginate(
            endpoint=self._BASE_ENDPOINT, as_data_frame=as_data_frame, max_results=max_results,
            transformer=lambda x: "{}-{}".format(x["identifier"], x["version"]), **params)

    def get_cases(self, as_data_frame=False, max_results=None, include_all=True, **params):
        """
        :type as_data_frame: bool
        :type max_results: int
        :param include_all: use False for the default minimal representation of case, it will be faster
        :type include_all: bool
        :type params: dict
        :rtype: generator
        """
        if params.get('count', False):
            results, next_page_params = self._get(self._BASE_ENDPOINT, **params)
            return results[0]
        else:
            if include_all:
                params['include'] = [self._INCLUDE_ALL]
            return self._paginate(
                endpoint=self._BASE_ENDPOINT, as_data_frame=as_data_frame, max_results=max_results, **params)

    def get_summary(self, as_data_frame=False, params_list=[], **params):
        """
        :type as_data_frame: bool
        :type params_list: list
        :rtype: dict | pd.DataFrame
        """
        if params_list:
            self._params_sanity_checks(params_list)
            for p in params_list:
                p.update(params)
            results_list = [self.get_summary(as_data_frame=as_data_frame, **p) for p in params_list]
            return self._render_multiple_results(results_list, as_data_frame=as_data_frame)
        else:
            results, _ = self._get("{endpoint}/summary".format(endpoint=self._BASE_ENDPOINT), **params)
            if not results:
                logging.warning("No summary found")
                return None
            assert len(results) == 1, "Unexpected number of summaries"
            return self._render_single_result(results, as_data_frame=as_data_frame, indexes=params)

    def delete(self, case_id, case_version):
        path = "{endpoint}/{case_id}/{case_version}".format(
            endpoint=self._BASE_ENDPOINT, case_id=case_id, case_version=case_version
        )
        results, _ = self._delete(path)
        result = self._render_single_result(results)
        return Transaction.fromJsonDict(result) if result else None

    @staticmethod
    def _params_sanity_checks(params_list):
        if not all(isinstance(p, dict) for p in params_list):
            raise ValueError("Cannot accept a list of 'params' combined with other parameters. " +
                             "Include all parameters in the list")
        keys = None
        for p in params_list:
            if keys is None:
                keys = set(p.keys())
            else:
                if len(set(p.keys()).difference(keys)) > 0:
                    raise ValueError("Cannot accept a list of 'params' with different lists of filters")

    def get_case(self, identifier, version, as_data_frame=False, include_all=True, **params):
        """
        :type as_data_frame: bool
        :type identifier: str
        :type version: str
        :type include_all: bool
        :rtype: dict | pd.DataFrame
        """
        if include_all:
            params['include'] = [self._INCLUDE_ALL]
        results, _ = self._get("{endpoint}/{identifier}/{version}".format(
            endpoint=self._BASE_ENDPOINT, identifier=identifier, version=version), **params)
        if not results:
            logging.warning("No case found with id-version {}-{}".format(identifier, version))
            return None
        assert len(results) == 1, "Unexpected number of cases returned when searching by identifier"
        return self._render_single_result(results, as_data_frame=as_data_frame)

    def get_case_by_identifiers(self, identifiers, as_data_frame=False, include_all=True, **params):
        """
        :type as_data_frame: bool
        :type identifiers: list
        :type include_all: bool
        :rtype: list | pd.DataFrame
        """
        if include_all:
            params['include'] = [self._INCLUDE_ALL]
        results, _ = self._get("{endpoint}/{identifiers}".format(
            endpoint=self._BASE_ENDPOINT, identifiers=",".join(identifiers)), **params)
        return self._render(results, as_data_frame=as_data_frame)

    def search(self, query):
        results, _ = self._get("{endpoint}/search/{query}".format(endpoint=self._BASE_ENDPOINT, query=query))
        return self._render(results, as_data_frame=False)

    def get_similar_cases_by_case(self, case_id, case_version, as_data_frame=False, **params):
        """
        :type as_data_frame: bool
        :type case_id: str
        :type case_version: int
        :type params: dict
        :rtype: list | pd.DataFrame
        """
        results, _ = self._get([self._BASE_ENDPOINT, case_id, case_version, "similar-cases"], **params)
        if not results:
            logging.warning("No similar cases found")
            return None
        return self._render(results, as_data_frame=as_data_frame)

    def get_similar_cases_by_phenotypes(self, phenotypes, as_data_frame=False, **params):
        """
        :type as_data_frame: bool
        :type phenotypes: list
        :type params: dict
        :rtype: list | pd.DataFrame
        """
        params['hpoIds'] = phenotypes
        results, _ = self._get([self._BASE_ENDPOINT, "phenotypes", "similar-cases"], **params)
        if not results:
            logging.warning("No similar cases found")
            return None
        return self._render(results, as_data_frame=as_data_frame)

    def get_shared_variants_cases_by_case(self, case_id, case_version, report_event_type, **params):
        """
        :type case_id: str
        :type case_version: int
        :type report_event_type: ReportEventType
        :type limit: int
        :type params: dict
        :rtype: list
        """
        assert report_event_type in REPORT_EVENT_TYPES, \
            "Invalid report event type provided '{}'. Valid values: {}".format(report_event_type, REPORT_EVENT_TYPES)
        params['type'] = report_event_type
        results, _ = self._get([self._BASE_ENDPOINT, case_id, case_version, "shared-variants"], **params)
        if not results:
            logging.warning("No cases sharing {} variants found".format(report_event_type))
            return None
        return results

    def get_shared_genes_cases_by_case(self, case_id, case_version, report_event_type, **params):
        """
        :type case_id: str
        :type case_version: int
        :type report_event_type: ReportEventType
        :type params: dict
        :rtype: list
        """
        assert report_event_type in REPORT_EVENT_TYPES, \
            "Invalid report event type provided '{}'. Valid values: {}".format(report_event_type, REPORT_EVENT_TYPES)
        params['type'] = report_event_type
        results, _ = self._get([self._BASE_ENDPOINT, case_id, case_version, "shared-genes"], **params)
        if not results:
            logging.warning("No cases sharing {} genes found".format(report_event_type))
            return None
        return results

    def get_shared_variants_counts(self, variant_ids, **params):
        """
        :type variant_ids: list
        :type params: dict
        :rtype: list
        """
        variant_coordinates = [v.toJsonDict() for v in self.variants().variant_ids_to_coordinates(variant_ids)]
        results, _ = self._post([self._BASE_ENDPOINT, "shared-variants-counts"], variant_coordinates, **params)
        return results

    def get_phenosim_matrix(self, as_data_frame=False, **params):
        """
        :type as_data_frame: bool
        :rtype: list | pd.DataFrame
        """
        results, _ = self._get("{endpoint}/similarity-matrix".format(endpoint=self._BASE_ENDPOINT), **params)
        if not results:
            logging.warning("No similarity matrix found")
            return None
        return self._render(results, as_data_frame=as_data_frame)
