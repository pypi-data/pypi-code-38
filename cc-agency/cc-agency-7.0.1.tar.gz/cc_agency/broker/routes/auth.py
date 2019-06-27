from flask import jsonify, request
from werkzeug.exceptions import Unauthorized


def auth_routes(app, auth, conf):
    tokens_valid_for_seconds = conf.d['broker']['auth']['tokens_valid_for_seconds']

    @app.route('/token', methods=['GET'])
    def get_token():
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        if not user['verified_by_credentials']:
            raise Unauthorized()

        token = auth.issue_token(user)
        return jsonify({
            'token': token,
            'validForSeconds': tokens_valid_for_seconds
        })
