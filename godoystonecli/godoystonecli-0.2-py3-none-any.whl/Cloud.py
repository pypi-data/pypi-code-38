
class Cloud(object):

    def __init__(self):

        self.url = ""
        self.token = ""

    def connect(self):
        print("Conexão com a cloud {0} feita com sucesso".format(self.url))