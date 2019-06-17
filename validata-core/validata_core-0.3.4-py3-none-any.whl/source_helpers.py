from tabulator import helpers


def build_tabulator_params(type, name, source):
    """Return tabulator params auto-detected from `name` and `source`, handling `type=file` for Validata UI and API.

    Also decode `source`.
    """
    scheme, format = helpers.detect_scheme_and_format(name)

    # In case of uploaded file (we work with bytes string)
    if type == 'file':

        # CSV: converts to string
        if format == 'csv':
            scheme = 'text'
            encoding = helpers.detect_encoding(source)
            source = source.decode(encoding)

        # Else use custom BytesLoader
        else:
            scheme = 'bytes'

    return {'source': source, 'format': format, 'scheme': scheme}
