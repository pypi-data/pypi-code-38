from ciperror import BaseCipError


class StorageUnreacheableCipError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code='GFS001',
            message='Storage indisponível: {}'.format(message),
            friendly_message='O storage utilizado pelo sistema está indisponível.',
            http_status=500)


class FileNotFoundCipError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code='GFS002',
            message='Arquivo não encontrado: {}'.format(message),
            friendly_message='Arquivo não encontrado.',
            http_status=404)


class PathNotFoundCipError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code='GFS003',
            message='Diretorio inválido ou inexistente: {}'.format(message),
            friendly_message='Diretório inválido ou inexistente.',
            http_status=404)


class PermissionDeniedCipError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code='GFS004',
            message='Permissão negada no storage: {}'.format(message),
            friendly_message='Usuário ou aplicação não tem permissão de acesso ao storage.',
            http_status=401)


class NotEnoughSpaceCipError(BaseCipError):
    def __init__(self, message):
        super().__init__(
            code='GFS005',
            message='O storage não possui espaço suficiente: {}'.format(message),
            friendly_message='O storage não possui espaço suficiente para a operação.',
            http_status=507)
