from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.SMEntity import SMEntity


class EntitiesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return SMEntity:
        """
        return SMEntity(array)
