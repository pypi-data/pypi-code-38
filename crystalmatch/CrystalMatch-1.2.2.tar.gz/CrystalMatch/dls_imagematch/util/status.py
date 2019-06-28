class StatusFlag:
    def __init__(self, code, status):
        self.code = code
        self.status = status

    def to_json_array(self):
        return {'code': self.code, 'msg': self.status}

    def to_json_array_with_names(self, code_str, msg_str):
        return {code_str: self.code, msg_str: self.status}

    def __str__(self):
        return str(self.code) + ", " + self.status
