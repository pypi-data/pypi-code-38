import os
import credisur.excelbuilder as excelbuilder
from credisur.exceladapter import ExcelWriter
import time

def parse_bank_files(cwd):
    print("parse_bank_files")
    results = list()

    if not os.path.isdir(cwd + '/outputs/'):
        missing_path = ("/".join(cwd.split("/")) + '/outputs/')
        print ("ERROR: El directorio %s no existe" % (missing_path,))
        return

    for filepath in files("inputs/"):
        results.extend(list(parse_file(filepath)))

    filepath = cwd + '/outputs/' + 'rendicion' + time.strftime("%Y%m%d-%H%M%S") + '.xlsx'
    writer = configure_writer(filepath)
    build_excel(writer, results, bank_columns_config())
    writer.save()


def files(path):
    for file in os.listdir(path):
        if not file.endswith("rendi"):
            continue

        filepath = os.path.join(path, file)

        if not os.path.isfile(filepath):
            continue

        yield filepath

def parse_file(filepath):
    with open(filepath, "r") as file:
        for line in file:
            parsed_line = parse_line(line)
            if not parsed_line:
                continue
            yield parsed_line

def parse_line(line):
    tipo_de_novedad = line[0:1]
    cuit_originante = line[1:11]
    sector = line[12:14]
    prestacion = line[15:24]
    fecha_vencimiento = line[25:33]
    cbu_bloque_1 = line[33:41]
    filler_cbu_2 = line[41:43]
    cbu_bloque_2 = line[44:58]
    id_cliente = line[58:79]
    vto_debito_original = line[80:87]
    ref_debito = line[88:102]
    importe = int(line[103:112].lstrip("0"))
    moneda_debito = line[113:114]
    fecha_segundo_vencimiento= line[115:122]
    importe_segundo_vencimiento = line[123:132]
    fecha_tercer_vencimiento = line[133:140]
    importe_tercer_vencimiento = line[141:150]
    identificador_pagador_nuevo = line[151:172]
    codigo_rechazos = line[173:176]

    if not tipo_de_novedad == "D":
        print(tipo_de_novedad)
        return

    return {
        'tipo_de_novedad': tipo_de_novedad,
        'cuit_originante': cuit_originante,
        'sector': sector,
        'prestacion': prestacion,
        'fecha_vencimiento': fecha_vencimiento,
        'cbu_bloque_1': cbu_bloque_1,
        'filler_cbu_2': filler_cbu_2,
        'cbu_bloque_2': cbu_bloque_2,
        'id_cliente': id_cliente,
        'vto_debito_original': vto_debito_original,
        'ref_debito': ref_debito,
        'importe': importe,
        'moneda_debito': moneda_debito,
        'fecha_segundo_vencimiento': fecha_segundo_vencimiento,
        'importe_segundo_vencimiento': importe_segundo_vencimiento,
        'fecha_tercer_vencimiento': fecha_tercer_vencimiento,
        'importe_tercer_vencimiento': importe_tercer_vencimiento,
        'identificador_pagador_nuevo': identificador_pagador_nuevo,
        'codigo_rechazos': codigo_rechazos
    }

def bank_columns_config():
    # D E F H I L S

    config_list = list()
    config_list.append(("A", "Prestación", 'prestacion'))
    config_list.append(("B", "Fecha Vencimiento", 'fecha_vencimiento'))
    config_list.append(("C", "CBU Bloque 1", 'cbu_bloque_1'))
    config_list.append(("D", "CBU Bloque 2", 'cbu_bloque_2'))
    config_list.append(("E", "ID Cliente", 'id_cliente'))
    config_list.append(("F", "Importe", 'importe'))
    config_list.append(("G", "Código Rechazos", 'codigo_rechazos'))

    return config_list

def configure_writer(filepath):
    return ExcelWriter(filepath)

def build_excel(excelwriter, transactions, columns_config):
    builder = excelbuilder.BasicBuilder(transactions, columns_config)
    excelwriter.build_sheet("Resultados Débito", builder.build_sheet_data())

def print_not_empty(label, str):
    if str.strip():
        print(label, str)