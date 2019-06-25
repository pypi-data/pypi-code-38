
from Modules.Cloud import Cloud

class GCP(Cloud): #Inheritance is made with Class(AnotherClass)
    def __init__(self):
        self.url = "http://gcp"
        self.token = "12345"

    def create_vm(self):
        self.connect()
        print("Criando máquina na GCP")