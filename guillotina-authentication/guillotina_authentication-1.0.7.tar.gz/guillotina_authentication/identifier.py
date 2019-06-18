import logging
import math
import time

from guillotina_authentication.user import OAuthUser
from guillotina_authentication import utils
from guillotina_rediscache import cache

logger = logging.getLogger(__name__)

USER_CACHE_DURATION = 60 * 1
NON_IAT_VERIFY = {
    'verify_iat': False,
}


class OAuthClientIdentifier:

    def __init__(self, request):
        self.request = request

    def get_user_cache_key(self, login):
        return '{}-{}-{}'.format(
            getattr(self.request, '_container_id', 'root'),
            login,
            math.ceil(math.ceil(time.time()) / USER_CACHE_DURATION)
        )

    async def get_user(self, token):
        if token.get('type') not in ('bearer', 'wstoken', 'cookie'):
            return

        if '.' not in token.get('token', ''):
            # quick way to check if actually might be jwt
            return

        cache_key = self.get_user_cache_key(token['token'])
        store = cache.get_memory_cache()
        try:
            return store[cache_key]
        except KeyError:
            pass

        validated_jwt = token['decoded']
        if ('client' not in validated_jwt or
                'client_args' not in validated_jwt):
            return

        try:
            client = utils.get_client(
                validated_jwt['client'], **validated_jwt['client_args'])
            user, user_data = await client.user_info()
        except Exception:
            logger.warning(
                f'Error getting user data for {token}', exc_info=True)
            return

        user = OAuthUser(user_id=user.id, properties=user_data)
        container_id = getattr(self.request, '_container_id', None)

        user.apply_scope(validated_jwt, container_id)
        store[cache_key] = user
        return user
