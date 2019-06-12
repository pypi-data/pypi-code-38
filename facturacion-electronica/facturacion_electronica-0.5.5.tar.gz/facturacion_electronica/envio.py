# -#- coding: utf-8 -#-
from facturacion_electronica.conexion import Conexion
from facturacion_electronica.consumo_folios import ConsumoFolios as CF
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica.dte import DTE as CDTE
from facturacion_electronica.emisor import Emisor as Emis
from facturacion_electronica.respuesta import Respuesta
from facturacion_electronica.firma import Firma
from facturacion_electronica.libro import Libro as Lib
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError
from lxml import etree


class Envio(object):

    def __init__(self, vals, resumen=False):
        self._iniciar()
        util.set_from_keys(self, vals)
        self.conexion = self.test
        self._resumen = resumen

    @property
    def conexion(self):
        if not hasattr(self, '_conexion'):
            return False
        return self._conexion

    @conexion.setter
    def conexion(self, val):
        if val:
            self._conexion = False
            return
        self._conexion = Conexion(self.Emisor, self.firma)

    @property
    def ConsumoFolios(self):
        if not hasattr(self, '_consumo_folios'):
            return []
        return self._consumo_folios

    @ConsumoFolios.setter
    def ConsumoFolios(self, vals):
        #CDTE.Emisor = self.Emisor
        _cfs = []
        for cf in vals:
            _cfs.append(CF(cf))
        self._consumo_folios = _cfs

    @property
    def Documento(self):
        if not hasattr(self, '_documentos'):
            return []
        return self._documentos

    @Documento.setter
    def Documento(self, docs):
        _documentos = []
        CDTE.Emisor = self.Emisor
        CDTE.firma = self.firma
        for vals in docs:
            if vals.get('TipoDTE'):
                TipoDTE = vals['TipoDTE']
            caf_file = vals.get('caf_file', [])
            for docData in vals["documentos"]:
                docu = Doc(
                            docData,
                            resumen=False
                        )
                docu.verify = self.verify
                docu.test = self.test
                if caf_file:
                    docu.caf_file = caf_file
                docu.TipoDTE = TipoDTE
                _documentos.append(docu)
        self._documentos = sorted(_documentos, key=lambda t: t.NroDTE)

    @property
    def DTE(self):
        CDTE(
                self.Emisor,
                self.firma,
            )
        return CDTE

    @property
    def Emisor(self):
        if not hasattr(self, '_emisor'):
            return False
        return self._emisor

    @Emisor.setter
    def Emisor(self, vals):
        if vals:
            self._emisor = Emis(vals)

    @property
    def errores(self):
        if not hasattr(self, '_errores'):
            return []
        return self._errores

    @errores.setter
    def errores(self, val):
        if not hasattr(self, '_errores'):
            self._errores = [val]
        else:
            self._errores.append(val)

    @property
    def filename(self):
        if not hasattr(self, '_filename'):
            return ''
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = val

    @property
    def firma(self):
        return self.firma_electronica

    @property
    def firma_electronica(self):
        if not hasattr(self, '_firma_electronica'):
            return False
        return self._firma_electronica

    @firma_electronica.setter
    def firma_electronica(self, vals):
        if vals:
            self._firma_electronica = Firma(vals)
        else:
            print("firma no soportada")
            self._firma_electronica = False

    @property
    def Libro(self):
        if not hasattr(self, '_libro'):
            return False
        return self._libro

    @Libro.setter
    def Libro(self, vals):
        if vals.get('TipoOperacion', 'VENTA') == 'VENTA':
            CDTE.Emisor = self.Emisor
        self._libro = Lib(vals)

    @property
    def Recepciones(self):
        if not hasattr(self, '_recepciones'):
            return []
        return self._recepciones

    @Recepciones.setter
    def Recepciones(self, vals):

        def recursive_xml(el):
            if el.text and bool(el.text.strip()):
                return el.text
            res = {}
            for e in el:
                res[el.tag] = recursive_xml(e)
            return res
        _recepciones = []
        for recep in vals:
            respuesta = Respuesta(recep)
            envio = respuesta.xml_envio
            respuesta.Emisor = {
                'RUTEmisor': envio.find('SetDTE/Caratula/RutEmisor').text,
            }
            for dte in envio.findall('SetDTE/DTE'):
                res = recursive_xml(dte)
                respuesta.DTEs = res
            _recepciones.append(respuesta)
        self._recepciones = _recepciones

    @property
    def RecepMer(self):
        if not hasattr(self, '_recep_mer'):
            return []
        return self._recep_mer

    @RecepMer.setter
    def RecepMer(self, vals):
        _recepciones = []
        Respuesta.firma = self.firma
        for recep in vals:
            respuesta = Respuesta(recep.get('Respuesta'))
            respuesta.DTEs = {'Encabezado': recep.get('Encabezado')}
            _recepciones.append(respuesta)
        self._recep_mer = _recepciones

    @property
    def RutReceptor(self):
        if not hasattr(self, '_rut_receptor'):
            return '60803000-K'
        return self._rut_receptor

    @RutReceptor.setter
    def RutReceptor(self, val):
        self._rut_receptor = val

    @property
    def ValidacionCom(self):
        if not hasattr(self, '_validacion_com'):
            return []
        return self._validacion_com

    @ValidacionCom.setter
    def ValidacionCom(self, vals):
        _recepciones = []
        Respuesta.firma = self.firma
        for recep in vals:
            respuesta = Respuesta(recep.get('Respuesta'))
            respuesta.DTEs = {'Encabezado': recep.get('Encabezado')}
            _recepciones.append(respuesta)
        self._validacion_com = _recepciones

    @property
    def test(self):
        if not hasattr(self, '_test'):
            return False
        return self._test

    @test.setter
    def test(self, val):
        self._test = val

    @property
    def verify(self):
        if not hasattr(self, '_verify'):
            return True
        return self._verify

    @verify.setter
    def verify(self, val):
        self._verify = val

    def _iniciar(self):
        self.es_boleta = False
        self._resumen = False

    def caratula_libro(self):
        if self.Libro.TipoOperacion == 'BOLETA' and\
                self.Libro.TipoLibro != 'ESPECIAL':
            raise UserError("Boletas debe ser solamente Tipo Operación ESPECIAL")
        if self.Libro.TipoLibro in ['ESPECIAL'] or\
                self.Libro.TipoOperacion in ['BOLETA']:
            FolioNotificacion = '<FolioNotificacion>{0}</FolioNotificacion>'\
                .format(self.Libro.FolioNotificacion)
        else:
            FolioNotificacion = ''
        if self.Libro.TipoOperacion in ['BOLETA']:
            TipoOperacion = ''
        else:
            TipoOperacion = '<TipoOperacion>' + self.Libro.TipoOperacion\
                + '</TipoOperacion>'
        CodigoRectificacion = ''
        if self.Libro.TipoLibro == 'RECTIFICA':
            CodigoRectificacion = '\n<CodAutRec>' +\
                self.Libro.CodigoRectificacion + '</CodAutRec>'
        xml = '''<EnvioLibro ID="{10}">
<Caratula>
<RutEmisorLibro>{0}</RutEmisorLibro>

<RutEnvia>{1}</RutEnvia>
<PeriodoTributario>{2}</PeriodoTributario>
<FchResol>{3}</FchResol>
<NroResol>{4}</NroResol>{5}
<TipoLibro>{6}</TipoLibro>
<TipoEnvio>{7}</TipoEnvio>
{8}{11}
</Caratula>
{9}
</EnvioLibro>
'''.format(self.Emisor.RUTEmisor,
           self.firma_electronica.rut_firmante\
            if self.firma_electronica else '66666666-6',
           self.Libro.PeriodoTributario,
           self.Emisor.FchResol,
           self.Emisor.NroResol,
           TipoOperacion,
           self.Libro.TipoLibro,
           self.Libro.TipoEnvio,
           FolioNotificacion,
           self.Libro.sii_xml_request,
           self.doc_id,
           CodigoRectificacion,
           )
        return xml

    def caratula_dte(self, EnvioDTE, SubTotDTE):
        xml = '''<SetDTE ID="SetDoc">
<Caratula version="1.0">
<RutEmisor>{0}</RutEmisor>
<RutEnvia>{1}</RutEnvia>
<RutReceptor>{2}</RutReceptor>
<FchResol>{3}</FchResol>
<NroResol>{4}</NroResol>
<TmstFirmaEnv>{5}</TmstFirmaEnv>
{6}</Caratula>{7}
</SetDTE>
'''.format(self.Emisor.RUTEmisor,
           self.firma_electronica.rut_firmante\
            if self.firma_electronica else '66666666-6',
           self.RutReceptor,
           self.Emisor.FchResol,
           self.Emisor.NroResol,
           util.time_stamp(),
           SubTotDTE,
           EnvioDTE)
        return xml

    def caratula_consumo_folios(self, cf, IdEnvio='SetDoc'):
        if cf.Correlativo != 0:
            Correlativo = "<Correlativo>"\
                + str(cf.Correlativo) + "</Correlativo>"
        else:
            Correlativo = ''
        xml = '''<DocumentoConsumoFolios ID="{10}">
<Caratula  version="1.0" >
<RutEmisor>{0}</RutEmisor>
<RutEnvia>{1}</RutEnvia>
<FchResol>{2}</FchResol>
<NroResol>{3}</NroResol>
    <FchInicio>{4}</FchInicio>
<FchFinal>{5}</FchFinal>{6}
<SecEnvio>{7}</SecEnvio>
<TmstFirmaEnv>{8}</TmstFirmaEnv>
</Caratula>
{9}
</DocumentoConsumoFolios>
'''.format(self.Emisor.RUTEmisor,
           self.firma_electronica.rut_firmante,
           self.Emisor.FchResol,
           self.Emisor.NroResol,
           cf.FchInicio,
           cf.FchFinal,
           Correlativo,
           str(cf.SecEnvio),
           util.time_stamp(),
           cf.sii_xml_request,
           IdEnvio)
        return xml

    def envio_dte(self, doc):
        xml = '''<EnvioDTE xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte EnvioDTE_v10.xsd" \
version="1.0">
{}
</EnvioDTE>'''.format(doc)
        return xml

    def envio_boleta(self, doc):
        xml = '''<EnvioBOLETA xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte EnvioBOLETA_v11.xsd" \
version="1.0">
{}
</EnvioBOLETA>'''.format(doc)
        return xml

    def envio_libro_cv(self, doc, simplificado=False):
        simp = 'http://www.sii.cl/SiiDte LibroCV_v10.xsd'
        if simplificado:
            simp = 'http://www.sii.cl/SiiDte LibroCVS_v10.xsd'
        xml = '''<LibroCompraVenta xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</LibroCompraVenta>'''.format(simp, doc)
        return xml

    def envio_libro_boleta(self, doc):
        xsd = 'http://www.sii.cl/SiiDte LibroBOLETA_v10.xsd'
        xml = '''<LibroBoleta xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</LibroBoleta>'''.format(xsd, doc)
        return xml

    def envio_consumo_folios(self, doc, simplificado=False):
        xsd = 'http://www.sii.cl/SiiDte ConsumoFolio_v10.xsd'
        xml = '''<ConsumoFolios xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</ConsumoFolios>'''.format(xsd, doc)
        self.sii_xml_request = xml

    def envio_libro_guia(self, doc, simplificado=False):
        xsd = 'http://www.sii.cl/SiiDte LibroGuia_v10.xsd'
        xml = '''<LibroGuia xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</LibroGuia>'''.format(xsd, doc)
        self.sii_xml_request = xml

    def _RecepcionEnvio(self, Caratula, resultado):
        resp = '''<RespuestaDTE version="1.0" xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte RespuestaEnvioDTE_v10.xsd" >
    <Resultado ID="Odoo_resp">
            {0}
            {1}
    </Resultado>
</RespuestaDTE>'''.format(Caratula, resultado)
        self.sii_xml_request = resp

    def envio_recep(self, caratula, recep):
        xml = '''<EnvioRecibos xmlns='http://www.sii.cl/SiiDte' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://www.sii.cl/SiiDte EnvioRecibos_v10.xsd' version="1.0">
    <SetRecibos ID="SetDteRecibidos">
        {0}
        {1}
    </SetRecibos>
</EnvioRecibos>'''.format(caratula, recep)
        self.sii_xml_request = xml

    def _ResultadoDTE(self, Caratula, resultado):
        resp = '''<RespuestaDTE version="1.0" xmlns="http://www.sii.cl/SiiDte" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sii.cl/SiiDte RespuestaEnvioDTE_v10.xsd" >
    <Resultado ID="Odoo_resp">
            {0}
            {1}
    </Resultado>
</RespuestaDTE>'''.format(Caratula, resultado)
        return resp

    def Recibo(self, id, receps):
        doc = '''<Recibo version="1.0" xmlns="http://www.sii.cl/SiiDte" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sii.cl/SiiDte Recibos_v10.xsd" >
    <DocumentoRecibo ID="{0}" >
        {1}
    </DocumentoRecibo>
</Recibo>
        '''.format(
            id,
            receps
        )
        return doc

    def firmar(self, uri, type='env'):
        result = b''
        if self.firma_electronica.firma:
            result = self.firma_electronica.firmar(self.sii_xml_request, uri, type)
        self.sii_xml_request = result

    def generate_xml_send(self):
        tots_dte = {}
        documentos = ''
        for dte in self.Documento:
            try:
                dte.timbrar()
                tots_dte.setdefault(dte.TipoDTE, 0)
                tots_dte[dte.TipoDTE] += 1
                documentos += '\n' + dte.sii_xml_request
            except Exception as e:
                err = {
                        'FechaEmis': dte.FechaEmis,
                        'Folio': dte.Folio,
                        'TipoDTE': dte.TipoDTE,
                        'error': str(e),
                    }
                print(err)
                self.errores = err
        SubTotDTE = ''
        for key, value in tots_dte.items():
            SubTotDTE += '<SubTotDTE>\n<TpoDTE>' + str(key)\
                + '</TpoDTE>\n<NroDTE>'+str(value)+'</NroDTE>\n</SubTotDTE>\n'
        self.filename += ".xml"
        # firma del sobre
        dtes = self.caratula_dte(documentos, SubTotDTE)
        env = 'env'
        if self.es_boleta:
            self.sii_xml_request = self.envio_boleta(dtes)
            env = 'env_boleta'
        else:
            self.sii_xml_request = self.envio_dte(dtes)
        self.firmar(
            'SetDoc',
            env)

    def do_dte_send(self):
        self.generate_xml_send()
        barcodes = []
        for r in self.Documento:
            barcodes.append({
                    'Folio': r.Folio,
                    'TpoDTE': r.TipoDTE,
                    'sii_barcode_img': r.sii_barcode_img
                })
        result = {
            'sii_result': 'draft',
            }
        if self.conexion:
            result = self.conexion.send_xml_file(
                            self.sii_xml_request,
                            self.filename
                        )
        result.update({
                'sii_xml_request': self.sii_xml_request,
                'sii_send_filename': self.filename,
                'barcodes': barcodes,
                'errores': self.errores,
                })
        return result

    def do_libro_send(self):
        if not self.Libro.validar():
            return []
        self.doc_id = self.Libro.TipoOperacion + '_' + \
            self.Libro.PeriodoTributario
        libro = self.caratula_libro()
        env = 'libro'
        if self.Libro.TipoOperacion in ['BOLETA']:
                xml = self.envio_libro_boleta(libro)
                env = 'libro_boleta'
        else:
            xml = self.envio_libro_cv(libro)
        root = etree.XML(xml)
        xml_pret = etree.tostring(
            root,
            pretty_print=True,
        ).decode('iso-8859-1')
        self.sii_xml_request = xml_pret
        self.firmar(
            self.doc_id,
            env)
        result = {'sii_result': 'draft'}
        self.sii_xml_request = self.sii_xml_request
        if not self.test:
            result = self.conexion.send_xml_file(
                            self.sii_xml_request,
                            self.doc_id + '.xml'
                        )
        result.update({
            'sii_xml_request': self.sii_xml_request,
            })
        return result

    def do_consumo_folios_send(self):
        results = []
        for _cf in self.ConsumoFolios:
            if not _cf.validar():
                continue
            self.filename = 'CF_' + _cf.FchInicio
            cf = self.caratula_consumo_folios(
                _cf
            )
            self.envio_consumo_folios(cf)
            self.firmar(
                'SetDoc',
                type='consu',
            )
            result = {'sii_result': 'draft'}
            sii_xml_request = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request
            if not self.test:
                result = self.conexion.send_xml_file(
                                sii_xml_request,
                                self.filename
                            )
            result.update({
                    'sii_xml_request': sii_xml_request,
                    'sii_send_filename': self.filename + ".xml",
                    })
            results.append(result)
        return results

    def do_receipt_deliver(self):
        resps = []
        CDTE.firma = self.firma_electronica
        for r in self.Recepciones:
            self._RecepcionEnvio(
                r.Caratula,
                r.RecepcionEnvio,
            )
            self.firmar(
                'Odoo_resp',
                'env_resp',
            )
            resp = {
                'sii_xml_response': self.sii_xml_request,
                'respuesta': 'recepcion_envio_' + (r.xml_nombre) + '_' \
                + str(r.IdRespuesta),
                'EstadoRecepEnv': r.EstadoRecepEnv,
                'RecepEnvGlosa': r.RecepEnvGlosa,
            }
            resps.append(resp)
        return resps

    def do_receipt(self):
        dict_recept = self._recep()
        id = "T" + str(self.TipoDTE) + "F" + str(self.Folio)
        receps = util.create_xml(dict_recept)
        doc = self._Recibo(id, receps)
        receipt = self.firmar(
            doc,
            'Recibo',
            'recep')
        envio = self._read_xml('etree')
        RutRecibe = envio['SetDTE']['Caratula']['RutEmisor']
        dict_caratula = self._caratula_recep(
            self.Emisor.RUTEmisor,
            RutRecibe,
        )
        caratula = util.create_xml(dict_caratula)
        envio_dte = self._envio_recep(caratula, receipt)
        envio_dte = self.firmar(
            envio_dte,
            'SetDteRecibidos',
            'env_recep'
        )
        return {
                'respuesta': envio_dte,
            }

    def do_validar_comercial(self):
        IdRespuesta = self.recepcion.id_respuesta
        dte = self._resultado(IdRespuesta)
        envio = self._read_xml('etree')
        NroDetalles = 1
        ResultadoDTE = util.create_xml(dte)
        RutRecibe = envio['SetDTE']['Caratula']['RutEmisor']
        caratula_validacion_comercial = self._caratula_respuesta(
            self.Emisor.RUTEmisor,
            RutRecibe,
            NroDetalles
        )
        caratula = util.create_xml(caratula_validacion_comercial)
        resp = self._ResultadoDTE(caratula, ResultadoDTE)
        respuesta = self.firmar(
            resp,
            'Odoo_resp',
            'env_resp'
        )
        return {
            'respuesta': respuesta,
        }

    def do_reject(self):
        IdRespuesta = 'ddd'
        dte = self._resultado(IdRespuesta)
        envio = self._read_xml('etree')
        NroDetalles = 1
        ResultadoDTE = util.create_xml(dte)
        RutRecibe = envio['SetDTE']['Caratula']['RutEmisor']
        caratula_validacion_comercial = self._caratula_respuesta(
            self._receptor.document_number,
            RutRecibe,
            IdRespuesta,
            NroDetalles)
        caratula = util.create_xml(caratula_validacion_comercial)
        resp = self._ResultadoDTE(caratula, ResultadoDTE)
        respuesta = self.firmar(
            resp,
            'Odoo_resp',
            'env_resp')
        return{
            'respuesta': respuesta
        }
