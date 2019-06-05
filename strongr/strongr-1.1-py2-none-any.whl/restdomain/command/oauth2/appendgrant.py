class AppendGrant():
    def __init__(self, client_id, code, redirect_uri, scope, user_id, expires):
        self.client_id = client_id
        self.code = code
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.user_id = user_id
        self.expires = expires
