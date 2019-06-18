from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.User import User


class UsersMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return User:
        """
        return User(array)