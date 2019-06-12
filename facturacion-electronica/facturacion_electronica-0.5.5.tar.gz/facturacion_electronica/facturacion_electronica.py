# -*- coding: utf-8 -*-
from facturacion_electronica.libro_boletas import Boletas
from facturacion_electronica.conexion import Conexion
from facturacion_electronica.consumo_folios import ConsumoFolios
from facturacion_electronica.documento import Documento
from facturacion_electronica.dte import DTE
from facturacion_electronica.emisor import Emisor
from facturacion_electronica.envio import Envio
from facturacion_electronica.firma import Firma
from facturacion_electronica.libro import Libro
import json
import csv
import base64


def timbrar_json(json_str=None):
    try:
        data = json.loads(json_str)
        return timbrar(data)
    except:
        return


def procesar_documento(documentos, verify, test):
    _documentos = []
    for docs in documentos:
        TipoDTE = docs.get('TipoDTE', 33)
        caf_file = docs.get('caf_file', [])
        for docData in docs["documentos"]:
            docu = Documento(
                            docData,
                            resumen=False
                        )
            docu.verify = verify
            docu.test = test
            docu.caf_file = caf_file
            docu.TipoDTE = TipoDTE
            _documentos.append(docu)
    return _documentos


def timbrar(vals):
    firma = Firma(vals["firma_electronica"])
    emisor = Emisor(vals["Emisor"])
    verify = vals.get('verify', True)
    test = vals.get('test', False)
    _dtes = False
    if vals.get('Documento'):
        _dtes = procesar_documento(vals['Documento'], verify, test)
    respuesta = []
    if _dtes:
        dtes = sorted(_dtes, key=lambda t: int(t.NroDTE))
        DTE.Emisor = emisor
        DTE.firma = firma
        respuesta = []
        errores = []
        for dte in dtes:
            try:
                dte.timbrar()
                respuesta.append(
                        {
                            'TipoDte': dte.TipoDTE,
                            'Folio': dte.Folio,
                            'sii_xml_request': dte.sii_xml_request,
                            'sii_barcode_img': dte.sii_barcode_img,
                        })
            except Exception as e:
                    err = {
                            'FechaEmis': dte.FechaEmis,
                            'Folio': dte.Folio,
                            'TipoDTE': dte.TipoDTE,
                            'error': str(e),
                        }
                    errores.append(err)
    respuesta.append(errores)
    return respuesta


def xml_envio(vals):
    envio = Envio(vals)
    envio.test = True
    respuesta = envio.do_dte_send()
    return respuesta


def timbrar_y_enviar(vals):
    envio = Envio(vals)
    respuesta = envio.do_dte_send()
    return respuesta


def cf_json(json_str=None):
    try:
        data = json.loads(json_str)
        return consumo_folios(data)
    except:
        return


def consumo_folios(dicDocs):
    envio = Envio(dicDocs)
    return envio.do_consumo_folios_send()


def consumo_folios_resumen(data, folios=False):
    test = data['test'] if 'test' in data else False
    emisor = Emisor(data["Emisor"])
    firma = Firma(data["firma_electronica"])
    fechas = {}
    if folios:
        i = 0
        for row in folios:
            if i > 0:
                if row[0] not in fechas:
                    fechas[row[0]] = ConsumoFolios(emisor, firma)
                if 'Correlativo' in data:
                    fechas[row[0]].set_correlativo(data['Correlativo'])
                if 'SecEnvio' in data:
                    fechas[row[0]].set_sec_envio(data['SecEnvio'])
                docu = Documento({
                    'TasaImp': data["Emisor"]['ValorIva'],
                    'Fecha': row[0],
                    'Folio': int(row[2]),
                    'MntNeto': int(row[3]),
                    'MntIVA': int(row[4]),
                    'MntExento': int(row[5]),
                    'MntTotal': int(row[6]),
                    'Anulado': row[7],
                    }, int(row[1]), resumen=True)
                fechas[row[0]].set_docu(docu)
            else:
                cabezera = row
            i += 1
    elif 'Documentos' in data:
        for r in data['Documentos']:
            for d in r['documentos']:
                fecha = d['Encabezado']['IdDoc']['Fecha']
                if fecha not in fechas:
                    fechas[fecha] = ConsumoFolios(emisor, firma)
                if 'Correlativo' in data:
                    fechas[fecha].set_correlativo(data['Correlativo'])
                if 'SecEnvio' in data:
                    fechas[fecha].set_sec_envio(data['SecEnvio'])
                docu = Documento(d, r['TipoDTE'])
                fechas[fecha].set_docu(docu)
    else:
        cf = ConsumoFolios(emisor, firma)
        cf.FchInicio = data['FechaInicio']
        cf.FchFinal = data['FechaFinal']
        if 'Correlativo' in data:
            cf.set_correlativo(data['Correlativo'])
        if 'SecEnvio' in data:
            cf.set_sec_envio(data['SecEnvio'])
        envio = Envio(emisor, firma, test=test)
        envio.setLibro(cf)
        res = envio.do_consumo_folios_send()
        res.update({
                'correlativo': cf.Correlativo,
                'fecha_inicio': cf.FchInicio,
                'fecha_final': cf.FchFinal,
                'total_neto': cf.total_neto,
                'total_exento': cf.total_exento,
                'total_iva': cf.total_iva,
                'total': cf.total,
                'total_boletas': cf.total_boletas,

        })
        return [res]
    cfs = []
    respuestas = []
    envio = Envio(emisor, firma, test=test)
    for key, cf in fechas.items():
        cf.validar()
        cfs.append(cf.sii_xml_request)
        envio.setLibro(cf)
        res = envio.do_consumo_folios_send()
        res.update({
                'correlativo': cf.Correlativo,
                'fecha_inicio': cf.FchInicio,
                'fecha_final': cf.FchFinal,
                'total_neto': cf.total_neto,
                'total_exento': cf.total_exento,
                'total_iva': cf.total_iva,
                'total': cf.total,
                'total_boletas': cf.total_boletas,
                'rangos': cf.get_rangos(),

        })
        respuestas.append(res)
    return respuestas


def libro(dicDocs=None):
    envio = Envio(dicDocs)
    return envio.do_libro_send()


def libro_resumen(dicDocs, csv=False):
    firma = Firma(dicDocs["firma_electronica"])
    emisor = Emisor(dicDocs["Emisor"])
    libro = Libro(emisor, firma)
    libro.set_periodo_tributario(dicDocs["periodo_tributario"])
    libro.set_tipo_operacion(dicDocs["tipo_operacion"])
    libro.set_tipo_libro(dicDocs["tipo_libro"])
    test = dicDocs['test'] if 'test' in dicDocs else False
    envio = Envio(emisor, firma, test=test)
    respuesta = []
    if csv:
        libro = _libro_csv(libro, csv)
    else:
        for dteDoc in dicDocs["Documentos"]:
            for docData in dteDoc["documentos"]:
                docu = Documento(docData, dteDoc["TipoDTE"])
                libro.set_docu(docu)
    libro.validar()
    envio.setLibro(libro)
    respuesta = envio.do_libro_send()
    return respuesta


def _libro_csv(libro, csv=None):
    '''
    0 = Tipo Doc;                           11 = Cod IVA no Rec;                22 = Tabacos - Cigarrillos;
    1 = Folio;                              12 = Monto IVA no Rec;              23 = Tabacos - Elaborados;
    2 = Rut Contraparte;                    13 = IVA Uso Común;                 24 = Impuesto a Vehiculos Automóviles;
    3 = Tasa Impuesto;                      14 = Cod Otro Imp (Con Crédito);    25 = Codigo sucursal SII;
    4 = Razón Social Contraparte;           15 = Tasa Otro Imp (Con Crédito);   26 = Numero Interno;Emisor/Receptor;
    5 = Tipo Impuesto[1=IVA:2=LEY 18211];   16 = Monto Otro Imp (Con Crédito);  27 = Emisor Receptor;
    6 = Fecha Emisión;                      17 = Monto Otro Imp Sin Crédito;    28 = Monto Total;
    7 = Anulado[A];                         18 = Monto Activo Fijo;
    8 = Monto Exento;                       19 = Monto IVA Activo Fijo;
    9 = Monto Neto;                         20 = IVA No Retenido;
    10 = Monto IVA (Recuperable);           21 = Tabacos - Puros;
    '''
    i = 0
    for row in csv:
        if not row:
            continue
        if i > 0:
            if int(row[0]) not in [39, 41, 35]:
                docu = Documento({
                    'Folio': int(row[1]),
                    'Encabezado': {
                            'Receptor': {
                                'RUTRecep': row[2],
                                'RznSocRecep': row[4]
                            }
                    },
                    'TasaImp': int(row[3]),
                    'TpoImp': int(row[5]),
                    'Fecha': row[6],
                    'Anulado': row[7],
                    'MntExento': int(row[8]) if row[8] else False,
                    'MntNeto': int(row[9]) if row[9] else False,
                    'MntIVA': int(row[10]) if row[10] else False,
                    'CodIVANoRec': int(row[11]) if row[11] else False,
                    'IVANoRec':  int(row[12]) if row[12] else False,
                    'IVAUsoComun': int(row[13]) if row[13] else False,
                    'CodOtroImp': int(row[14]) if row[14] else False,
                    'TasaOtroImp': int(row[15]) if row[15] else False,
                    'MontoOtroImp': int(row[16]) if row[16] else False,
                    'MntTotal': int(row[17]) if row[17] else False,
                    'MontoOtroImpNoRec': int(row[18]) if row[18] else False,
                    'MontoActivoFijo': int(row[19]) if row[19] else False,
                    'MontoIVAActivoFijo': int(row[20]) if row[20] else False,
                    'IVANoRetenido': int(row[21]) if row[21] else False,
                    'TabacosPuros': int(row[22]) if row[22] else False,
                    'TabacosCigarrillos': int(row[23]) if row[23] else False,
                    'TabacosElaborados': int(row[24]) if row[24] else False,
                    'Vehiculos': int(row[25]) if row[25] else False,
                    'CodSucur': int(row[26]) if row[26] else False,
                    'NumeroInterno': int(row[27]) if row[27] else False,
                    'EmisorReceptor': int(row[28]) if row[28] else False,

                    }, int(row[0]), resumen=True)
            else:
                docu = Boletas({
                        'Folio': int(row[1]),
                        'TasaImp': int(row[3]),
                        'MntExento': int(row[8]) if row[8] else False,
                        'MntNeto': int(row[9]) if row[9] else False,
                        'MntIVA': int(row[10]) if row[10] else False,
                        'MntTotal': int(row[17]) if row[17] else False,
                    }, int(row[0]))
            libro.set_docu(docu)
        else:
            cabezera = row
        i += 1
    return libro


def consulta_estado_dte(vals):
    firma = Firma(vals["firma_electronica"])
    emisor = Emisor(vals["Emisor"])
    conex = Conexion(emisor, firma)
    return conex._get_send_status(vals["codigo_envio"])


def consulta_estado_documento(vals):
    firma = Firma(vals["firma_electronica"])
    emisor = Emisor(vals["Emisor"])
    respuesta = []
    for d in vals['Documento']:
        Documento.Emisor = emisor
        for r in d['documentos']:
            tipoDoc = int(d["TipoDTE"])
            documento = Documento(r, resumen=True)
            documento.TipoDTE = tipoDoc
            conexion = Conexion(emisor, firma)
            respuesta.append(conexion._get_dte_status(documento))
    return respuesta


def consulta_reclamo_documento(vals):
    firma = Firma(vals["firma_electronica"])
    emisor = Emisor(vals["Emisor"])
    respuesta = []
    for d in vals['Documento']:
        Documento.Emisor = emisor
        for r in d['documentos']:
            tipoDoc = int(d["TipoDTE"])
            documento = Documento(r, resumen=True)
            documento.TipoDTE = tipoDoc
            conexion = Conexion(emisor, firma)
            respuesta.append(conexion.get_dte_claim(documento))
    return respuesta


def leer_xml(vals):
    vals.update({'test': True})
    resp = Envio(vals)
    respuestas = resp.do_receipt_deliver()
    return respuestas


def recepcion_mercaderias(vals):
    vals.update({'test': True})
    resp = Envio(vals)
    respuesta = resp.get_dte_claim()
    return respuesta


def validacion_comercial(vals):
    vals.update({'test': True})
    resp = Envio(vals)
    respuesta = resp.get_dte_claim()
    return respuesta


def test(vals):
    if vals is None:
        return "r null"
    else:
        return "your firma is : " + vals["firma"]


def main():
    test({})


def ejemplo_libro():
    docEjemplo = json.load(open("ejemplos/ejemplo_libro_ventas.json"))
    libro(docEjemplo)


def ejemplo_cf():
    docEjemplo = json.load(open("ejemplos/ejemplo_consumo_folios.json"))
    consumo_folios(docEjemplo)


def ejemplo_cf_csv():
    data = json.load(open("ejemplos/ejemplo_consumo_folios_csv.json"))
    folios = csv.reader(base64.b64decode(data['consumo_folios']).splitlines(), csv.excel, delimiter=',', quotechar='|')
    i = 0
    listado = ['Fecha', 'Folio', 'RUTRecep', 'MntNeto', 'MntIVA', 'MntExento', 'MntTotal']
    firma = Firma(data["firma_electronica"])
    emisor = Emisor(data["Emisor"])
    fechas = {}
    for row in folios:
        if i >0:
            if row[0] not in fechas:
                fechas[row[0]] = ConsumoFolios(emisor, firma)
            else:
                docu = Documento({
                    'Fecha': row[0],
                    'Folio': int(row[2]),
                    'MntNeto': float(row[3]),
                    'MntIVA': float(row[4]),
                    'MntExento': float(row[5]),
                    'MntTotal': float(row[6]),
                    'Anulado': row[7],
                    }, int(row[1]), resumen=True)
                fechas[row[0]].set_docu(docu)

        else:
            cabezera = row
        i += 1
    for key, cf in fechas.items():
        cf.validar()
        print (cf.sii_xml_request)


if __name__ == "__main__":
    main()
