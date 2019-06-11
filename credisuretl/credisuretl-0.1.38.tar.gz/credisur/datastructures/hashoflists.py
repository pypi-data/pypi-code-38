class HashOfLists:
    def __init__(self):
        self.hash = {}

    def append(self, key, item):
        if not key in self.hash:
            self.hash[key] = []

        self.hash[key].append(item)

    def items(self):
        for key, list in self.hash.items():
            yield key, list

    def __getitem__(self, key):
        return self.hash[key]

    def keys(self):
        return self.hash.keys()

    def __contains__(self, key):
        return key in self.hash
