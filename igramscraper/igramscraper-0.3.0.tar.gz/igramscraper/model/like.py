class Like:

    def __init__(self, props=None):
        self.identifier = None
        self.username = None
        super(Like, self).__init__(props)

    def _initPropertiesCustom(self, value, prop):
        if prop == 'id':
            self.identifier = value
        if prop == 'username':
            self.username = value
