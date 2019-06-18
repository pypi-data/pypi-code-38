from ciperror import BaseCipError


class FileCopyServiceRequestError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="FLC001",
            message="Erro no request para o File Copy Service: {}".format(
                message),
            friendly_message="Erro no request para o File Copy Service.",
            http_status=500)


class FileCopyBadChecksumError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="FLC002",
            message="Erro na verificação do checksum: {}".format(message),
            friendly_message="Erro de integridade de arquivo.",
            http_status=500
        )


class FileCopyBadFileError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="FLC003",
            message="Arquivo com falha de integridade: {}".format(message),
            friendly_message="Erro de integridade de arquivo.",
            http_status=500
        )
