from pyark import cva_client
import logging


class PedigreesClient(cva_client.CvaClient):

    _BASE_ENDPOINT = "pedigrees"

    def __init__(self, url_base, token):
        cva_client.CvaClient.__init__(self, url_base, token=token)

    def get_pedigree(self, identifier, version, as_data_frame=False):
        results, _ = self._get("{endpoint}/{identifier}/{version}".format(
            endpoint=self._BASE_ENDPOINT, identifier=identifier, version=version))
        if not results:
            logging.warning("No pedigree found with id-version {}-{}".format(identifier, version))
            return None
        assert len(results) == 1, "Unexpected number of pedigrees returned when searching by identifier"
        return self._render_single_result(results, as_data_frame=as_data_frame)
