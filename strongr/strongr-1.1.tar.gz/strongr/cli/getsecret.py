from strongr.core.domain.secretdomain import SecretDomain
from .wrapper import Command


class GetSecret(Command):
    """
    Returns a jobs stdout

    secret:get
        {key : The key of the secret}
    """
    def handle(self):
        service = SecretDomain.secret_service()
        query_bus = service.get_query_bus()
        query_factory = SecretDomain.query_factory()

        result = query_bus.handle(query_factory.new_get_secret(self.argument('key')))

        print(result)
