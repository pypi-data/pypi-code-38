class VkError(Exception):
    def __init__(self, error_code, error_msg, request_params):
        self.error_code = error_code
        self.error_msg = error_msg
        self.request_params = request_params

    def __str__(self):
        return f'CODE: {self.error_code} MSG: {self.error_msg}'
