# -*- coding: utf-8 -*-
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica.dte import DTE
from facturacion_electronica import clase_util as util
from lxml import etree
import base64
import collections


class UserError(Exception):
    """Clase perdida"""
    pass


class Respuesta(DTE):

    def __init__(self, vals):
        util.set_from_keys(self, vals)

    @property
    def Caratula(self):
        NroDetalles = len(self.xml_envio.findall('SetDTE/DTE'))
        caratula = collections.OrderedDict()
        caratula['RutResponde'] = self.RutResponde
        caratula['RutRecibe'] = self.RutRecibe
        caratula['IdRespuesta'] = self.IdRespuesta
        caratula['NroDetalles'] = NroDetalles
        caratula['NmbContacto'] = self.NmbContacto
        caratula['FonoContacto'] = self.FonoContacto
        caratula['MailContacto'] = self.MailContacto
        caratula['TmstFirmaResp'] = util.time_stamp()
        caratula_xml = util.create_xml({'Caratula': caratula})
        caratula_xml.set('version', '1.0')
        return etree.tostring(caratula_xml).decode('ISO-8859-1')

    @property
    def CodEnvio(self):
        if not hasattr(self, '_cod_envio'):
            return '1'
        return self._cod_envio

    @CodEnvio.setter
    def CodEnvio(self, val):
        self._cod_envio = val

    @property
    def IdRespuesta(self):
        if not hasattr(self, '_id_resp'):
            return 1
        return self._id_resp

    @IdRespuesta.setter
    def IdRespuesta(self, val):
        self._id_resp = val

    @property
    def DTEs(self):
        if not hasattr(self, '_dtes'):
            return False
        return self._dtes

    @DTEs.setter
    def DTEs(self, vals):
        _dtes = []
        if hasattr(self, '_dtes'):
            _dtes = self._dtes
        _dtes.append(Doc(vals))
        self._dtes = _dtes

    @property
    def FonoContacto(self):
        if not hasattr(self, '_fono_contacto'):
            return ''
        return self._fono_contacto

    @FonoContacto.setter
    def FonoContacto(self, val):
        self._fono_contacto = val

    @property
    def MailContacto(self):
        if not hasattr(self, '_mail_contacto'):
            return ''
        return self._mail_contacto

    @MailContacto.setter
    def MailContacto(self, val):
        self._mail_contacto = val

    @property
    def NmbContacto(self):
        if not hasattr(self, '_nmb_contacto'):
            return ''
        return self._nmb_contacto

    @NmbContacto.setter
    def NmbContacto(self, val):
        self._nmb_contacto = val

    @property
    def RecepcionEnvio(self):
        envio = self.xml_envio
        if envio.find('SetDTE/Caratula') is None:
            return True
        recep = self._receipt()
        resp_dtes = util.create_xml({"RecepcionEnvio": recep})
        return util.xml_to_string(resp_dtes)

    @property
    def Recinto(self):
        if not hasattr(self, '_recinto'):
            return ''
        return self._recinto

    @Recinto.setter
    def Recinto(self, val):
        self._recinto = val

    @property
    def RutRecibe(self):
        if not hasattr(self, '_rut_recibe'):
            return '66666666-6'
        return self._rut_recibe

    @RutRecibe.setter
    def RutRecibe(self, val):
        self._rut_recibe = val

    @property
    def RutResponde(self):
        if not hasattr(self, '_rut_responde'):
            return self.firma.rut_firmante
        return self._rut_responde

    @RutResponde.setter
    def RutResponde(self, val):
        self._rut_responde = val

    @property
    def EstadoRecepEnv(self):
        if not hasattr(self, '_estado_recep_env'):
            return -1
        return self._estado_recep_env

    @EstadoRecepEnv.setter
    def EstadoRecepEnv(self, vals):
        self._estado_recep_env = vals

    @property
    def RecepEnvGlosa(self):
        if not hasattr(self, '_recep_env_glosa'):
            return 'No Procesado'
        return self._recep_env_glosa

    @RecepEnvGlosa.setter
    def RecepEnvGlosa(self, vals):
        self._recep_env_glosa = vals

    @property
    def xml_envio(self):
        if not hasattr(self, '_xml_envio'):
            return False
        return self._xml_envio

    @xml_envio.setter
    def xml_envio(self, val):
        try:
            _xml = base64.b64decode(val)
        except:
            _xml = val
        xml = _xml.decode('ISO-8859-1')\
            .replace('<?xml version="1.0" encoding="ISO-8859-1"?>', '')\
            .replace('<?xml version="1.0" encoding="ISO-8859-1" ?>', '')\
            .replace(' xmlns="http://www.sii.cl/SiiDte"', '')\
            .replace(' xmlns="http://www.w3.org/2000/09/xmldsig#"', '')
        self._xml_envio = etree.XML(xml)

    @property
    def xml_nombre(self):
        if not hasattr(self, '_xml_nombre'):
            return False
        return self._xml_nombre

    @xml_nombre.setter
    def xml_nombre(self, val):
        self._xml_nombre = val

    def _check_digest_caratula(self):
        string = etree.tostring(self.xml_envio[0])
        #mess = etree.tostring(etree.fromstring(string), method="c14n")
        #our = base64.b64encode(self.firma.digest(mess))
        #if our != xml.find("Signature/SignedInfo/Reference/DigestValue").text:
        #    self.EstadoRecepEnv = 2
        #    self.RecepEnvGlosa = 'Envio Rechazado - Error de Firma'
        self.EstadoRecepEnv = 0
        self.RecepEnvGlosa = 'Envio Ok'

    def _check_digest_dte(self, dte):
        envio = self.xml_envio.find("SetDTE")
        for e in envio.findall("DTE"):
            string = etree.tostring(e.find("Documento"))
            #mess = etree.tostring(etree.fromstring(string), method="c14n")
            #our = base64.b64encode(self.firma.digest(mess))
            #if our != e.find("Signature/SignedInfo/Reference/DigestValue").text:
            #    self.EstadoRecepEnv = 1
            #    self.RecepEnvGlosa = 'DTE No Recibido - Error de Firma'
        self.EstadoRecepDTE = 0
        self.RecepDTEGlosa = 'DTE Recibido OK'

    def _validar_caratula(self, cara):
        if cara.find('RutReceptor').text != self.Emisor.RUTEmisor:
            self.EstadoRecepEnv = 3
            self.RecepEnvGlosa = 'Rut no corresponde a nuestra empresa'
        try:
            util.xml_validator(self._read_xml(False), 'env')
        except:
            self.EstadoRecepEnv = 1
            self.RecepEnvGlosa = 'Envio Rechazado - Error de Schema'
        self.EstadoRecepEnv = 0
        self.RecepEnvGlosa = 'Envío Ok'

    def _validar(self, doc):
        cara, glosa = self._validar_caratula(doc[0][0].find('Caratula'))
        return cara, glosa

    def _validar_dte(self, encabezado):
        res = collections.OrderedDict()
        res['TipoDTE'] = encabezado.find('IdDoc/TipoDTE').text
        res['Folio'] = encabezado.find('IdDoc/Folio').text
        res['FchEmis'] = encabezado.find('IdDoc/FchEmis').text
        res['RUTEmisor'] = encabezado.find('Emisor/RUTEmisor').text
        res['RUTRecep'] = encabezado.find('Receptor/RUTRecep').text
        res['MntTotal'] = encabezado.find('Totales/MntTotal').text
        self._check_digest_dte(encabezado)
        res['EstadoRecepDTE'] = self.EstadoRecepDTE
        res['RecepDTEGlosa'] = self.RecepDTEGlosa
        if encabezado.find('Receptor/RUTRecep').text != self.Emisor.RUTEmisor:
            res['EstadoRecepDTE'] = 3
            res['RecepDTEGlosa'] = 'Rut no corresponde a la empresa esperada'
        return res

    def _validar_dtes(self):
        envio = self.xml_envio
        res = []
        for doc in envio.findall('SetDTE/DTE'):
            res.append({
                'RecepcionDTE': self._validar_dte(
                                    doc.find('Documento/Encabezado'))
                })
        return res

    def _receipt(self):
        envio = self.xml_envio
        resp = collections.OrderedDict()
        resp['NmbEnvio'] = self.xml_nombre
        resp['FchRecep'] = util.time_stamp()
        resp['CodEnvio'] = util._acortar_str(self.CodEnvio, 10)
        resp['EnvioDTEID'] = envio.find('SetDTE').attrib['ID']
        resp['Digest'] = envio.find(
                            "Signature/SignedInfo/Reference/DigestValue").text
        self._validar_caratula(envio.find('SetDTE/Caratula'))
        if self.EstadoRecepEnv == 0:
            self._check_digest_caratula()
        resp['RutEmisor'] = envio.find('SetDTE/Caratula/RutEmisor').text
        resp['RutReceptor'] = envio.find('SetDTE/Caratula/RutReceptor').text
        resp['EstadoRecepEnv'] = self.EstadoRecepEnv
        resp['RecepEnvGlosa'] = self.RecepEnvGlosa
        NroDTE = len(envio.findall('SetDTE/DTE'))
        resp['NroDTE'] = NroDTE
        resp['item'] = self._validar_dtes()
        return resp

    def _validar_dte_en_envio(self, doc):
        res = collections.OrderedDict()
        res['TipoDTE'] = doc.find('IdDoc/TipoDTE').text
        res['Folio'] = doc.find('IdDoc/Folio').text
        res['FchEmis'] = doc.find('IdDoc/FchEmis').text
        res['RUTEmisor'] = doc.find('Emisor/RUTEmisor').text
        res['RUTRecep'] = doc.find('Receptor/RUTRecep').text
        res['MntTotal'] = doc.find('Totales/MntTotal').text
        res['CodEnvio'] = str(self.IdRespuesta) + str(self.Folio)
        res['EstadoDTE'] = self.EstadoDTE
        res['EstadoDTEGlosa'] = self.EstadoDTEGlosa
        return res

    def _resultado(self):
        return {
            'ResultadoDTE': self._datos_respuesta()
        }

    def _recep(self):
        receipt = collections.OrderedDict()
        receipt['TipoDoc'] = self.TipoDTE
        receipt['Folio'] = self.Folio
        receipt['FchEmis'] = self.FechaEmis
        receipt['RUTEmisor'] = self.RUTEmisor
        receipt['RUTRecep'] = self.Emisor.RUTEmisor
        receipt['MntTotal'] = int(round(self.monto_total))
        receipt['Recinto'] = self.Recinto
        receipt['RutFirma'] = self.firma.rut_firmante
        receipt['Declaracion'] = 'El acuse de recibo que se declara en\
 este acto, de acuerdo a lo dispuesto en la letra b) del Art. 4, y la letra c)\
  del Art. 5 de la Ley 19.983, acredita que la entrega de mercaderias\
   o servicio(s) prestado(s) ha(n) sido recibido(s).'
        receipt['TmstFirmaRecibo'] = util.time_stamp()
        return receipt

    def _caratula_recep(self):
        caratula = collections.OrderedDict()
        caratula['RutResponde'] = self.RutResponde
        caratula['RutRecibe'] = self.RutRecibe
        caratula['NmbContacto'] = self.NmbContacto
        caratula['FonoContacto'] = self.FonoContacto
        caratula['MailContacto'] = self.MailContacto
        caratula['TmstFirmaEnv'] = util.time_stamp()
        return caratula
