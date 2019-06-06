from ciperror import BaseCipError


class LadderServiceRequestError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="LAD001",
            message="Erro no request para o Ladder Service: {}".format(message),
            friendly_message="Erro no request para o Ladder Service.",
            http_status=500)


class LadderServiceNotFoundError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="LAD002",
            message="Ladder não encontrada: {}".format(message),
            friendly_message="Ladder não encontrada.",
            http_status=404)