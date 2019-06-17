class InternalSchemaError(Exception):
    pass


class ContextError(InternalSchemaError):
    def __init__(self, context, xml_file):
        self.message = f'Контекст {context} в файле {xml_file} не найден'


class NodeAttributeError(InternalSchemaError):
    def __init__(self, context, node, xml_file):
        self.message = f'Атрибут {context}/{node} в файле {xml_file} не найден'


class TokenizerError(InternalSchemaError):
    def __init__(self, expression, xml_file, ex):
        self.message = (f'Ошибка при лексическом анализе xpath выражения '
                        f'{expression} в файле {xml_file} ({ex}).')


class ParserError(InternalSchemaError):
    def __init__(self, expression, xml_file, ex):
        self.message = (f'Ошибка при интерпретации xpath выражения '
                        f'{expression} в файле {xml_file} ({ex}).')


class TypeConvError(InternalSchemaError):
    def __init__(self, args, ex):
        self.message = (f'Ошибка при приведении к вещественному типу '
                        f'аргументов {args}: {ex}')
