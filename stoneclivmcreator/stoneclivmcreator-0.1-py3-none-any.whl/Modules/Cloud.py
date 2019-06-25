
class Cloud(object):

    def __init__(self):

        self.url = ""
        self.token = ""

    def connect(self):
        print("The connection with cloud {0} was completed successfully".format(self.url))