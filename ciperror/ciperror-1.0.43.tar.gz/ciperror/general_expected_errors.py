from ciperror import BaseCipError


class InvalidProfileError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GEE001",
            message="invalid profile name: {}".format(message),
            friendly_message="Profile name inválido.",
            http_status=422)


class ProfileCancelledError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GEE002",
            message="profile cancelado: {}".format(message),
            friendly_message="Houve uma tentativa de atualizar um profile que ja foi cancelado.",
            http_status=422)


class NoProfileReadyForReviewError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code="GEE003",
            message="Sem profiles com ready_for_review: {}".format(message),
            friendly_message="Não há profiles prontos para revisão.",
            http_status=409)


class JobIdAlreadyExistError(BaseCipError):
    def __init__(self, message, param):
        super().__init__(
            code="GEE004",
            message="já existe um job com o id: {0}: {1}".format(param,message),
            friendly_message="já existe um job com o id: {0}".format(param),
            http_status=400)


class GatewayRedirectTimeoutError(BaseCipError):
    def __init__(self, full_path):
        super().__init__(
            code="GEE005",
            message="Tempo de requisição para a url [{0}] esgotado.".format(full_path),
            friendly_message="Erro de comunicação interna.",
            http_status=504)


class JobNotFoundError(BaseCipError):
    def __init__(self, job_id):
        super().__init__(
            code="GEE006",
            message="Job: {} não encontrado.".format(job_id),
            friendly_message="Não foi possível localizar as informações detalhadas desta mídia.",
            http_status=404)

class Unauthorized(BaseCipError):
    def __init__(self, access_token):
        super().__init__(
            code="GEE007",
            message="Token de acesso inválida. Access-token: {}".format(access_token),
            friendly_message="Acesso não autorizado. Token inválida ou inexistente.",
            http_status=401)

class PermissionDenied(BaseCipError):
    def __init__(self, access_token):
        super().__init__(
            code="GEE008",
            message="Permissão negada",
            friendly_message="Permissão negada. Usuario sem permissões para acessar o recurso.",
            http_status=403)

# class InvalidKpiIdError(BaseCipError):
#     def __init__(self, message):
#         super().__init__(
#             code="GEE021",
#             message="ID do KPI inválido: {}".format(message),
#             friendly_message="Não foi encontrado um job com o id do KPI fornecido.",
#             http_status=422)


# class EfIdAlreadyExistError(BaseCipError):
#     def __init__(self, message):
#         super().__init__(
#             code="GEE022",
#             message="ef id ja esta preenchido: {}".format(message),
#             friendly_message="ef id já esta preenchido.",
#             http_status=422)


