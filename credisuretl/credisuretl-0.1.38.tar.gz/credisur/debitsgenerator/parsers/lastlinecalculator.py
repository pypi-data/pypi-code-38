from functools import reduce


def calculate_last_line(header_data, debits_data):
    """

    :type header_data: credisur.debitsgenerator.parsers.parsedebitsheaders.Header
    """
    monetary_records = len(debits_data)
    total_amount = reduce(lambda x, y: x + y, map(lambda x: x.monto_numero, debits_data))
    process_date = header_data.fecha_proceso

    return LastLine(process_date, monetary_records, total_amount)

def format_amount(amount):
    return str(round(amount * 100)).zfill(10)


def format_total_number_of_records(number):
    return str(number).zfill(10)


def format_number_of_records(number):
    return str(number).zfill(7)


class LastLine:

    def __init__(self, fecha_proceso, registros_monetarios, suma_importes_registros):
        # formato de registros: 7 caracteres y relleno con ceros
        # formato de registros TOTALES: 10 caracteres y relleno con ceros
        # formato de montos: 10 caracteres, en centavos y relleno con ceros
        # formato fecha: ddmmaaaa
        # FILLER 1: del 34 al 103 (70 chars en blanco)
        # FILLER 2: del 114 al 250 (137 chars en blanco)

        self._tipo_de_novedad = "T"
        self._registros_monetarios = format_number_of_records(registros_monetarios)
        self._registros_no_monetarios = format_number_of_records(0)
        self._registros_totales = format_total_number_of_records(registros_monetarios)
        self._fecha_proceso = fecha_proceso
        self._suma_importes_registros = format_amount(suma_importes_registros)


    @property
    def tipo_de_novedad(self):
        return self._tipo_de_novedad

    @property
    def registros_totales(self):
        return self._registros_totales

    @property
    def registros_monetarios(self):
        return self._registros_monetarios

    @property
    def registros_no_monetarios(self):
        return self._registros_no_monetarios

    @property
    def fecha_proceso(self):
        return self._fecha_proceso

    @property
    def suma_importes_registros(self):
        return self._suma_importes_registros
