
from Modulos.Cloud import Cloud

class Azure(Cloud):
    def __init__(self):
        self.url = "http://azure"
        self.token = "abcxyz"

    def criar_vm(self):
        self.connect()
        print("criando máquina na azure")