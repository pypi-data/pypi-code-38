from ciperror import BaseCipError


class DatabaseServerConnectionError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE001',
            message='Sem conexao com o banco de dados: {}'.format(message),
            friendly_message="Sem conexão com o banco de dados.",
            http_status=504)


class DatabaseTimeoutError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE002',
            message='TimeOut, tempo de conexao maior que o permitido: {}'.format(message),
            friendly_message="Problemas na conexão com o banco de dados.",
            http_status=408)


class DatabaseMongoInvalidURIError(BaseCipError):

    def __init__(self):
        super().__init__(
            code='DBE003',
            message='URI inválida, a uri deve conter mongodb:// ou mongodb+srv://.',
            friendly_message="Sem conexão com o banco de dados.",
            http_status=400)


class DatabaseNetworkTimeoutError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE004',
            message='A conexão aberta excedeu o socketTimeout: {}'.format(message),
            friendly_message="Sem conexão com o banco de dados.",
            http_status=408)


class DatabaseWriteError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE005',
            message='Erro durante a escrita no banco de dados: {}'.format(message),
            friendly_message="Sem conexão com o banco de dados.",
            http_status=500)


class DatabaseAckError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE006',
            message='Erro ACK message: {}'.format(message),
            friendly_message="Sem conexão com o banco de dados.",
            http_status=500)


class DatabaseNoReponseError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE007',
            message='Sem resposta do banco de dados: {}'.format(message),
            friendly_message="Sem conexão com o banco de dados.",
            http_status=500)


class DatabaseDuplicateEntryError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='DBE008',
            message='Entrada duplicada não permitida: {}'.format(message),
            friendly_message="Não é possivel cadastrar duas entradas iguais no banco.",
            http_status=409)
