from datetime import datetime
class Name_files(object):
    def __init__(self):
        self.name_base = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_name_file(self,body,ext):
        name = self.name_base + "-" + body + "." +ext
        return name
        