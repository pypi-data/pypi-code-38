import strongr.core.gateways

from strongr.secretsdomain.model import Secret

import itertools

class GetSecretHandler():
    def __call__(self, query):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        result = session.query(Secret).filter(Secret.key == query.key).first()

        if result is not None:
            return result.value

        return None
