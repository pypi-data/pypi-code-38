from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.MediaType import MediaType


class ImageTypesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributeValue:
        """
        return MediaType(array)
