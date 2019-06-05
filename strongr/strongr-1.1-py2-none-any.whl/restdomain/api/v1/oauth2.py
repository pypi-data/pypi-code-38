from flask import url_for, request
from flask_restplus import Namespace, Resource

import strongr.restdomain.model.gateways
from strongr.restdomain.model.oauth2 import Client

ns = Namespace('oauth', description='Operations related to oauth2 login')

@ns.route('/revoke', methods=['POST'])
class Revoke(Resource):
    def post(self):
        auth_server = strongr.restdomain.model.gateways.Gateways.auth_server()
        return auth_server.create_revocation_response()

@ns.route('/token', methods=['POST'])
class Token(Resource):
    def post(self):
        auth_server = strongr.restdomain.model.gateways.Gateways.auth_server()
        return auth_server.create_token_response()

# @ns.route('/authorize')
# class Authorize(Resource):
#     def get(self):
#         auth_server = strongr.restdomain.model.gateways.Gateways.auth_server()
#         # Login is required since we need to know the current resource owner.
#         # It can be done with a redirection to the login page, or a login
#         # form on this authorization page.
#         if request.method == 'GET':
#             grant = auth_server.validate_authorization_request()
#             #return render_template(
#             #    'authorize.html',
#             #    grant=grant,
#             #    user=current_user,
#             #)
#         confirmed = request.form['confirm']
#         if confirmed:
#             # granted by resource owner
#             return auth_server.create_authorization_response()
#         # denied by resource owner
#         return auth_server.create_authorization_response(None)
#
#     def post(self):
#         auth_server = strongr.restdomain.model.gateways.Gateways.auth_server()
#         # Login is required since we need to know the current resource owner.
#         # It can be done with a redirection to the login page, or a login
#         # form on this authorization page.
#         #if request.method == 'GET':
#             #grant = auth_server.validate_authorization_request()
#             # return render_template(
#             #    'authorize.html',
#             #    grant=grant,
#             #    user=current_user,
#             # )
#         #confirmed = request.form['confirm']
#         #if confirmed:
#             # granted by resource owner
#         return auth_server.create_authorization_response('1')
#         # denied by resource owner
#         #return auth_server.create_authorization_response(None)
