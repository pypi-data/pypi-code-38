from .errorsiterator import ErrorsIterator

def validate_lines(debits_data):
    errors = ErrorsIterator()

    validate_func = validate_line_func(errors)

    for line in debits_data:
        validate_func(line)

    return errors

def validate_line_func(errors):

    fields = {
        'tipo_novedad': 'Tipo Novedad',
        'cbu_bloque_1': 'CBU Bloque 1',
        'cbu_bloque_2': 'CBU Bloque 2',
        'id_cliente': 'ID Cliente',
        'monto': 'Monto',
    }

    def validate_line(line):
        """

        :type line: credisur.debitsgenerator.parsers.parsedebitslines.DebitLine
        """

        row = line.row
        sheet_name = line.sheet_name

        def add_error(error):
            errors.add_error(error + " en fila %s de solapa %s" % (row, sheet_name))

        check_for_presence(line, fields, add_error)

    return validate_line


def check_for_presence(line, fields, err_func):
    for field, error_message in fields.items():
        if not getattr(line, field):
            err_func("Falta el tipo '%s'" % (error_message,))

