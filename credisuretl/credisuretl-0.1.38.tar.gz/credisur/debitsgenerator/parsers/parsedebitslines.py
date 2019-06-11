

def parse_debits_lines(page_data):
    last_row = page_data.max_row + 1

    debit_lines = []

    for line_num in range(8, last_row):
        line_mapping = map_line(line_num, page_data)
        debit_lines.append(DebitLine(line_mapping))

    for line in debit_lines:
        # print(line.cbu_bloque_1, line.cbu_bloque_2, line.monto)
        pass

    return debit_lines


def map_line(row, page_data):
    raw_amount = page_data.cell(row=row, column=5).value
    amount = None

    if raw_amount:
        amount = format_amount(raw_amount)

    return {
        'sheet_name': page_data.title,
        'row': row,
        'tipo_novedad': page_data.cell(row=row, column=1).value,
        'cbu_bloque_1':  page_data.cell(row=row, column=2).value,
        'cbu_bloque_2': page_data.cell(row=row, column=3).value,
        'id_cliente': page_data.cell(row=row, column=4).value,
        'monto': amount,
        'monto_numero': raw_amount
    }


def format_amount(amount):
    return str(round(amount * 100)).zfill(10)


class DebitLine:

    def __init__(self, line_mapping):
        self._sheet_name = line_mapping['sheet_name']
        self._row = line_mapping['row']
        self._tipo_novedad = line_mapping['tipo_novedad']
        self._cbu_bloque_1 = line_mapping['cbu_bloque_1']
        self._cbu_bloque_2 = line_mapping['cbu_bloque_2']
        self._id_cliente = line_mapping['id_cliente']
        self._monto = line_mapping['monto']
        self._monto_numero = line_mapping['monto_numero']


    @property
    def sheet_name(self):
        return self._sheet_name


    @property
    def row(self):
        return self._row


    @property
    def tipo_novedad(self):
        return self._tipo_novedad


    @property
    def cbu_bloque_1(self):
        return self._cbu_bloque_1


    @property
    def cbu_bloque_2(self):
        return self._cbu_bloque_2


    @property
    def id_cliente(self):
        return self._id_cliente


    @property
    def monto(self):
        return self._monto


    @property
    def monto_numero(self):
        return self._monto_numero