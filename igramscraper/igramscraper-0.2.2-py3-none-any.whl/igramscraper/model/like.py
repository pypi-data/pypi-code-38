class Like:

    def _initPropertiesCustom(self,value, prop):
        if prop == 'id':
            self.identifier = value
        if prop == 'username':
            self.username = value