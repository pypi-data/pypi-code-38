from ciperror import BaseCipError


class EFGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE001",
            message="Erro inexperado: {}".format(message),
            friendly_message="Erro na integração com a EF.",
            http_status=500)


class PublishRequestError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE002",
            message="Erro no post de publish request: {}".format(message),
            friendly_message="Erro ao criar um rascunho na EF.",
            http_status=500)


class DraftNotFoundError(BaseCipError):
    def __init__(self, message, uuid):
        super().__init__(
            code="EFE003",
            message="UUID {} não encontrado: {}".format(uuid, message),
            friendly_message="Não existe rascunho na EF para o código informado.",
            http_status=404)


class ProgramNotFoundError(BaseCipError):
    def __init__(self, message, program_id):
        super().__init__(
            code="EFE004",
            message="program_id {} não encontrado: {}".format(program_id, message),
            friendly_message="Não existe programa na EF para o código informado.",
            http_status=404)


class MediaNotFoundError(BaseCipError):
    def __init__(self, message, ef_id):
        super().__init__(
            code="EFE005",
            message="ef_id {} não encontrado: {}".format(ef_id, message),
            friendly_message="Não existe mídia na EF para o código informado.",
            http_status=404)


class ProfileError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE006",
            message="Erro/rejeição de profile: {}".format(message),
            friendly_message="Ocorreu um erro ao criar um profile de vídeo na EF.",
            http_status=500)


class CreateMediaError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE007",
            message="Erro de publish/create na EF: {}".format(message),
            friendly_message="Erro de publicação na EF.",
            http_status=500)


class ReplaceMediaError(BaseCipError):
    def __init__(self, message, ef_if):
        super().__init__(
            code="EFE008",
            message="Erro no replace da mídia: {} na EF: {}".format(ef_if, message),
            friendly_message="Erro ao regerar mídia na EF.",
            http_status=500)


class EFResponseOfflineError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE009",
            message="Sem resposta da API da EF: {}".format(message),
            friendly_message="Sem resposta da API da EF.",
            http_status=500)


class EFUnprocessableEntityError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="EFE010",
            message="Erro no envio dos profiles a EF: {}".format(message),
            friendly_message="Erro no envio dos profiles a EF.",
            http_status=422)
