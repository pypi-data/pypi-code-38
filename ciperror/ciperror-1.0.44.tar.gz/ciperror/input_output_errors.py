from ciperror import BaseCipError


class InvalidInputError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code='IOE001',
            message='Entrada inválida: {}'.format(message),
            friendly_message='Os dados inseridos são inválidos para essa operação.',
            http_status=400)


class InvalidKpiError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE002',
            message='Id do kpi invalido: {}'.format(message),
            friendly_message='ID do sistema KPI dos Estúdios Globo inválido.',
            http_status=422)


class KpiExistError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE003',
            message='Ja existe um job com esse ID(kpi_metadata.id: {}'.format(message),
            friendly_message='Erro ao cadastrar um novo job de entrega.',
            http_status=422)


class InvalidProfileError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE004',
            message='Nome do profile invalido: {}'.format(message),
            friendly_message='Nome do profile inválido.',
            http_status=422)


class EfidExistError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE005',
            message='Ja existe um ef_id para esse job: {}'.format(message),
            friendly_message='Ja existe um ID da EF para esse job de entrega.',
            http_status=422)


class StatusError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE006',
            message='Status não pode ser menor que o atual: {}'.format(message),
            friendly_message='Erro na atualizacão do status.',
            http_status=422)


class StatusReadyForReviewError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE007',
            message='Sem profiles com o status = ready_for_review: {}'.format(message),
            friendly_message='Não existem profiles prontos para revisão.',
            http_status=422)


class StatusCancelledError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE008',
            message='este profile ja foi cancelado: {}'.format(message),
            friendly_message='Profile já cancelado.',
            http_status=422)


class DateTimeStartError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE009',
            message='O DateTime inicial ja foi cadastrado: {}'.format(message),
            friendly_message='Já existe data cadastrada.',
            http_status=422)


class DateTimeFinishError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE010',
            message='O DateTime final ja foi cadastrado: {}'.format(message),
            friendly_message='Já existe data cadastrada.',
            http_status=422)


class DateTimeSaveError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE011',
            message='data inicial < que data final: {}'.format(message),
            friendly_message='A data inicial precisa ser menor que a data final.',
            http_status=422)


class StatusUpdateError(BaseCipError):

    def __init__(self, message):
        super().__init__(
            code='IOE012',
            message='Erro ao atualizar o status: {}'.format(message),
            friendly_message='Status atual não pode ser atualizado.',
            http_status=422)

class EfRequiredError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="IOE013",
            message="'ef_id' é uma propriedade obrigatória: {}".format(message),
            friendly_message="O ID da EF é obrigatório.",
            http_status=422)

class EfIdIntError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="IOE014",
            message="ef id deve ser inteiro: {}".format(message),
            friendly_message="EF ID deve ser um número inteiro.",
            http_status=422)


class DateValidationError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="IOE015",
            message="Problema no preenchimento da Data: {}".format(message),
            friendly_message="Problema no preenchimento da data.",
            http_status=422)

class XmlPebbleParserError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="IOE016",
            message="Erro ao parsear o XML vindo da Pebble: {}".format(message),
            friendly_message="Problema ao ler o arquivo XML vindo da Pebble.",
            http_status=404)


