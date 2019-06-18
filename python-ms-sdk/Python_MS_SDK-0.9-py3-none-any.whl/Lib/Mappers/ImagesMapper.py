from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Media import Media


class ImagesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Media:
        """
        return Media(array)
