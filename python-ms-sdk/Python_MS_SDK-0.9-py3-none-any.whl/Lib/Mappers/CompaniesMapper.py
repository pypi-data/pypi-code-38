from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Company import Company


class CompaniesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Company:
        """
        return Company(array)