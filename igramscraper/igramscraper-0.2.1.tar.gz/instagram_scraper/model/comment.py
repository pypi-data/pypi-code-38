from .initializer_model import InitializerModel
import textwrap

class Comment(InitializerModel):

    '''
     * @param $value
     * @param $prop
     '''
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
