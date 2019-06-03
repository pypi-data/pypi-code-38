from ciperror import BaseCipError


class GeneralUnexpectedError(BaseCipError):
    def __init__(self, service_name, message):
        super().__init__(
            code="GUE000",
            message="Erro inesperado no {0}: {1}".format(service_name, message),
            friendly_message="Erro inesperado no {}.".format(service_name),
            http_status=500)


class JobDataApiGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE001",
            message="Erro inesperado no JobDataAPI: {}".format(message),
            friendly_message="Erro desconhecido no Job Data API.",
            http_status=500)


class Ingest4KGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE002",
            message="Erro inesperado no Ingest 4K: {}".format(message),
            friendly_message="Erro desconhecido no Ingest 4K.",
            http_status=500)


class EFApiGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE003",
            message="Erro inesperado no EF API: {}".format(message),
            friendly_message="Erro desconhecido no serviço de integração com a EF.",
            http_status=500)


class OrquestratorGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE004",
            message="Erro inesperado no Orquestrator: {}".format(message),
            friendly_message="Erro desconhecido no orquestrador.",
            http_status=500)


class CheckFileGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE005",
            message="Erro inesperado no CheckFile: {}".format(message),
            friendly_message="Erro desconhecido no serviço de verificação de arquivos.",
            http_status=500)


class AppPCAGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE006",
            message="Erro inesperado no App PCA: {}".format(message),
            friendly_message="Erro desconhecido no serviço de integração com a EF.",
            http_status=500)


class MonitoringGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE007",
            message="Erro inesperado na Monitoracao: {}".format(message),
            friendly_message="Erro desconhecido no serviço de monitoração em tempo real.",
            http_status=500)


class BFFGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE008",
            message="Erro inesperado no BFF: {}".format(message),
            friendly_message="Erro desconhecido no serviço de integração"
                             " entre a página e os serviços de Media Delivery.",
            http_status=500)


class StatusServiceUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE009",
            message="Erro inesperado no Status service: {}".format(message),
            friendly_message="Erro desconhecido no serviço de Status",
            http_status=500)


class ReleaseNotesServiceGeneralUnexpectedError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GUE010",
            message="Erro inesperado no Release Notes Service: {}".format(message),
            friendly_message="Erro desconhecido no Release Notes Services.",
            http_status=500)
