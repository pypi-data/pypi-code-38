
STATUS_OK = 'ok'
STATUS_ERROR = 'error'
STATUS_NO_ADMIN = 'noadmin'
STATUS_NO_PERMISSION = 'nopermission'
STATUS_NO_SUCH_TYPE = 'nosuchtype'
STATUS_USER_NOT_FOUND = 'usernotfound'
STATUS_WRONG_DATA = 'wrongdata'
STATUS_ROOM_HAS_ITEMS = 'roomhasitems'
STATUS_NO_SUCH_ACTION = 'nosuchaction'
STATUS_ALREADY_TRAINING = 'alreadytraining'

class Status():
    def __init__(self, type, message=None, data=None):
        self.type = type
        self.message = message
        self.data = data

    def get_dict(self) -> dict:
        """
        Converts the Status-object to a transportable dict
        :return: the dict
        """
        data = {}

        if self.type is not None:
            data['type'] = self.type
        else:
            data['type'] = STATUS_OK

        if self.message is not None:
            data['message'] = self.message

        data['data'] = self.data

        return data