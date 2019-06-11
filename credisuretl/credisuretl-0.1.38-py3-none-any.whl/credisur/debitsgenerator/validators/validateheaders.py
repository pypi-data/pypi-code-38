from .errorsiterator import ErrorsIterator

def validate_headers(header_data):
    errors = ErrorsIterator()
    sheet_name = header_data.sheet_name

    if header_data.cuit is None:
        errors.add_error("Falta el CUIT en solapa %s" % (sheet_name))

    if header_data.prestacion is None:
        errors.add_error("Falta la 'Prestación' en solapa %s" % (sheet_name))

    if header_data.prestacion is None:
        errors.add_error("Falta la 'Ref del débito' en solapa %s" % (sheet_name))

    if header_data.primer_vencimiento is None:
        errors.add_error("Falta la 'Fecha 1er vencimiento' en solapa %s" % (sheet_name))

    if header_data.fecha_proceso is None:
        errors.add_error("Falta la 'Fecha de proceso' en solapa %s" % (sheet_name))

    return errors
