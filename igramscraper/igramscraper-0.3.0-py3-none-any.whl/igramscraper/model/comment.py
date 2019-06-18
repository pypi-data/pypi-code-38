from .initializer_model import InitializerModel
import textwrap


class Comment(InitializerModel):
    """
     * @param $value
     * @param $prop
     """

    def __init__(self, props=None):
        self.identifier = None
        self.text = None
        self.created_at = None
        # Account object
        self.owner = None

        super(Comment, self).__init__(props)

    def init_properties_custom(self, value, prop):
        if prop == 'id':
           self.identifier = value

        standart_properties = [
            'created_at',
            'text',
        ]

        if prop in standart_properties:
            self.__setattr__(prop, value)

        if prop == 'owner':
            from .account import Account
            self.owner = Account(value)
