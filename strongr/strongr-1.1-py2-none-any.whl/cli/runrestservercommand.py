from strongr.restdomain.model.gateways import Gateways
from .wrapper import Command

class RunRestServerCommand(Command):
    """
    Runs the strongr REST server that sits between FASTR and STRONGR

    restdomain:startserver
    """
    def handle(self):
        Gateways.flask_app().run()
