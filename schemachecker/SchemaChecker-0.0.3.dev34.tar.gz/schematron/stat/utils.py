class Dict(dict):
    #TODO: implement working with list as attribute
    def __getattr__(self, item):
        value = self.get(item)
        if value:
            return value

    def __setattr__(self, key, value):
        self[key] = value
