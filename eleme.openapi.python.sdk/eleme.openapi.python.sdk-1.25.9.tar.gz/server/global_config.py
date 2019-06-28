class Global:

    sand_box = True

    app_key = None
    # your secret
    secret = None

    callback_url = None

    server_url = None

    log = None

    def __init__(self, config):
        Global.sand_box = config.get_env()
        Global.app_key = config.get_app_key()
        Global.secret = config.get_secret()
        Global.callback_url = config.get_callback_url()
        Global.log = config.get_log()

    @staticmethod
    def get_env():
        return Global.sand_box

    @staticmethod
    def get_app_key():
        return Global.app_key

    @staticmethod
    def get_secret():
        return Global.secret

    @staticmethod
    def get_callback_url():
        return Global.callback_url

    @staticmethod
    def get_log():
        return Global.log

    @staticmethod
    def get_server_url():
        return Global.server_url

    @staticmethod
    def get_access_token_url():
        return Global.get_server_url() + "/token"

    @staticmethod
    def get_api_server_url():
        return Global.get_server_url() + "/api/v1/"

    @staticmethod
    def get_authorize_url():
        return Global.get_server_url() + "/authorize"