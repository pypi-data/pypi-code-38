from ciperror import BaseCipError


class UploadFileError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="FTP001",
            message="Erro ao realizar upload de um ou mais arquivos. na EF: {}".format(message),
            friendly_message="Erro ao realizar upload de um ou mais arquivos.",
            http_status=500)
