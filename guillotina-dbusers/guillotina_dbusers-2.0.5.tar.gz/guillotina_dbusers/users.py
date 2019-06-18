

class DBUserIdentifier(object):

    def __init__(self, request):
        self.request = request

    async def get_user(self, token):
        try:
            users = await self.request.container.async_get('users')
        except (AttributeError, KeyError):
            return

        user_ids = await users.async_keys()
        if token.get('id', '') in user_ids:
            user = await users.async_get(token.get('id', ''))
            if not user.disabled:
                return user
