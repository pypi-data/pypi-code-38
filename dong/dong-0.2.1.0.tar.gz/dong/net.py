def authorization_headers(jwt_token):
    return {'Authorization': 'JWT {}'.format(jwt_token)}
