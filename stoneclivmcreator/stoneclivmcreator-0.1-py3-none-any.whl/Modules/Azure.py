
from Modules.Cloud import Cloud

class Azure(Cloud):
    def __init__(self):
        self.url = "http://azure"
        self.token = "aldjkjfh"

    def create_vm(self):
        self.connect()
        print("Criando máquina na Azure")