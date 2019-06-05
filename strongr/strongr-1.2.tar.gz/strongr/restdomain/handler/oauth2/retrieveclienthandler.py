class RetrieveClientHandler:
    def __call__(self, query):
        from pprint import pprint
        pprint(query.__dict__)
