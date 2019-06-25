class Cloud(object):
    def __init__(self):
        self.url = ""
        self.token = ""
    
    def connect(self):
        print(f"Conexao com a cloud {self.url} feita com sucesso")