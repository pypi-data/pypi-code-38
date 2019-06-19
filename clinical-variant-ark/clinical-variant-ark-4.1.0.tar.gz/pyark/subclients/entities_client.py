import pyark.cva_client as cva_client
import pandas as pd


class EntitiesClient(cva_client.CvaClient):

    def __init__(self, url_base, token):
        cva_client.CvaClient.__init__(self, url_base, token=token)

    def get_panels_summary(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return: returns all observed panels and the number of cases on which they were applied.
        :rtype: list or pd.DataFrame
        """
        results, _ = self._get("panels", **params)
        # some additional flattening
        return self._render(results, as_data_frame=as_data_frame)

    def get_panels_by_regex(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return: returns observed panels matching the regex.
        :rtype: list or pd.DataFrame
        """
        results, _ = self._get("panels/search", **params)
        return self._render(results, as_data_frame=as_data_frame)

    def get_all_panels(self, **params):
        """
        :return: return a list of observed panel names
        :rtype: pd.Series
        """
        results = self.get_panels_summary(consider_versions=False, **params)
        all_panels = [x['panel']['panelName'] for x in results]
        return pd.Series(all_panels, index=all_panels)

    def get_disorders_summary(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return:
        :rtype: list or pd.DataFrame
        """
        results, _ = self._get("disorders", **params)
        return self._render(results, as_data_frame=as_data_frame)

    def get_disorders_by_regex(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return: returns observed disorders matching the regex.
        :rtype: list or pd.DataFrame
        """
        results, _ = self._get("disorders/search", **params)
        return self._render(results, as_data_frame=as_data_frame)

    def get_all_specific_diseases(self, **params):
        """
        :return: return a list of observed specific diseases
        :rtype: pd.Series
        """
        results = self.get_disorders_summary(**params)
        all_diseases = list(set([x['disorder']['specificDisease'] for x in results]))
        return pd.Series(all_diseases, index=all_diseases)

    def get_all_disease_groups(self, **params):
        """
        :return: return a list of observed disease groups
        :rtype: pd.Series
        """
        results = self.get_disorders_summary(**params)
        all_disease_groups = list(set([x['disorder']['diseaseGroup'] for x in results]))
        return pd.Series(all_disease_groups, index=all_disease_groups)

    def get_all_disease_subgroups(self, **params):
        """
        :return: return a list of observed disease subgroups
        :rtype: pd.Series
        """
        results = self.get_disorders_summary(**params)
        all_disease_subgroups = list(set([x['disorder']['diseaseSubGroup'] for x in results]))
        return pd.Series(all_disease_subgroups, index=all_disease_subgroups)

    def get_genes_summary(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return:
        :rtype: list or pd.DataFrame
        """
        results, _ = self._get("genes", **params)
        return self._render(results, as_data_frame=as_data_frame)

    def get_genes(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return:
        """
        results, _ = self._get(endpoint="genes/search", **params)
        return self._render(results, as_data_frame=as_data_frame)

    def get_phenotypes(self, as_data_frame=False, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return:
        """
        results, _ = self._get(endpoint="phenotypes", **params)
        return self._render(results, as_data_frame=as_data_frame)

    def get_hpo(self, identifier, as_data_frame=False):
        """
        :param identifier: An HPO identifier as in HP:00012345
        :type identifier: dict
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return:
        :rtype: list or pd.DataFrame
        """
        results, _ = self._get("hpos/{id}".format(id=identifier))
        return self._render(results, as_data_frame=as_data_frame)

    def get_hpos(self, as_data_frame=False, max=None, **params):
        """
        :param as_data_frame: return results in a flattened Pandas data frame or in a list of dictionaries
        :type as_data_frame: bool
        :return:
        """
        return self._paginate(endpoint="hpos/search", as_data_frame=as_data_frame, max=max, **params)
