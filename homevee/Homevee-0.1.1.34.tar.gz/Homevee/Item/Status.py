
STATUS_OK = 'ok'
STATUS_ERROR = 'error'
STATUS_NO_ADMIN = 'noadmin'
STATUS_NO_PERMISSION = 'nopermission'
STATUS_NO_SUCH_TYPE = 'nosuchtype'
STATUS_USER_NOT_FOUND = 'usernotfound'
STATUS_WRONG_DATA = 'wrongdata'
STATUS_ROOM_HAS_ITEMS = 'roomhasitems'

class Status():
    def __init__(self, type, message=None):
        self.type = type
        self.message = message

    def get_dict(self) -> dict:
        """
        Converts the Status-object to a transportable dict
        :return: the dict
        """
        return {
            'status': self.type,
            'message': self.message
        }