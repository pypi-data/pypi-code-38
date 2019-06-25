from Modulos.Cloud import Cloud

class GCP(Cloud):

    def __init__(self):
        self.url = 'http://gcp'
        self.token = '12345'

    def criar_vm(self):
        self.connect()
        print("criando maquina gcp")