from ciperror import BaseCipError


class JobDataServicelUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="JDS001",
            message="Erro inesperado no JobDataService: {}".format(message),
            friendly_message="Erro desconhecido no serviço de metadados de job.",
            http_status=500)


class JobDataServiceNotFoundError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="JDS002",
            message="Job ID não encontrado: {}".format(message),
            friendly_message="Job não encontrado.",
            http_status=404)


