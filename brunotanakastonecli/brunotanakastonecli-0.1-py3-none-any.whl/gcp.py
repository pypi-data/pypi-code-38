from Modulos.cloud import cloud

class gcp(cloud):

    def __init__(self):
        self.url = "http://gcp"
        self.token = "12345"

    def criar_vm(self):
        self.connect()
        print("criando maquina no gcp")