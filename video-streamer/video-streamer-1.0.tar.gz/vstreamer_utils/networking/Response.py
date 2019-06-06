

class Response:
    pass


class ErrorResponse(Response):
    def __init__(self, error_string):
        super().__init__()
        self.error_string = error_string


class DirectoryInfoResponse(Response):
    def __init__(self, directory_info):
        super().__init__()
        self.directory_info = directory_info


class AdditionalEntryPropertiesResponse(Response):
    def __init__(self, filepath, additional_properties):
        super().__init__()
        self.filepath = filepath
        self.additional_properties = additional_properties
