from strongr.restdomain.command.oauth2 import AppendGrant

from strongr.core.exception import InvalidParameterException

class CommandFactory:
    """ This factory instantiates command objects to be sent to a rest commandbus. """
    def newAppendGrant(client_id, code, redirect_uri, scope, user_id, expires):
        """ Generates a new AppendGrant command

        :param client_id: the client id
        :type client_id: string

        :param code: the code
        :type code: string

        :param redirect_uri: the redirect uri
        :type redirect_uri: string

        :param scope: the scope
        :type scope: string

        :param user_id: the user_id
        :type user_id: string

        :param expires: when should the grant expire?
        :type expires: int

        :returns: An AppendGrant command object
        :rtype: AppendGrant
        """
        client_id = client_id.strip()
        if not len(client_id) > 0:
            raise InvalidParameterException('Client id is invalid'.format(cmd))

        code = code.strip()
        if not len(code) > 0:
            raise InvalidParameterException('Code is invalid'.format(cmd))

        redirect_uri = redirect_uri.strip()
        if not len(redirect_uri) > 0:
            raise InvalidParameterException('Redirect uri is invalid'.format(cmd))

        scope = scope.strip()
        if not len(scope) > 0:
            raise InvalidParameterException('Scope is invalid'.format(cmd))

        user_id = user_id.strip()
        if not len(user_id) > 0:
            raise InvalidParameterException('User id is invalid'.format(cmd))


        if not expires >= 0:
            raise InvalidParameterException('Expires is invalid'.format(cmd))

        return AppendGrant(client_id, code, redirect_uri, scope, user_id, expires)
