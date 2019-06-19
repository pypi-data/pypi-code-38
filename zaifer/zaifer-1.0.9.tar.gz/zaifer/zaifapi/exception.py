

class InvalidAPIKeyException(Exception):
    '''
    API Keyが不正です。
    '''
    pass


class InvalidAPISecretException(Exception):
    '''
    API Secretが不正です。
    '''
    pass


class OrderNotFoundException(Exception):
    '''
    注文が存在しません。
    '''
    pass


class NonceNotIcreasedException(Exception):
    '''
    ナンスが増加されていません。
    '''
    pass


class NonceOutOfRangeException(Exception):
    '''
    ナンスが範囲外です。
    '''
    pass
