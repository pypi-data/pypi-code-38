class Response():
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response

    def get_dict(self):
        return {'status_code': self.status_code, 'response': self.response}