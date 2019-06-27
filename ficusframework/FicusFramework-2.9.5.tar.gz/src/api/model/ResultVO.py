SUCCESS_CODE = 2
DOING_CODE = 1
FAIL_CODE = -1


class ResultVO(object):
    code = 2
    msg = "success"
    content = None

    def __init__(self, code=2, msg="success", content=None):
        self.code = code
        self.content = content
        self.msg = msg

    def to_json(self):
        from flask import jsonify
        return jsonify({'code': self.code, 'msg': self.msg, 'content': self.content})

    def to_dict(self):
        return {'code': self.code, 'msg': self.msg, 'content': self.content}


SUCCESS = ResultVO(content="success")
DOING = ResultVO(code=DOING_CODE, msg="doing", content="doing")
FAIL = ResultVO(code=FAIL_CODE, msg="failed", content="failed")
