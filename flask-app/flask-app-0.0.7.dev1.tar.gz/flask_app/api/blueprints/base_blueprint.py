from flask import request

class BaseBluePrint(object):
    def __init__(self,app=None):
        self.app = app

    def register(self):
        from api.blueprints.users import users_blueprint

        self.app.register_blueprint(users_blueprint)
