from ciperror import BaseCipError


class ElementalServiceRequestError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="ELE001",
            message="Erro no request para o Elemental Service: {}".format(message),
            friendly_message="Erro no request para o Elemental Service.",
            http_status=500)


class CreateElementalJobRequestError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE002",
            message="Erro no post de criar job: {}".format(message),
            friendly_message="Erro ao criar um job no elemental.",
            http_status=500)

class ElementalTranscodingError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="ELE003",
            message="Erro no processo de transcoding do elemental: {}".format(message),
            friendly_message="Erro no processo de transcoding.",
            http_status=500)
