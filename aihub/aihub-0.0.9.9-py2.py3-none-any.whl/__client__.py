from aihub.__file__          import File
from aihub.__algo__          import Algo
from aihub.__collection__    import Collection


class Client(object):

    environment = None
    user_client = None

    def __init__(self, environment, user_client):
        self.environment  = environment
        self.user_client  = user_client
    
    @property
    def file(self):
        return File(self)

    def algo(self, algo_url):
        return Algo(self, algo_url)

class MemberClient(Client):
    def __init__(self, environment):
        super(MemberClient, self).__init__(environment, True)

    def collection(self, collection_name):
        return Collection(self, collection_name)

class AlgorithmClient(Client):
    def __init__(self, environment):
        super(AlgorithmClient, self).__init__(environment, False)