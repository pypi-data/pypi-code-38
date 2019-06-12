# -*- coding: utf-8 -*-
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica import clase_util as util
from datetime import datetime
import collections
import logging

_logger = logging.getLogger(__name__)


class ConsumoFolios(object):

    def __init__(self, vals):
        self._iniciar()
        util.set_from_keys(self, vals)

    def _iniciar(self):
        self.sii_message = None
        self.sii_xml_request = '<Resumen><TipoDocumento>39</TipoDocumento>\
<MntTotal>0</MntTotal><FoliosEmitidos>0</FoliosEmitidos><FoliosAnulados>0\
</FoliosAnulados><FoliosUtilizados>0</FoliosUtilizados></Resumen>'
        self.sii_xml_response = None
        self.total_boletas = 0
        self.total_neto = 0
        self.total_exento = 0
        self.total_iva = 0
        self.total = 0

    @property
    def Correlativo(self):
        if not hasattr(self, '_correlativo'):
            return 0
        return self._correlativo

    @Correlativo.setter
    def Correlativo(self, correlativo=0):
        self.Correlativo = correlativo

    @property
    def Documento(self):
        if not hasattr(self, '_documentos'):
            return []
        return self._documentos

    @Documento.setter
    def Documento(self, vals):
        documentos = []
        for dteDoc in vals:
            for docData in dteDoc.get("documentos", []):
                if not docData.get('sii_xml_request'):
                    docu = Doc(
                                docData,
                                resumen=True
                            )
                    docu.TipoDTE = dteDoc["TipoDTE"]
                    documentos.append(docu)
        self._documentos = sorted(documentos, key=lambda t: t.Folio)

    @property
    def Fecha(self):
        if not hasattr(self, '_fecha'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fecha

    @Fecha.setter
    def Fecha(self, val):
        self._fecha = val

    @property
    def FchFinal(self):
        if not hasattr(self, '_fch_final'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fch_final

    @FchFinal.setter
    def FchFinal(self, val):
        self._fch_final = val

    @property
    def FchInicio(self):
        if not hasattr(self, '_fch_inicio'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fch_inicio

    @FchInicio.setter
    def FchInicio(self, val):
        self._fch_inicio = val

    @property
    def SecEnvio(self):
        if not hasattr(self, '_sec_envio'):
            return 0
        return self._sec_envio

    @SecEnvio.setter
    def SecEnvio(self, sec_envio=0):
        self.SecEnvio = sec_envio

    def getResumen(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        det['NroDoc'] = rec.Folio
        Neto = rec.MntNeto
        MntExe = rec.MntExe
        TaxMnt = rec.MntIVA
        monto_total = rec.MntTotal
        tasa = None
        TasaIVA = '19'
        if Neto == 0 and not rec.Anulado:
            for t in rec.Impuesto:
                if t.tax_id.monto > 0:
                    tasa = t.tax_id
                    TaxMnt += t.monto
                    Neto += t.base
                elif t.tax_id.monto == 0:
                    MntExe += t.base
        if tasa:
            TasaIVA = tasa.monto
        if MntExe > 0:
            det['MntExe'] = int(round(MntExe, 0))
        if TaxMnt > 0:
            det['MntIVA'] = int(round(TaxMnt))
            det['TasaIVA'] = TasaIVA
        if monto_total == 0:
            monto_total = int(round((Neto + MntExe + TaxMnt), 0))
        det['MntNeto'] = int(round(Neto))
        det['MntTotal'] = monto_total
        if rec.Anulado:
            det['Anulado'] = 'A'
        return det

    '''Se asumen que vienen ordenados de menor a mayor'''
    def _last(self, folio, items):
        last = False
        for c in items:
            if folio > c['Final'] and folio > c['Inicial']:
                if not last or last['Inicial'] < c['Inicial']:
                    last = c
        return last

    def _nuevo_rango(self, folio, f_contrario, contrarios):
        '''obtengo el último tramo de los contrarios'''
        last = self._last(folio, contrarios)
        if last and last['Inicial'] > f_contrario:
            return True
        return False

    def _orden(self, folio, rangos, contrarios, continuado=True):
        last = self._last(folio, rangos)
        if not continuado or not last or self._nuevo_rango(
                    folio, last['Final'], contrarios):
            r = collections.OrderedDict()
            r['Inicial'] = folio
            r['Final'] = folio
            rangos.append(r)
            return rangos
        result = []
        for r in rangos:
            if r['Final'] == last['Final'] and folio > last['Final']:
                r['Final'] = folio
            result.append(r)
        return result

    def _rangosU(self, resumen, rangos, continuado=True):
        if not rangos:
            rangos = collections.OrderedDict()
        folio = resumen['NroDoc']
        if 'Anulado' in resumen and resumen['Anulado'] == 'A':
            utilizados = rangos.get('itemUtilizados', [])
            if not rangos.get('itemAnulados'):
                rangos['itemAnulados'] = []
                r = collections.OrderedDict()
                r['Inicial'] = folio
                r['Final'] = folio
                rangos['itemAnulados'].append(r)
            else:
                rangos['itemAnulados'] = self._orden(
                                    resumen['NroDoc'], rangos['itemAnulados'],
                                    utilizados, continuado
                                )
            return rangos
        anulados = rangos['itemAnulados'] if 'itemAnulados' in rangos else []
        if not rangos.get('itemUtilizados'):
            rangos['itemUtilizados'] = []
            r = collections.OrderedDict()
            r['Inicial'] = folio
            r['Final'] = folio
            rangos['itemUtilizados'].append(r)
        else:
            rangos['itemUtilizados'] = self._orden(
                            resumen['NroDoc'], rangos['itemUtilizados'],
                            anulados, continuado
                        )
        return rangos

    def _setResumen(self, resumen, resumenP, continuado=True):
        resumenP['TipoDocumento'] = resumen['TpoDoc']
        if 'Anulado' not in resumen:
            if 'MntNeto' in resumen and not 'MntNeto' in resumenP:
                resumenP['MntNeto'] = resumen['MntNeto']
            elif 'MntNeto' in resumen:
                resumenP['MntNeto'] += resumen['MntNeto']
            elif not 'MntNeto' in resumenP:
                resumenP['MntNeto'] = 0
            if 'MntIVA' in resumen and not 'MntIva' in resumenP:
                resumenP['MntIva'] = resumen['MntIVA']
            elif 'MntIVA' in resumen:
                resumenP['MntIva'] += resumen['MntIVA']
            elif not 'MntIva' in resumenP:
                resumenP['MntIva'] = 0
            if 'TasaIVA' in resumen and not 'TasaIVA' in resumenP:
                resumenP['TasaIVA'] = resumen['TasaIVA']
            if 'MntExe' in resumen and not 'MntExento' in resumenP:
                resumenP['MntExento'] = resumen['MntExe']
            elif 'MntExe' in resumen:
                resumenP['MntExento'] += resumen['MntExe']
            elif not resumenP.get('MntExento'):
                resumenP['MntExento'] = 0
            if not resumenP.get('MntTotal'):
                resumenP['MntTotal'] = resumen['MntTotal']
            else:
                resumenP['MntTotal'] += resumen['MntTotal']
        if 'FoliosEmitidos' in resumenP:
            resumenP['FoliosEmitidos'] +=1
        else:
            resumenP['FoliosEmitidos'] = 1
        if not resumenP.get('FoliosAnulados'):
            resumenP['FoliosAnulados'] = 0
        if resumen.get('Anulado'):
            resumenP['FoliosAnulados'] += 1
        elif 'FoliosUtilizados' in resumenP:
            resumenP['FoliosUtilizados'] += 1
        else:
            resumenP['FoliosUtilizados'] = 1
        if not resumenP.get('T' + str(resumen['TpoDoc'])):
            resumenP['T' + str(resumen['TpoDoc'])] = collections.OrderedDict()
        resumenP[str(resumen['TpoDoc'])+'_folios'] = self._rangosU(
                    resumen, resumenP['T' + str(resumen['TpoDoc'])],
                    continuado)
        if 'Anulado' not in resumen:
            self.total_neto = resumenP.get('MntNeto', 0)
            self.total_iva = resumenP.get('MntIva', 0)
            self.total_exento = resumenP.get('MntExento', 0)
            self.total = resumenP['MntTotal']
        if resumen['TpoDoc'] in [39]:
            self.total_boletas += 1
        return resumenP

    def get_rangos(self):
        resumenes = self._get_resumenes()
        detalles = []

        def pushItem(key_item, item, tpo_doc):
            rango = {
                'tipo_operacion': 'utilizados' if \
                key_item == 'RangoUtilizados' else 'anulados',
                'folio_inicio': item['Inicial'],
                'folio_final': item['Final'],
                'cantidad': int(item['Final']) - int(item['Inicial']) + 1,
                'tpo_doc':  tpo_doc,
            }
            detalles.append(rango)

        for r, value in resumenes.items():
            if value.get('T' + str(r)):
                Rangos = value['T' + str(r)]
                if 'itemUtilizados' in Rangos:
                    for rango in Rangos['itemUtilizados']:
                        pushItem('RangoUtilizados', rango, r)
                if 'itemAnulados' in Rangos:
                    for rango in Rangos['itemAnulados']:
                        pushItem('RangoAnulados', rango, r)
        return detalles

    def _get_resumenes(self):
        if not self.Documento:
            return {}
        resumenes = {}
        #@TODO ordenar documentos
        ant = {}
        for rec in self.Documento:
            if not rec.TipoDTE or rec.TipoDTE not in [39, 41, 61]:
                print("Por este medio solamente se pueden declarar Boletas o \
Notas de crédito Electrónicas, por favor elimine el documento %s del listado" \
% rec.name)
            if self.FchInicio == '':
                self.FchInicio = rec.FechaEmis
            if rec.FechaEmis != self.FchFinal:
                self.FchFinal = rec.FechaEmsi
            rec.sended = True
            resumen = self.getResumen(rec)
            TpoDoc = resumen['TpoDoc']
            if not str(TpoDoc) in ant:
                    ant[str(TpoDoc)] = 0
            if not resumenes.get(TpoDoc):
                resumenes[TpoDoc] = collections.OrderedDict()
            resumenes[TpoDoc] = self._setResumen(
                                    resumen,
                                    resumenes[TpoDoc],
                                    ((ant[str(TpoDoc)] + 1) == rec.Folio)
                                )
            ant[str(TpoDoc)] = rec.Folio
        return resumenes

    def validar(self):
        Resumen = []
        listado = ['TipoDocumento', 'MntNeto', 'MntIva', 'TasaIVA',
                   'MntExento', 'MntTotal', 'FoliosEmitidos', 'FoliosAnulados',
                   'FoliosUtilizados', 'itemUtilizados']
        TpoDocs = []
        if self.Documento:
            resumenes = self._get_resumenes()
            for r, value in resumenes.items():
                if not str(r) in TpoDocs:
                    TpoDocs.append(str(r))
                ordered = collections.OrderedDict()
                for i in listado:
                    if i in value:
                        ordered[i] = value[i]
                    elif i == 'itemUtilizados':
                        Rangos = value['T' + str(r)]
                        folios = []
                        if 'itemUtilizados' in Rangos:
                            utilizados = []
                            for rango in Rangos['itemUtilizados']:
                                utilizados.append({'RangoUtilizados': rango})
                            folios.append({'itemUtilizados': utilizados})
                        if 'itemAnulados' in Rangos:
                            anulados = []
                            for rango in Rangos['itemAnulados']:
                                anulados.append({'RangoAnulados': rango})
                            folios.append({'itemAnulados': anulados})
                        ordered['T' + str(r)] = folios
                Resumen.append({'Resumen': ordered})
            dte = {'item': Resumen}
            etree_xml = util.create_xml(dte)
            sii_xml_request = util.xml_to_string(etree_xml)
            for TpoDoc in TpoDocs:
                sii_xml_request = sii_xml_request.replace('<T' + str(TpoDoc) + '>', '')\
                .replace('</'+str(TpoDoc)+'>', '\n').replace('<T'+str(TpoDoc)+'/>', '\n')
            self.sii_xml_request = sii_xml_request
        return True
