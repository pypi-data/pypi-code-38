from strongr.authdomain.query import IsValidUser

from strongr.core.exception import InvalidParameterException

class QueryFactory:
    def newIsValidUserQuery(self, username, password):
        """ Generates a new IsValidUser query

        :returns: An IsValidUser query object
        :rtype: IsValidUser
        """
        if username == None or len(username) == 0 or len(username.strip()) == 0:
            raise InvalidParameterException('Username is invalid')

        if password == None or len(password) == 0:
            raise InvalidParameterException('Password is invalid')

        return IsValidUser(username, password)
