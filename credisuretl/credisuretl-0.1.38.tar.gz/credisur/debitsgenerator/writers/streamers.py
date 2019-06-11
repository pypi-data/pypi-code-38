
def stream_lines(header_data, debits_data, stream):
    for line in parse_lines(header_data, debits_data):
        stream.write(line + "\n")


def parse_lines(header_data, debits_data):
    func_to_map = build_map_func(header_data)
    return map(func_to_map, debits_data)


def build_map_func(header_data):
    """

    :type header_data: credisur.debitsgenerator.parsers.parsedebitsheaders.Header
    """

    def build_string_for(line):
        """

        :type line: credisur.debitsgenerator.parsers.parsedebitslines.DebitLine
        """
        return "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % (
            line.tipo_novedad,                      #  1      1      1
            header_data.cuit,                       # 11      2     12
            " " * 3, # sector                       #  3     13     15
            header_data.prestacion.ljust(10),       # 10     16     25
            header_data.primer_vencimiento,         #  8     26     33
            line.cbu_bloque_1,                      #  8     34     41
            "0" * 3, # filler                       #  3     42     44
            line.cbu_bloque_2,                      # 14     45     58
            line.id_cliente[:22].ljust(22),         # 22     59     80
            header_data.primer_vencimiento,         #  8     81     88
            header_data.ref_debito.ljust(15),       # 15     89    103
            line.monto,                             # 10    104    113
            "80", # moneda 80 pesos 82 dólares      #  2    114    115
            " " * 8, # fecha segundo vencimiento    #  8    116    123
            "0" * 10, # monto segundo vencimiento   # 10    124    133
            " " * 8,  # fecha tercer vencimiento    #  8    134    141
            "0" * 10,  # monto tercer vencimiento   # 10    142    151
            " " * 22, # no corresponde              # 22    152    173
            " " * 3, # no corresponde               #  3    174    176
            "0" * 10, # no corresponde              # 10    177    186
            "0" * 10, # no corresponde              # 10    187    196
            " " * 54 # FILLER                       # 54    197    250
        )

    return build_string_for

def stream_last_line(last_line, stream):
    line = parse_last_line(last_line)

    if not line:
        return

    stream.write(line)


def parse_last_line(last_line):
    """

    :type last_line: credisur.debitsgenerator.parsers.lastlinecalculator.LastLine
    """

    return "%s%s%s%s%s%s%s%s" % (
        last_line.tipo_de_novedad,          #  1    1    1
        last_line.registros_totales,        # 10    2   11
        last_line.registros_monetarios,     #  7   12   18
        last_line.registros_no_monetarios,  #  7   19   25
        last_line.fecha_proceso,            #  8   26   33
        " " * 70,                           # 70   34  103
        last_line.suma_importes_registros,  # 70   34  103
        " " * 137                           #137  114  259
    )