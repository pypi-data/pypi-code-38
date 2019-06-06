from ciperror import BaseCipError


class RedisConnectionError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="CONN001",
            message="Erro de conexão com o Redis: MESSAGE: {}".format(message),
            friendly_message="Erro de conexão com o Redis.",
            http_status=500)


class SMTPConnectionError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="CONN002",
            message="Erro de conexão com o servidor SMTP: MESSAGE: {}".format(message),
            friendly_message="Erro de conexão com o servidor SMTP.",
            http_status=500)


class FTPConnectionError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="CONN003",
            message="Erro de conexao com o servidor de FTP da PEBBLE: MESSAGE: {}".format(message),
            friendly_message="Erro de conexao com servidor FTP da PEBBLE.",
            http_status=500)
