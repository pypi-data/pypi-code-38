from ciperror import BaseCipError


class CallBackNotificationError(BaseCipError):
    def __init__(self, service, message):
        super().__init__(
            code="CBE001",
            message="Erro ao realizar callback da requisição para o serviço: {} - message: {}".format(service, message),
            friendly_message="Erro ao notificar serviço {}".format(service),
            http_status=500)


class NotificationError(BaseCipError):
    def __init__(self, service, message):
        super().__init__(
            code="CBE002",
            message="Erro ao enviar notificação para o serviço: {} - message: {}".format(service, message),
            friendly_message="Erro ao enviar notificação para o serviço {}".format(service),
            http_status=500)
