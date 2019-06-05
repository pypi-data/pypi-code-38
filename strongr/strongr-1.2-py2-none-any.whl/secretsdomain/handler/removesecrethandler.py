from strongr.secretsdomain.model import Secret
import strongr.core.gateways

class RemoveSecretHandler():
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        session.query(Secret).filter(Secret.key == command.key).delete()
