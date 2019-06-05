from strongr.secretsdomain.model import Secret
import strongr.core.gateways

import uuid

class AddSecretHandler():
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        secret = session.query(Secret).filter(Secret.key == command.key).first()

        if secret is None:
            secret = Secret()

        secret.key = command.key
        secret.value = command.value

        session.add(secret)
