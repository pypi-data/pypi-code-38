import strongr.core.gateways

from strongr.secretsdomain.model import Secret

import itertools

class ListSecretsHandler():
    def __call__(self, query):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        result = session.query(Secret.key).order_by(Secret.key).all()

        return list(itertools.chain.from_iterable(result))
