from guillotina.auth.users import GuillotinaUser
from guillotina_authentication import utils
from guillotina.auth import authenticate_user


class OAuthUser(GuillotinaUser):

    def __init__(self, user_id, properties):
        super(OAuthUser, self).__init__(user_id, properties)
        self._validated_jwt = None

    def apply_scope(self, validated_jwt, container_id):
        self._validated_jwt = validated_jwt
        allowed_scopes = validated_jwt.get('allowed_scopes') or []
        for scope in validated_jwt.get('scope') or []:
            if scope not in allowed_scopes:
                continue
            split = scope.split(':')
            if len(split) not in (2, 3):
                continue
            if len(split) == 3:
                if container_id is None:
                    # on root, do not apply this guy...
                    continue
                if container_id != split[0]:
                    continue
            if split[-2] == 'role':
                self._roles[split[-1]] = 1
            if split[-2] == 'permission':
                self._permissions[split[-1]] = 1

    async def refresh(self, scopes):
        client = utils.get_client(
            self._validated_jwt['client'],
            **self._validated_jwt['client_args'])

        refresh_token = self._validated_jwt['client_args']['refresh_token']
        otoken, otoken_data = await client.get_access_token(
            refresh_token, grant_type='refresh_token')

        client_args = dict(
            access_token=otoken,
            refresh_token=refresh_token)

        if 'expires_in' in otoken_data:
            timeout = otoken_data['expires_in']
        else:
            timeout = 60 * 60 * 1

        user, user_data = await client.user_info()

        jwt_token, data = authenticate_user(user.id, {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'client': self._validated_jwt['client'],
            'client_args': client_args,
            'allowed_scopes': user_data.get('allowed_scopes'),
            'scope': scopes,
            'identifier': 'oauth'
        }, timeout=timeout)

        result = {
            'exp': data['exp'],
            'token': jwt_token
        }
        return result