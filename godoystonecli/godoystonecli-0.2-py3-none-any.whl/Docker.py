import subprocess


class Docker:
    def __init__(self):
        pass

    def create_container(self, name, image, command):
        docker_create = "docker run -tdi --name {0} {1} {2}".format(name, image, command)
        output = subprocess.Popen([docker_create], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = output.communicate()[0]
        return output

    def delete_container(self, name):
        pass

    def run_command(self, name, command):
        pass

    def list_containers(self):
        docker_list = "docker ps -a"
        output = subprocess.Popen([docker_list], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = output.communicate()[0]
        return output