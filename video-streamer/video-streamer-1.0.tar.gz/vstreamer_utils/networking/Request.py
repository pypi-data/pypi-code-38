

class Request:
    pass


class DirectoryInfoRequest(Request):
    def __init__(self, path):
        super().__init__()
        self.path = path


class AdditionalEntryPropertiesRequest(Request):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
