from Modulos.cloud import cloud

class azure(cloud):

    def __init__(self):
        self.url = "http://azure"
        self.token = "abcde"

    def criar_vm(self):
        self.connect()
        print("criando maquina na azure")
