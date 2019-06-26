class APIJSON:
    """Trait to indicate that the subclass supports the api_json method"""
    def api_json(self):
        raise NotImplementedError