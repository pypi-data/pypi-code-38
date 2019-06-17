class InternalEdoError(Exception):
    pass


class XsdSchemeError(InternalEdoError):
    def __init__(self, ex):
        self.message = f'Ошибка при разборе .xsd файла шаблона: {ex}'
