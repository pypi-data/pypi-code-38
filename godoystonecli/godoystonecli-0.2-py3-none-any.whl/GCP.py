
from Modulos.Cloud import Cloud
from Modulos.Docker import Docker

class GCP(Cloud, Docker):
    def __init__(self):
        self.url = "http://gcp"
        self.token = "12345"

    def create_vm(self, vms):
        self.connect()
        print("criando máquina na gcp")
        for vm in vms:
            result = self.create_container("gcp_"+vm.get("name"), vm.get("os"), "/bin/bash")
            print(result) 

    def list_vms(self):
        containers = self.list_containers()
        containers = str(containers).split("\n")
        containers = [ c.replace("\\n", "").replace("\\", "").replace("\'", "") for c in containers ]
        containers = [ c.replace("\"", "\"").replace("'b", "") for c in containers ]
        #containers = json.loads(containers)

        print(containers)