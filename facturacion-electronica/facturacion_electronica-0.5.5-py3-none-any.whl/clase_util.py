# -#- coding: utf-8 -#-
import pytz
from datetime import datetime
import os
import re
from lxml import etree
import collections


class UserError(Exception):
    """Clase perdida"""
    pass


def set_from_keys(obj, vals={}):
    for k, v in vals.items():
        if hasattr(obj, k):
            setattr(obj, k, v)
        else:
            print("Atributo no encontrado en %s: %s" % (type(obj), k))


def create_xml(to_xml, root=None):
    if type(to_xml) is list:
        for r in to_xml:
            if type(r) in [list, dict, collections.OrderedDict]:
                create_xml(r, root)
            else:
                root.text = str(r)
    else:
        for k, v in to_xml.items():
            if root is not None:
                el = etree.SubElement(root, k)
            else:
                root = etree.Element(k)
                el = root
            if type(v) in [list, dict, collections.OrderedDict]:
                create_xml(v, el)
            else:
                el.text = str(v)
    return root


def xml_to_string(dict_xml):
    return etree.tostring(dict_xml).decode().replace('<item>', '')\
            .replace('</item>', '').replace('<item/>', '')\
            .replace('<itemDscRcgGlobal>', '')\
            .replace('</itemDscRcgGlobal>', '').replace('<itemUtilizados>', '')\
            .replace('</itemUtilizados>', '').replace('<itemAnulados>', '')\
            .replace('</itemAnulados>', '').replace('<itemOtrosImp>', '')\
            .replace('</itemOtrosImp>', '').replace('<cdg_items>', '')\
            .replace('</cdg_items>', '')

def get_fecha(val):
    _fecha = False

    def _get_fecha(fecha, formato="%d-%m-%Y"):
            date = fecha.replace('/', '-')
            try:
                _fecha = datetime.strptime(date, formato).strftime("%Y-%m-%d")
                return _fecha
            except:
                pass
    formatos = ["%d/%m/%Y", "%d-%m-%y", "%d-%m-%y", "%Y-%m-%d"]
    for f in formatos:
        _fecha = _get_fecha(val, f)
        if _fecha:
            break
    return _fecha


def verificar_rut(rut=False):
    #@TODO
    if not rut:
        return rut
    _rut_ = (re.sub('[^1234567890Kk]', '', str(rut))).zfill(9).upper()
    return True


def format_vat(value):
    #''' Se Elimina el 0 para prevenir problemas con el sii, ya que las muestras no las toma si va con
    #el 0 , y tambien internamente se generan problemas'''
    if not value or value == '' or value == 0:
        value ="66666666-6"
        #@TODO opción de crear código de cliente en vez de rut genérico
    rut = value
    #@TODO hacer validaciones de rut
    return rut


def _acortar_str(texto, size=1):
    c = 0
    cadena = ""
    while c < size and c < len(texto):
        cadena += texto[c]
        c += 1
    return cadena


def time_stamp(formato='%Y-%m-%dT%H:%M:%S'):
    tz = pytz.timezone('America/Santiago')
    return datetime.now(tz).strftime(formato)


def validar_xml(some_xml_string, validacion='doc'):
    if validacion == 'bol':
        return True
    validacion_type = {
        'aec': 'AEC_v10.xsd',
        'cesion': 'Cesion_v10.xsd',
        'consu': 'ConsumoFolio_v10.xsd',
        'doc': 'DTE_v10.xsd',
        'dte_cedido': 'DTECedido_v10.xsd',
        'env': 'EnvioDTE_v10.xsd',
        'env_boleta': 'EnvioBOLETA_v11.xsd',
        'env_recep': 'EnvioRecibos_v10.xsd',
        'env_resp': 'RespuestaEnvioDTE_v10.xsd',
        'libro': 'LibroCV_v10.xsd',
        'libro_s': 'LibroCVS_v10.xsd',
        'libro_boleta': 'LibroBOLETA_v10.xsd',
        'libro_guia': 'LibroGuia_v10.xsd',
        'recep': 'Recibos_v10.xsd',
        'sig': 'xmldsignature_v10.xsd',
    }
    xsdpath = os.path.dirname(os.path.realpath(__file__)) + '/xsd/'
    xsd_file = xsdpath + validacion_type[validacion]
    try:
        xmlschema_doc = etree.parse(xsd_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml_doc = etree.fromstring(some_xml_string)
        result = xmlschema.validate(xml_doc)
        if not result:
            xmlschema.assert_(xml_doc)
        return result
    except AssertionError as e:
        print(etree.tostring(xml_doc))
        raise UserError('XML Malformed Error:  %s' % e.args)
