import pyark.cva_client as cva_client
from protocols.protocol_7_2.cva import VariantsCoordinates, VariantCoordinates


class LiftOverClient(cva_client.CvaClient):

    _BASE_ENDPOINT = "lift-overs"

    def __init__(self, url_base, token):
        cva_client.CvaClient.__init__(self, url_base, token=token)
        self.variants_client = self.variants()

    def lift_over_by_identifiers(self, variant_identifiers, **params):
        """
        :param variant_identifiers: the list of variant identifiers in format
        {assembly}:{chromosome}:{position}:{reference}:{alternate}
        :type variant_identifiers: list
        :return list of VariantCoordinates
        :rtype: list
        """
        variant_coordinates_list = self.variants_client.variant_ids_to_coordinates(variant_identifiers)
        variants_coordinates = VariantsCoordinates()
        variants_coordinates.variants = variant_coordinates_list

        results, _ = self._post(self._BASE_ENDPOINT, payload=variants_coordinates.toJsonDict(), **params)
        assert len(results) == len(variant_identifiers), "Some variants failed to lift over"

        return [VariantCoordinates.fromJsonDict(x) for x in results]

    def lift_over_by_variants_coordinates(self, variant_coordinates_list, **params):
        """
        :param variant_coordinates_list: the list of VariantCoordinates
        :type variant_coordinates_list: list
        :return list of VariantCoordinates
        :rtype: list
        """
        variants_coordinates = VariantsCoordinates()
        variants_coordinates.variants = variant_coordinates_list

        results, _ = self._post(self._BASE_ENDPOINT, payload=variants_coordinates.toJsonDict(), **params)
        assert len(results) == len(variant_coordinates_list), "Some variants failed to lift over"

        return [VariantCoordinates.fromJsonDict(x) for x in results]
