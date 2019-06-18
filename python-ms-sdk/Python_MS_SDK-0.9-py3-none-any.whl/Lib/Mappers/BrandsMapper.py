from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Brand import Brand


class BrandsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Brand:
        """
        return Brand(array)
