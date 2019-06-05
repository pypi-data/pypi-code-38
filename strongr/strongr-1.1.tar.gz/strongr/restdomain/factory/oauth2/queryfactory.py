from strongr.restdomain.query.oauth2 import RetrieveClient, RetrieveGrant,\
                                            RetrieveTokenByAccessToken, RetrieveTokenByRefreshToken

from strongr.core.exception import InvalidParameterException

class QueryFactory:
    """ This factory instantiates query objects to be sent to a rest querybus. """
    def newRetrieveClient(client_id):
        """ Generates a new RetrieveClient query

        :param client_id: the client id
        :type client_id: string

        :returns: A RetrieveClient query object
        :rtype: RetrieveClient
        """
        client_id = client_id.strip()
        if not len(client_id) > 0:
            raise InvalidParameterException('Client id is invalid'.format(cmd))

        return RetrieveClient(client_id=client_id)

    def newRetrieveGrant(self, client_id, code):
        """ Generates a new RetrieveGrant query

        :param client_id: the client id
        :type client_id: string

        :param code: the code
        :type code: string

        :returns: A RetrieveGrant query object
        :rtype: RetrieveGrant
        """
        client_id = client_id.strip()
        if not len(client_id) > 0:
            raise InvalidParameterException('Client id is invalid'.format(cmd))

        code = code.strip()
        if not len(code) > 0:
            raise InvalidParameterException('Code is invalid'.format(cmd))

        return RetrieveGrant(client_id=client_id, code=code)

    def newRetrieveTokenByAccessToken(self, access_token):
        """ Generates a new RetrieveTokenByAccessToken query

        :param access_token: the access token
        :type access_token: string

        :returns: A RetrieveTokenByAccessToken query object
        :rtype: RetrieveTokenByAccessToken
        """
        client_id = client_id.strip()
        if not len(client_id) > 0:
            raise InvalidParameterException('Client id is invalid'.format(cmd))

        return RetrieveTokenByAccessToken(access_token)

    def newRetrieveTokenByRefreshToken(self, refresh_token):
        """ Generates a new RetrieveTokenByRefreshToken query

        :param refresh_token: the refresh token
        :type refresh_token: string

        :returns: A RetrieveTokenByRefreshToken query object
        :rtype: RetrieveTokenByRefreshToken
        """
        client_id = client_id.strip()
        if not len(client_id) > 0:
            raise InvalidParameterException('Client id is invalid'.format(cmd))

        return RetrieveTokenByRefreshToken(refresh_token)
