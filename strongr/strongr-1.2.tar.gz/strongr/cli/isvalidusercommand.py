from strongr.core.domain.authdomain import AuthDomain
from .wrapper import Command

import json

class IsValidUserCommand(Command):
    """
    Check if the login is a valid user

    authdomain:isvaliduser
        {username : The username to be checked}
        {password : The password to be checked}
    """
    def handle(self):
        authService = AuthDomain.authService()
        queryFactory = AuthDomain.queryFactory()

        query = queryFactory.newIsValidUserQuery(self.argument('username'), self.argument('password'))
        result = authService.getQueryBus().handle(query)
        print(json.dumps(result))
