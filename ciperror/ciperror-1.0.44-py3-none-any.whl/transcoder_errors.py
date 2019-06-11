from ciperror import BaseCipError


class TranscoderServiceRequestError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="TRE001",
            message="Erro no request para o Transcoder Service: {}".format(message),
            friendly_message="Erro no request para o Transcoder Service.",
            http_status=500)


class TranscoderJobNotFoundError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="TRE002",
            message="Job de transcoder não encontrado: {}".format(message),
            friendly_message="Job de transcoder não encontrado.",
            http_status=404)

class TranscoderFinishJobError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="TRE003",
            message="Erro durante a finalização do job de transcoder: {}".format(message),
            friendly_message="Erro durante a finalização do job de transcoder.",
            http_status=500)