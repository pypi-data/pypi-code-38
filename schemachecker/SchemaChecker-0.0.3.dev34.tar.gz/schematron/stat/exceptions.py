class InternalStatError(Exception):
    pass


class TokenizerError(InternalStatError):
    def __init__(self, expression):
        self.message = (f'Ошибка при лексическом анализе выражения '
                        f'{expression}')


class InputError(InternalStatError):
    def __init__(self, xml_file, ex):
        self.message = f'Ошибка при обработке файла {xml_file} ({ex})'


class OkudError(InternalStatError):
    def __init__(self, xml_file):
        self.message = (f'Не найден обязательный атрибут "OKUD" '
                        f'в разделе metaForm в файле {xml_file}')


class InterpreterError(InternalStatError):
    def __init__(self, expression):
        self.message = (f'Ошибка при интерпретации выражения '
                        f'{expression}')
