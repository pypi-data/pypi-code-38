from flask import Flask
# flask is a peer dependency


class LambdaHelper:

    DEFAULT_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True
    }

    MIME_TYPE = 'application/json'

    def __init__(self, flask_app: Flask):
        self.flask_app = flask_app

    def build_flask_response(self, status_code: int, json_body: str):

        response = self.flask_app.response_class(
            response=json_body,
            status=status_code,
            mimetype=LambdaHelper.MIME_TYPE,
            headers=LambdaHelper.DEFAULT_HEADERS
        )

        return response





