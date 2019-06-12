# -*- coding: utf-8 -*-
from facturacion_electronica.libro_boletas import Boletas
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica.emisor import Emisor
from facturacion_electronica import clase_util as util
from datetime import datetime
import collections
import logging
_logger = logging.getLogger(__name__)


class Libro(object):

    def __init__(self, vals):
        self._iniciar()
        util.set_from_keys(self, vals)

    @property
    def boletas(self):
        if not hasattr(self, '_boletas'):
            return False
        return self._boletas

    @boletas.setter
    def boletas(self, vals):
        _boletas = []
        for b in vals:
            _boletas.append(Boletas(b))
        self._boletas = _boletas

    @property
    def CodigoRectificacion(self):
        if not hasattr(self, '_codigo_rectificacion'):
            return False
        return self._codigo_rectificacion

    @CodigoRectificacion.setter
    def CodigoRectificacion(self, val):
        self._codigo_rectificacion = val

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
        self._documentos = documentos

    @property
    def Fecha(self):
        if not hasattr(self, '_fecha'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fecha

    @Fecha.setter
    def Fecha(self, val):
        self._fecha = val

    @property
    def FolioNotificacion(self):
        if not hasattr(self, '_folio_notificacion'):
            return 0
        return self._folio_notificacion

    @FolioNotificacion.setter
    def FolioNotificacion(self, val):
        self._folio_notificacion = val

    @property
    def NroSegmento(self):
        if not hasattr(self, '_nro_segmento'):
            return False
        return self._nro_segmento

    @NroSegmento.setter
    def NroSegmento(self, val):
        self._nro_segmento = val

    @property
    def FctProp(self):
        if not hasattr(self, '_fct_prop'):
            return False
        return self._fct_prop

    @FctProp.setter
    def FctProp(self, val):
        self._fct_prop = val

    @property
    def PeriodoTributario(self):
        if not hasattr(self, '_periodo_tributario'):
            return False
        return self._periodo_tributario

    @PeriodoTributario.setter
    def PeriodoTributario(self, val):
        self._periodo_tributario = val

    @property
    def TipoOperacion(self):
        if not hasattr(self, '_tipo_operacion'):
            return 'VENTA'
        return self._tipo_operacion

    @TipoOperacion.setter
    def TipoOperacion(self, val):
        '''
            [
                ('COMPRA', 'Compras'),
                ('VENTA', 'Ventas'),
                ('BOLETA', 'Boleta'),
            ]
        '''
        self._tipo_operacion = val

    @property
    def TipoLibro(self):
        if not hasattr(self, '_tipo_libro'):
            return 'MENSUAL'
        return self._tipo_libro

    @TipoLibro.setter
    def TipoLibro(self, val):
        '''
            [
                ('ESPECIAL','Especial'),
                ('MENSUAL','Mensual'),
                ('RECTIFICA','Rectifica')
            ]
        '''
        self._tipo_libro = val

    @property
    def TipoEnvio(self):
        if not hasattr(self, '_tipo_envio'):
            return 'TOTAL'
        return self._tipo_envio

    @TipoEnvio.setter
    def TipoEnvio(self, val):
        '''
            [
                ('AJUSTE', 'Ajuste'),
                ('TOTAL', 'Total'),
                ('PARCIAL', 'Parcial'),
            ]
        '''
        self._tipo_envio = val

    def _iniciar(self):
        self.sii_message = None
        self.sii_xml_request = None
        self.sii_xml_response = None
        self.sii_send_ident = None

    def _TpoImp(self, imp=1):
        #if imp.CodImp in [14, 1]:
        return 1
        #if imp.CodImp in []: determinar cuando es 18.211 // zona franca
        #    return 2

    def getResumen(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        #det['Emisor']
        #det['IndFactCompra']
        det['NroDoc'] = rec.Folio
        if rec.Anulado:
            det['Anulado'] = 'A'
        #det['Operacion']
        #det['TotalesServicio']
        MntTotal = rec.MntTotal
        det['TpoImp'] = self._TpoImp()
        det['TasaImp'] = 19.0
        if rec.impuestos:
            for imp in rec.impuestos:
                if imp.tax_id.CodImp not in [14]:
                    continue
                det['TpoImp'] = imp.tax_id.TpoImp
                det['TasaImp'] = round(imp.tax_id.TasaImp, 2)
                break
        #det['IndServicio']
        #det['IndSinCosto']
        det['FchDoc'] = rec.FechaEmis
        emisor = rec.Emisor
        if not rec.Emisor and self.TipoOperacion == 'COMPRA':
            emisor = Emisor({
                'RUTEmisor': rec.Receptor['RUTRecep'],
                'RznSoc': rec.Receptor['RznSocRecep'],
            })
        if emisor.CdgSIISucur:
            det['CdgSIISucur'] = emisor.CdgSIISucur
        det['RUTDoc'] = util.format_vat(emisor.RUTEmisor)
        det['RznSoc'] = emisor.RznSoc[:50]
        if rec.Referencia:
            det['TpoDocRef'] = rec._referencias[0].TpoDocRef
            det['FolioDocRef'] = rec._referencias[0].FolioRef
        if rec.MntExe > 0:
            det['MntExe'] = rec.MntExe
        elif self.TipoOperacion in ['VENTA'] and not rec.MntNeto > 0:
            det['MntExe'] = 0
        if rec.MntNeto > 0:
            det['MntNeto'] = rec.MntNeto
        if rec.MntIVA > 0 and not rec.IVAUsoComun:
            det['MntIVA'] = rec.MntIVA
        if rec.MntActivoFijo > 0:
            det['MntActivoFijo'] = rec.MntActivoFijo
            det['MntIVAActivoFijo'] = rec.MntIVAActivoFijo
        if rec.CodIVANoRec:
            det['IVANoRec'] = collections.OrderedDict()
            det['IVANoRec']['CodIVANoRec'] = rec.CodIVANoRec
            det['IVANoRec']['MntIVANoRec'] = rec.MntIVANoRec
        if rec.IVAUsoComun:
            det['IVAUsoComun'] = rec.IVAUsoComun
        if rec.ImptoReten:
            otros_imp = []
            for imp in rec.impuestos:
                if imp.tax_id.CodImp in [14]:
                    continue
                otro = collections.OrderedDict()
                otro['CodImp'] = str(imp.tax_id.CodImp)
                otro['TasaImp'] = imp.tax_id.TasaImp
                otro['MntImp'] = imp.MontoImp
                otros_imp.append({'OtrosImp': otro})
            det['itemOtrosImp'] = otros_imp
            for imp in rec.impuestos:
                if imp.tax_id.Retencion:
                    if imp.tax_id.Retencion == imp.tax_id.TasaImp:
                        det['IVARetTotal'] = imp.MontoImp
                        det['MntIVA'] -= det['IVARetTotal']
                    else:
                        det['IVARetParcial'] = int(round(
                                                self.MntNeto * \
                                                (imp.tax_id.Retencion / 100)))
                        det['IVANoRetenido'] = int(round(i['TaxMnt'] - (
                                            Neto * (tasa.Retencion / 100))))
                        det['MntIVA'] -= det['IVARetParcial']
        det['MntTotal'] = MntTotal
        return det

    def _setResumenBoletas(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        det['TotDoc'] = det['NroDoc'] = rec.Folio
        if rec.impuesto.TasaImp > 0:
            det['TpoImp'] = self._TpoImp(rec.impuesto)
            det['TasaImp'] = rec.TasaImp.TasaImp
            det['MntNeto'] = rec.MntNeto
            det['MntIVA'] = rec.MntIVA
        else:
            det['MntExe'] = rec.MntExe
        det['MntTotal'] = rec.MntTotal
        return det

    def _process_imps(self, tax_line_id, totales=0, currency=None, Neto=0,
                      TaxMnt=0, MntExe=0, ivas={}, imp={}):
        mnt = tax_line_id.compute_all(totales,  currency, 1)['taxes'][0]
        if mnt['monto'] < 0:
            mnt['monto'] *= -1
            mnt['base'] *= -1
        if tax_line_id.CodImp in [14, 15, 17, 18, 19, 30, 31, 32, 33, 34,
                                    36, 37, 38, 39, 41, 47, 48]:
            ivas.setdefault(tax_line_id.id, [tax_line_id, 0])
            ivas[tax_line_id.id][1] += mnt['monto']
            TaxMnt += mnt['monto']
            Neto += mnt['base']
        else:
            imp.setdefault(tax_line_id.id, [tax_line_id, 0])
            imp[tax_line_id.id][1] += mnt['monto']
            if tax_line_id.MntImp == 0:
                MntExe += mnt['base']
        return Neto, TaxMnt, MntExe, ivas, imp

    def getResumenBoleta(self, rec):
        det = collections.OrderedDict()
        det['TpoDoc'] = rec.TipoDTE
        det['FolioDoc'] = rec.Folio
        det['TpoServ'] = 3
        det['FchEmiDoc'] = rec.FechaEmis
        det['FchVencDoc'] = rec.FechaVenc
        #det['PeriodoDesde']
        #det['PeriodoHasta']
        #det['CdgSIISucur']
        Neto = rec.neto
        MntExe = rec.exento
        TaxMnt = rec.iva
        ivas = {}
        imp = {}
        impuestos = {}
        if 'lines' in rec:
            for line in rec.lines:
                if line.tax_ids:
                    for t in line.tax_ids:
                        impuestos.setdefault(t.CodImp, [t, 0])
                        impuestos[t.CodImp][1] += line.price_subtotal_incl
            for key, t in impuestos.items():
                Neto, TaxMnt, MntExe, ivas, imp = self._process_imps(
                                    t[0], t[1], rec.pricelist_id.TpoMoneda,
                                    Neto, TaxMnt, MntExe, ivas, imp)
        else:  # si la boleta fue hecha por contabilidad
            for l in rec.line_ids:
                if l.invoice_line_tax_ids:
                    for t in l.invoice_line_tax_ids:
                        if t.monto > 0:
                            if t.CodImp in [14, 15, 17, 18, 19, 30, 31, 32,
                                              33, 34, 36, 37, 38, 39, 41, 47,
                                              48]:
                                if not ivas.get(t.CodImp):
                                    ivas[t.CodImp] = [t, 0]
                                if l.credit > 0:
                                    ivas[t.CodImp][1] += l.credit
                                else:
                                    ivas[t.CodImp][1] += l.debit
                            else:
                                if not imp.get(t.CodImp):
                                    imp[t.CodImp] = [t, 0]
                                if l.credit > 0:
                                    imp[t.CodImp][1] += l.credit
                                    TaxMnt += l.credit
                                else:
                                    imp[t.CodImp][1] += l.debit
                                    TaxMnt += l.debit
                elif l.tax_ids and l.tax_ids[0].monto > 0:
                    if l.credit > 0:
                        Neto += l.credit
                    else:
                        Neto += l.debit
                elif l.tax_ids and l.tax_ids[0].monto == 0:
                    if l.credit > 0:
                        MntExe += l.credit
                    else:
                        MntExe += l.debit
        #det['IndServicio']
        #det['IndSinCosto']
        det['RUTCliente'] = self.format_vat(rec.Emisor.RUTEmisor)
        if TaxMnt > 0:
            det['MntIVA'] = int(round(TaxMnt))
            for key, t in ivas.items():
                det['TasaIVA'] = t[0].monto
        #det['CodIntCLi']
        if MntExe > 0:
            det['MntExe'] = int(round(MntExe, 0))
        monto_total = int(round((Neto + MntExe + TaxMnt), 0))
        det['MntTotal'] = monto_total
        det['MntNeto'] = int(round(Neto))
        det['MntIVA'] = int(round(TaxMnt))
        return det

    def _procesar_otros_imp(self, resumen, resumenP):
        no_rec = 0 if 'TotImpSinCredito' not in resumenP\
            else resumenP['TotImpSinCredito']
        if not resumenP.get('TotOtrosImp'):
            tots = []
            for o in resumen.get('OtrosImp'):
                tot = {}
                cod = o['CodImp'].replace('_no_rec', '')
                if cod == o['CodImp']:
                    tot['TotOtrosImp'] = collections.OrderedDict()
                    tot['TotOtrosImp']['CodImp'] = cod
                    tot['TotOtrosImp']['TotMntImp'] = o['MntImp']
                    #tot['FctImpAdic']
                    tot['TotOtrosImp']['TotCredImp'] = o['MntImp']
                    tots.append(tot)
                else:
                    no_rec += o['MntImp']
            if tots:
                resumenP['TotOtrosImp'] = tots
            if no_rec > 0:
                resumenP['TotImpSinCredito'] = no_rec
            return resumenP
        seted = False
        itemOtrosImp = []
        for r in resumen.get('OtrosImp', []):
            cod = r['CodImp'].replace('_no_rec', '')
            for o in resumenP['TotOtrosImp']:
                if o['CodImp'] == cod:
                    o['TotMntImp'] += r['MntImp']
                    if cod == r['CodImp'] and not o.get('TotCredImp'):
                        o['TotCredImp'] = r['MntImp']
                    elif cod == r['CodImp']:
                        o['TotCredImp'] += r['MntImp']
                    seted = True
                    itemOtrosImp.append({'TotOtrosImp': o})
                else:
                    no_rec += o['MntImp']
            if not seted:
                if cod == o['CodImp']:
                    tot = collections.OrderedDict()
                    tot['CodImp'] = cod
                    tot['TotMntImp'] = r['MntImp']
                    #tot['FctImpAdic']
                    tot['TotCredImp'] += o['MntImp']
                    itemOtrosImp.append(tot)
                else:
                    no_rec += o['MntImp']
        resumenP['itemOtrosImp'] = itemOtrosImp
        if not resumenP.get('TotImpSinCredito') and no_rec > 0:
            resumenP['TotImpSinCredito'] += no_rec
        elif no_rec:
            resumenP['TotImpSinCredito'] = no_rec
        return resumenP

    def _setResumenPeriodo(self, resumen, resumenP):
        resumenP['TpoDoc'] = resumen['TpoDoc']
        if 'TpoImp' in resumen:
            resumenP['TpoImp'] = resumen['TpoImp'] or 1
        if not resumenP.get('TotDoc'):
            resumenP['TotDoc'] = 1
            if 'TotDoc' in resumen:
                resumenP['TotDoc'] = resumen['TotDoc']
        else:
            resumenP['TotDoc'] += 1
        if 'TotAnulado' in resumenP and 'Anulado' in resumen:
            resumenP['TotAnulado'] += 1
            return resumenP
        elif 'Anulado' in resumen:
            resumenP['TotAnulado'] = 1
            return resumenP
        if 'MntExe' in resumen and not resumenP.get('TotMntExe'):
            resumenP['TotMntExe'] = resumen['MntExe']
        elif 'MntExe' in resumen:
            resumenP['TotMntExe'] += resumen['MntExe']
        elif not resumenP.get('TotMntExe'):
            resumenP['TotMntExe'] = 0
        if 'MntNeto' in resumen and not resumenP.get('TotMntNeto'):
            resumenP['TotMntNeto'] = resumen['MntNeto']
        elif 'MntNeto' in resumen:
            resumenP['TotMntNeto'] += resumen['MntNeto']
        elif not resumenP.get('TotMntNeto'):
            resumenP['TotMntNeto'] = 0
        if 'TotOpIVARec' in resumen:
            resumenP['TotOpIVARec'] = resumen['OpIVARec']
        if 'MntIVA' in resumen and not resumenP.get('TotMntIVA'):
            resumenP['TotMntIVA'] = resumen['MntIVA']
        elif 'MntIVA' in resumen:
            resumenP['TotMntIVA'] += resumen['MntIVA']
        elif not resumenP.get('TotMntIVA'):
            resumenP['TotMntIVA'] = 0
        if 'MntActivoFijo' in resumen and not 'TotOpActivoFijo'in resumenP:
            resumenP['TotOpActivoFijo'] = 1
            resumenP['TotMntActivoFijo'] = resumen['MntActivoFijo']
            resumenP['TotMntIVAActivoFijo'] = resumen['MntIVAActivoFijo']
        elif 'MntActivoFijo' in resumen:
            resumenP['TotOpActivoFijo'] += 1
            resumenP['TotMntActivoFijo'] += resumen['MntActivoFijo']
            resumenP['TotMntIVAActivoFijo'] += resumen['MntIVAActivoFijo']
        if 'IVANoRec' in resumen and not resumenP.get('TotIVANoRec'):
            tot = collections.OrderedDict()
            tot['CodIVANoRec'] = resumen['IVANoRec']['CodIVANoRec']
            tot['TotOpIVANoRec'] = 1
            tot['TotMntIVANoRec'] = resumen['IVANoRec']['MntIVANoRec']
            resumenP['TotIVANoRec'] = [tot]
        elif 'IVANoRec' in resumen:
            seted = False
            itemNoRec = []
            for r in resumenP.get('TotIVANoRec', []):
                if r['CodIVANoRec'] == resumen['IVANoRec']['CodIVANoRec']:
                    r['TotOpIVANoRec'] += 1
                    r['TotMntIVANoRec'] += resumen['IVANoRec']['MntIVANoRec']
                    seted = True
                itemNoRec.extend([r])
            if not seted:
                tot = collections.OrderedDict()
                tot['CodIVANoRec'] = resumen['IVANoRec']['CodIVANoRec']
                tot['TotOpIVANoRec'] = 1
                tot['TotMntIVANoRec'] = resumen['IVANoRec']['MntIVANoRec']
                itemNoRec.extend([tot])
            resumenP['TotIVANoRec'] = itemNoRec
        if resumen.get('IVAUsoComun') and not resumenP.get('TotOpIVAUsoComun', False):
            resumenP['TotOpIVAUsoComun'] = 1
            resumenP['TotIVAUsoComun'] = resumen['IVAUsoComun']
            if not self.FctProp:
                raise util.UserError("Debe Ingresar Factor de proporcionlaidad")
            resumenP['FctProp'] = self.FctProp
            resumenP['TotCredIVAUsoComun'] = int(round((
                            resumen['IVAUsoComun'] * self.FctProp)))
        elif resumen.get('IVAUsoComun'):
            resumenP['TotOpIVAUsoComun'] += 1
            resumenP['TotIVAUsoComun'] += resumen['IVAUsoComun']
            resumenP['TotCredIVAUsoComun'] += int(round((
                            resumen['IVAUsoComun'] * self.FctProp)))
        if resumen.get('TotOtrosImp'):
            resumenP = self._procesar_otros_imp(resumen, resumenP)
        if 'IVARetTotal' in resumen and not resumenP.get('TotOpIVARetTotal'):
            resumenP['TotIVARetTotal'] = resumen['IVARetTotal']
        elif 'IVARetTotal' in resumen:
            resumenP['TotIVARetTotal'] += resumen['IVARetTotal']
        if 'IVARetParcial' in resumen and not resumenP.get('TotOpIVARetParcial'):
            resumenP['TotIVARetParcial'] = resumen['IVARetParcial']
            resumenP['TotIVANoRetenido'] = resumen['IVANoRetenido']
        elif 'IVARetParcial' in resumen:
            resumenP['TotIVARetParcial'] += resumen['IVARetParcial']
            resumenP['TotIVANoRetenido'] += resumen['IVANoRetenido']
        #@TODO otros tipos IVA
        if not resumenP.get('TotMntTotal'):
            resumenP['TotMntTotal'] = resumen['MntTotal']
        else:
            resumenP['TotMntTotal'] += resumen['MntTotal']
        return resumenP

    def _setResumenPeriodoBoleta(self, resumen, resumenP):
        resumenP['TpoDoc'] = resumen['TpoDoc']
        if 'Anulado' in resumen and 'TotAnulado' in resumenP:
            resumenP['TotAnulado'] += 1
            return resumenP
        elif 'Anulado' in resumen:
            resumenP['TotAnulado'] = 1
            return resumenP
        if not 'TotalesServicio' in resumenP:
            resumenP['TotalesServicio'] = collections.OrderedDict()
            resumenP['TotalesServicio']['TpoServ'] = resumen['TpoServ']#@TODO separar por tipo de servicio
            resumenP['TotalesServicio']['TotDoc'] = 0
        resumenP['TotalesServicio']['TotDoc'] += 1
        if 'MntExe' in resumen and not 'TotMntExe' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntExe'] = resumen['MntExe']
        elif 'MntExe' in resumen:
            resumenP['TotalesServicio']['TotMntExe'] += resumen['MntExe']
        elif not resumenP['TotalesServicio'].get('TotMntExe'):
            resumenP['TotalesServicio']['TotMntExe'] = 0
        if 'MntNeto' in resumen and not resumenP['TotalesServicio'].get('TotMntNeto'):
            resumenP['TotalesServicio']['TotMntNeto'] = resumen['MntNeto']
        elif 'MntNeto' in resumen:
            resumenP['TotalesServicio']['TotMntNeto'] += resumen['MntNeto']
        elif not resumenP['TotalesServicio'].get('TotMntNeto'):
            resumenP['TotalesServicio']['TotMntNeto'] = 0
        if 'MntIVA' in resumen:
            resumenP['TotalesServicio']['TasaIVA'] = resumen['TasaIVA']
        if 'MntIVA' in resumen and not 'TotMntIVA' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntIVA'] = resumen['MntIVA']
        elif 'MntIVA' in resumen:
            resumenP['TotalesServicio']['TotMntIVA'] += resumen['MntIVA']
        elif not 'TotMntIVA' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntIVA'] = 0
        if not 'TotMntTotal' in resumenP['TotalesServicio']:
            resumenP['TotalesServicio']['TotMntTotal'] = resumen['MntTotal']
        else:
            resumenP['TotalesServicio']['TotMntTotal'] += resumen['MntTotal']
        return resumenP

    def validar(self):
        resumenes = []
        resumenesPeriodo = {}
        for rec in self.Documento:
            rec.sended = True
            TpoDoc = rec.TipoDTE
            if not TpoDoc in resumenesPeriodo:
                resumenesPeriodo[TpoDoc] = {}
            if self.TipoOperacion == 'BOLETA':
                resumen = self.getResumenBoleta(rec)
                resumenesPeriodo[TpoDoc] = self._setResumenPeriodoBoleta(
                                    resumen, resumenesPeriodo[TpoDoc])
                del(resumen['MntNeto'])
                del(resumen['MntIVA'])
                del(resumen['TasaIVA'])
            else:
                resumen = self.getResumen(rec)
                resumenes.extend([{'Detalle': resumen}])
            if self.TipoOperacion != 'BOLETA':
                resumenesPeriodo[TpoDoc] = self._setResumenPeriodo(
                                    resumen, resumenesPeriodo[TpoDoc])
        if self.boletas: # no es el libro de boletas especial
            for boletas in self.boletas:
                resumenesPeriodo[boletas.TipoDTE] = {}
                resumen = self._setResumenBoletas(boletas)
                del(resumen['TotDoc'])
                resumenesPeriodo[boletas.TipoDTE] = self._setResumenPeriodo(
                                    resumen, resumenesPeriodo[boletas.TipoDTE])
                # resumenes.extend([{'Detalle':resumen}])
        lista = ['TpoDoc', 'TpoImp', 'TotDoc', 'TotAnulado', 'TotMntExe',
                 'TotMntNeto', 'TotalesServicio', 'TotOpIVARec',
                 'TotMntIVA', 'TotMntIVA', 'TotOpActivoFijo',
                 'TotMntActivoFijo', 'TotMntIVAActivoFijo', 'TotIVANoRec',
                 'TotOpIVAUsoComun', 'TotIVAUsoComun', 'FctProp',
                 'TotCredIVAUsoComun', 'TotOtrosImp', 'TotImpSinCredito',
                 'TotIVARetTotal', 'TotIVARetParcial', 'TotMntTotal',
                 'TotIVANoRetenido', 'TotTabPuros', 'TotTabCigarrillos',
                 'TotTabElaborado', 'TotImpVehiculo']
        ResumenPeriodo = []
        for r, value in resumenesPeriodo.items():
            total = collections.OrderedDict()
            for v in lista:
                if v in value:
                    total[v] = value[v]
            ResumenPeriodo.extend([{'TotalesPeriodo': total}])
        dte = collections.OrderedDict()
        if ResumenPeriodo:
            dte['ResumenPeriodo'] = ResumenPeriodo
            dte_etree = util.create_xml({'item': dte})
            dte = util.create_xml(resumenes, dte_etree)
            dte = util.create_xml({'TmstFirma': util.time_stamp()}, dte_etree)
        self.sii_xml_request = util.xml_to_string(dte)
        return True
