# -#- coding: utf-8 -#-
import collections
from datetime import datetime
from lxml import etree
import codecs
import logging
import ssl
from facturacion_electronica import clase_util as util

_logger = logging.getLogger(__name__)

try:
    from suds.client import Client
except ImportError:
    print('Cannot import SUDS')

try:
    import urllib3
    # urllib3.disable_warnings()
    pool = urllib3.PoolManager(timeout=30)
except:
    raise UserError('Error en cargar urllib3')

server_url = {
    'certificacion': 'https://maullin.sii.cl/DTEWS/',
    'produccion': 'https://palena.sii.cl/DTEWS/'
}

claim_url = {
    'certificacion': 'https://ws2.sii.cl/WSREGISTRORECLAMODTECERT/registroreclamodteservice',
    'produccion': 'https://ws1.sii.cl/WSREGISTRORECLAMODTE/registroreclamodteservice',
}

connection_status = {
    '0': 'Upload OK',
    '1': 'El Sender no tiene permiso para enviar',
    '2': 'Error en tamaño del archivo (muy grande o muy chico)',
    '3': 'Archivo cortado (tamaño <> al parámetro size)',
    '5': 'No está autenticado',
    '6': 'Empresa no autorizada a enviar archivos',
    '7': 'Esquema Invalido',
    '8': 'Firma del Documento',
    '9': 'Sistema Bloqueado',
    'Otro': 'Error Interno.',
}


class UserError(Exception):
    _logger.info(Exception)
    #código que detiene la ejecución
    pass


class Conexion(object):

    def __init__(self, emisor=None, firma_electronica=None):
        self.Emisor = emisor
        if not self.Emisor:
            return
        if not self.Emisor.Modo:
            raise UserError("Not Service provider selected!")
        self.firma = firma_electronica
        try:
            if not self.token:
                self.token = True
        except Exception as e:
            print('error conexión: %s' % str(e))
            return

    @property
    def Emisor(self):
        if not hasattr(self, '_emisor'):
            return False
        return self._emisor

    @Emisor.setter
    def Emisor(self, val):
        self._emisor = val

    @property
    def seed(self):
        if not hasattr(self, '_seed') or not self._seed:
            return False
        xml_seed = u'<getToken><Semilla>%s</Semilla></getToken>' \
            % (self._seed)
        signed_node = self.firma.firmar(xml_seed, type="token")
        msg = etree.tostring(
            signed_node, pretty_print=True).decode()
        return msg

    @seed.setter
    def seed(self, val):
        if not val:
            return
        # En caso de que haya un problema con la validación de certificado del
        # sii ( por una mala implementación de ellos)
        # esto omite la validacion
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        url = server_url[self.Emisor.Modo] + 'CrSeed.jws?WSDL'
        _server = Client(url)
        resp = _server.service.getSeed().replace(
                    '<?xml version="1.0" encoding="UTF-8"?>', '')
        root = etree.fromstring(resp)
        self._seed = root[0][0].text

    @property
    def token(self):
        if not hasattr(self, '_token'):
            return False
        return self._token

    @token.setter
    def token(self, val):
        if not val:
            return False
        self.seed = True
        url = server_url[self.Emisor.Modo] + 'GetTokenFromSeed.jws?WSDL'
        _server = Client(url)
        resp = _server.service.getToken(self.seed).replace(
                '<?xml version="1.0" encoding="UTF-8"?>', '')
        respuesta = etree.fromstring(resp)
        self._token = respuesta[0][0].text

    def ensure_str(self, x, encoding="utf-8", none_ok=False):
        if none_ok is True and x is None:
            return x
        if not isinstance(x, str):
            x = x.decode(encoding)
        return x

    def send_xml_file(self, envio_dte=None, file_name="envio"):
        if not self.token:
            raise UserError("No hay Token")
        url = 'https://palena.sii.cl'
        if self.Emisor.Modo == 'certificacion':
            url = 'https://maullin.sii.cl'
        post = '/cgi_dte/UPL/DTEUpload'
        headers = {
            'Accept': 'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, */*',
            'Accept-Language': 'es-cl',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/4.0 (compatible; PROG 1.0; Windows NT 5.0; YComp 5.0.2.4)',
            'Referer': '{}'.format(self.Emisor.Website),
            'Connection': 'Keep-Alive',
            'Cache-Control': 'no-cache',
            'Cookie': 'TOKEN={}'.format(self.token),
        }
        params = collections.OrderedDict()
        params['rutSender'] = self.firma.rut_firmante[:8]
        params['dvSender'] = self.firma.rut_firmante[-1]
        params['rutCompany'] = self.Emisor.RUTEmisor[:8]
        params['dvCompany'] = self.Emisor.RUTEmisor[-1]
        params['archivo'] = (
                    file_name,
                    '<?xml version="1.0" encoding="ISO-8859-1"?>\n%s'\
                    % envio_dte,
                    "text/xml")
        urllib3.filepost.writer = codecs.lookup('iso-8859-1')[3]
        multi = urllib3.filepost.encode_multipart_formdata(params)
        try:
            headers.update({'Content-Length': '{}'.format(len(multi[0]))})
            response = pool.request_encode_body(
                                        'POST',
                                        url+post,
                                        params,
                                        headers
                                    )
        except Exception as e:
            return {'status': 'NoEnviado', 'xml_resp': str(e)}
        retorno = {
                'sii_xml_response': response.data.decode(),
                'sii_result': 'NoEnviado',
                'sii_send_ident': '',
                }
        if response.status != 200:
            return retorno
        respuesta_dict = etree.fromstring(response.data)
        if respuesta_dict.find('STATUS').text != '0':
            _logger.info(connection_status[respuesta_dict.find('STATUS').text])
        else:
            retorno.update({
                'sii_result': 'Enviado',
                'sii_send_ident': respuesta_dict.find('TRACKID').text
                })
        return retorno

    def _get_send_status(self, track_id):
        url = server_url[self.Emisor.Modo] + 'QueryEstUp.jws?WSDL'
        _server = Client(url)
        rut = util.format_vat(self.Emisor.RUTEmisor)
        try:
            respuesta = _server.service.getEstUp(
                            rut[:8],
                            str(rut[-1]),
                            track_id,
                            self.token
                        )
        except Exception as e:
            return {
                    'status': 'NoEnviado',
                    'xml_resp': str(e),
                    }
        print(respuesta)
        self.sii_message = respuesta
        resp = etree.XML(respuesta.replace(
                '<?xml version="1.0" encoding="UTF-8"?>', '')\
            .replace('SII:', '')\
            .replace(' xmlns="http://www.sii.cl/XMLSchema"', ''))
        status = {'status': 'NoDefinido', 'xml_resp': respuesta}
        estado = resp.find('RESP_HDR/ESTADO')
        if estado is None:
            return status
        if estado.text == "-11":
            if resp.find('RESP_HDR/ERR_CODE').text == "2":
                status = {
                    'warning': {
                        'title': 'Estado -11 2',
                        'message': "Estado -11: Espere a que sea aceptado por\
 el SII, intente en 5s más",
                        },
                    }
            else:
                status = {
                    'warning': {
                        'title': 'Estado -11',
                        'message': "Estado -11: error !Algo a salido mal,\
 revisar carátula",
                        },
                    }
        if estado.text in ["EPR", "LOK"]:
            status['status'] = "Aceptado"
            if resp.find('RESP_BODY/RECHAZADOS').text == "1":
                status['status'] = "Rechazado"
        elif estado.text in ["RCT", "RCH", "LRH", "RFR", "LRH", "RSC"]:
            status['status'] = "Rechazado"
        if resp.find('RESP_HDR/GLOSA_ESTADO'):
            status['glosa_estado'] = resp.find('RESP_HDR/GLOSA_ESTADO').text
        if resp.find('RESP_HDR/GLOSA'):
            status['glosa'] = resp.find('RESP_HDR/GLOSA').text
        return status

    def _get_dte_status(self, doc):
        url = server_url[self.Emisor.Modo] + 'QueryEstDte.jws?WSDL'
        _server = Client(url)
        receptor = util.format_vat(doc.Receptor['RUTRecep'])
        date = datetime.strptime(doc.FechaEmis, "%Y-%m-%d").strftime("%d-%m-%Y")
        rut = self.firma.rut_firmante
        try:
            respuesta = _server.service.getEstDte(
                rut[:8],
                str(rut[-1]),
                self.Emisor.RUTEmisor[:8],
                str(self.Emisor.RUTEmisor[-1]),
                receptor[:8],
                str(receptor[-1]),
                str(doc.TipoDTE),
                str(doc.Folio),
                date,
                str(doc.MntTotal),
                self.token
            )
        except Exception as e:
            return {'status': 'NoEnviado', 'xml_resp': str(e)}
        status = {'status': 'NoDefinido', 'xml_resp': respuesta}
        resp = etree.XML(
            respuesta.replace('<?xml version="1.0" encoding="UTF-8"?>', '')\
            .replace('SII:', '')\
            .replace(' xmlns="http://www.sii.cl/XMLSchema"', '')
            )
        estado = resp.find('RESP_HDR/ESTADO')
        if estado is None:
            return status
        if estado.text in ['2', '4']:
            status = {
                'warning': {
                        'title': "Error code: %s" % estado.text,
                        'message': resp.find('RESP_HDR/GLOSA_ERR').text,
                        },
                }
            return status
        if estado.text == '3':
            status = {
                'warning': {
                        'title': "Error code: 3",
                        'message': resp.find('RESP_HDR/GLOSA').text,
                        },
                }
            return status
        if estado.text in ["EPR", "DOK", "DNK", "MMC"]:
            status['status'] = "Procesado"
            body = resp.find('RESP_BODY')
            if body:
                if body.find('RECHAZADOS').text == "1":
                    status['status'] = "Rechazado"
                if body.find('REPARO').text == "1":
                    status['status'] = "Reparo"
            status['glosa'] = resp.find('RESP_HDR/GLOSA_ESTADO').text
            if estado.text in ["DNK", "DOK"]:
                status['glosa_error'] = resp.find('RESP_HDR/GLOSA_ERR').text
        elif estado.text in ["RCT", "RCH", "FAU"]:
            status['glosa'] = resp.find('RESP_HDR/GLOSA_ESTADO').text
            status['status'] = "Rechazado"
        elif resp.find('RESP_HDR/ESTADO').text in ["FAN"]:
            status['glosa'] = resp.find('RESP_HDR/GLOSA_ESTADO').text
            status['status'] = "Anulado"
        return status

    def ask_for_dte_status(self, doc):
        if not doc.sii_send_ident:
            raise UserError('No se ha enviado aún el documento,\
 aún está en cola de envío interna en odoo')
        if doc.sii_result == 'Enviado':
            status = self._get_send_status(doc.sii_send_ident)
            if doc.sii_result != 'Proceso':
                return status
        return self._get_dte_status()

    def sign_claim(self, claim):
        doc = etree.fromstring(claim)
        signed_node = self.firma.firmar(doc)
        msg = etree.tostring(
            signed_node, pretty_print=True)
        return msg
        self.seed_file = msg

    def get_dte_claim(self, doc):
        url = claim_url['produccion']+'?wsdl'
        _server = Client(
                    url,
                    headers={
                        'Cookie': 'TOKEN='+self.token,
                        }
                    )
        respuesta = _server.service.listarEventosHistDoc(
            self.Emisor.RUTEmisor[:8],
            str(self.Emisor.RUTEmisor[-1]),
            str(doc.TipoDTE),
            str(doc.folio),)
        return respuesta
