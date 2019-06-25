from Modulos.Cloud import Cloud

#Normalmente o nome do arquivo eh o mesmo nome da classe
class Azure(Cloud):

    def __init__(self):
        self.url = 'http://Azure'
        self.token = '12345'

    def criar_vm(self):
        self.connect()
        print("criando maquina azure")