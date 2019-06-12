# -*- coding: utf-8 -*-
from facturacion_electronica.dte import DTE
from facturacion_electronica.documento_linea import LineaDetalle
from facturacion_electronica.documento_referencias import Referencia
from facturacion_electronica.linea_impuesto import LineaImpuesto
from facturacion_electronica.receptor import Recep
from facturacion_electronica.clase_util import UserError
from facturacion_electronica.impuestos import Impuestos
from facturacion_electronica.global_descuento_recargo import GlobalDescuentoRecargo as GDR
from facturacion_electronica import clase_util as util
from datetime import datetime
import collections
import re


class Documento(DTE):

    def __init__(self, vals, resumen=False):
        self._resumen = resumen
        util.set_from_keys(self, vals)
        if 'codigo_vendedor' in vals:
            self.CodVndor = vals['codigo_vendedor']
        if 'codigo_caja' in vals:
            self.CodCaja = vals['codigo_caja']
        if vals.get('ticket'):
            self.TpoImpresion = 'T'
        #if self.es_boleta(False):
        #    if not self._resumen and (not self.CodCaja or not self.CodVndor):
        #        print("Debe Ingresar código de vendedor  y de caja")

    @property
    def Anulado(self):
        if not hasattr(self, '_anulado'):
            return False
        return self._anulado

    @Anulado.setter
    def Anulado(self, val):
        self._anulado = val

    @property
    def CiudadDest(self):
        if not hasattr(self, '_ciudad_dest'):
            return False
        return self._ciudad_dest

    @CiudadDest.setter
    def CiudadDest(self, val):
        self._ciudad_dest = val

    @property
    def CodCaja(self):
        return self._cod_caja

    @CodCaja.setter
    def CodCaja(self, val):
        self._cod_caja = val

    @property
    def CodIVANoRec(self):
        if not hasattr(self, '_no_rec_code'):
            return False
        return self._no_rec_code

    @CodIVANoRec.setter
    def CodIVANoRec(self, val):
        '''
            Integer con una de las opciones
            [
                ('1','Compras destinadas a IVA a generar operaciones no gravados o exentas.'),
                ('2','Facturas de proveedores registrados fuera de plazo.'),
                ('3','Gastos rechazados.'),
                ('4','Entregas gratuitas (premios, bonificaciones, etc.) recibidos.'),
                ('9','Otros.')
            ]
        '''
        self._no_rec_code = val

    @property
    def CodOtroImp(self):
        return self._otroImp

    @CodOtroImp.setter
    def CodOtroImp(self, vals):
        if type(vals) is dict:
            vals = [vals]
        for val in vals:
            tax = {
                    'TasaImp': val['TasaOtroImp'],
                    'CodImp': val['CodOtroImp'],
                    'no_rec': True if val['MontoOtroImpNoRec'] and val['MontoOtroImpNoRec'] > 0 else False,
                    'Retencion': val.get('Retencion')

            }
            otroImp = Impuestos(tax)
            impuesto = LineaImpuesto({
                            'tax_id': otroImp,
                            'base': self.neto,
                            'MontoImp': vals.get('MontoOtroImp', 19),
                            })
            self.impuestos = impuesto

    @property
    def CodVndor(self):
        if not hasattr(self, '_cod_vndor'):
            return False
        return self._cod_vndor

    @CodVndor.setter
    def CodVndor(self, val):
        self._cod_vndor = val

    @property
    def CmnaDest(self):
        if not hasattr(self, '_cmna_dest'):
            return False
        return self._cmna_dest

    @CmnaDest.setter
    def CmnaDest(self, val):
        self._cmna_dest = val

    @property
    def Detalle(self):
        if not hasattr(self, '_lineas_detalle'):
            return []
        line_number = 1
        invoice_lines = []
        for line in self._lineas_detalle:
            lines = collections.OrderedDict()
            lines['NroLinDet'] = line_number
            if line.CdgItem:
                cdg_items = []
                for cdg in line.CdgItem:
                    if cdg.get('VlrCodigo') == 'NO_PRODUCT':
                        no_product = True
                    else:
                        cdg_line = collections.OrderedDict()
                        cdg_line['TpoCodigo'] = cdg.get('TpoCodigo', 'INT1')
                        cdg_line['VlrCodigo'] = cdg.get('VlrCodigo', False)
                        cdg_items.append({'CdgItem': cdg_line})
                lines['cdg_items'] = cdg_items
            for t in line.Impuesto:
                taxInclude = t.price_include
            if line.IndExe:
                lines['IndExe'] = 1
            #if line.product_id.type == 'events':
            #   lines['ItemEspectaculo'] =
#            if self.es_boleta():
#                lines['RUTMandante']
            lines['NmbItem'] = line.NmbItem
            lines['DscItem'] = line.DscItem #descripción más extenza
            if line.CdgItem:
                lines['NmbItem'] = line.NmbItem
            #lines['InfoTicket']
            if line.QtyItem > 0:
                lines['QtyItem'] = line.QtyItem
                lines['UnmdItem'] = line.uom_id[:4]
            elif line.QtyItem < 0:
                raise UserError("NO puede ser menor que 0")
            if line.PrcItem:
                lines['PrcItem'] = line.PrcItem
            for imp in line.Impuesto:
                if imp.es_adicional:
                    lines['CodImpAdic'] = imp.CodImp
            if line.DescuentoMonto > 0:
                if line.DescuentoPct:
                    lines['DescuentoPct'] = line.DescuentoPct
                lines['DescuentoMonto'] = line.DescuentoMonto
            if not line.MntBruto:
                lines['MontoItem'] = line.MontoItem
            line_number += 1
            invoice_lines.extend([{'Detalle': lines}])
            if line.IndExe and not self.es_boleta(False):
                self.MntBruto = False
        return invoice_lines

    @Detalle.setter
    def Detalle(self, vals=[]):
        NroLinDet = 0
        recs = []
        for d in vals:
            NroLinDet += 1
            NroLinDet = d.get('NroLinDet', NroLinDet)
            valor_iva = 19 #self.Emisor.ValorIva if self.Emisor else 19
            linea = LineaDetalle(
                            d,
                            self.TpoMoneda,
                            valor_iva=valor_iva,
                            NroLinDet=NroLinDet
                        )
            self.impuestos = linea
            recs.append(linea)
        self._lineas_detalle = sorted(recs, key=lambda l: l.NroLinDet)

    @property
    def DirDest(self):
        if not hasattr(self, '_dir_dest'):
            return False
        return self._dir_dest

    @DirDest.setter
    def DirDest(self, val):
        self._dir_dest = val

    @property
    def DscRcgGlobal(self):
        if not hasattr(self, '_gdrs'):
            return []
        result = []
        lin_dr = 1
        dr_line = {}
        dr_line = collections.OrderedDict()
        for dr in self._gdrs:
            dr_line['NroLinDR'] = dr.NroLinDR
            dr_line['TpoMov'] = dr.TpoMov
            if dr.GlosaDR:
                dr_line['GlosaDR'] = dr.GlosaDR
            dr_line['TpoValor'] = dr.TpoValor
            dr_line['ValorDR'] = dr.ValorDR
            if self.TipoDTE in [34] and (
                    self.Referencia and \
                    self._referencias[0].TpoDocRef == '34'):
                dr_line['IndExeDR'] = 1
            result.append({'DscRcgGlobal': dr_line})
            lin_dr += 1
        return result

    @DscRcgGlobal.setter
    def DscRcgGlobal(self, vals=[]):
        """
            "DscRcgGlobal": [
                    {
                        "valor": 500,
                        "tipo": "monto", # monto o porcentaje
                        "glosa": "descripción descuento"
                    },
                ]
        """
        gdrs = []
        for r in vals:
            gdr = GDR(r)
            gdrs.append(gdr)
        self._gdrs = gdrs

    @property
    def Encabezado(self):
        encabezado = collections.OrderedDict()
        encabezado['IdDoc'] = self.IdDoc
        encabezado['Emisor'] = self.Emisor
        encabezado['Receptor'] = self.Receptor
        if self.TipoDespacho:
            encabezado['Transporte'] = self.Transporte
        encabezado['Totales'] = self.Totales
        return encabezado

    @Encabezado.setter
    def Encabezado(self, vals={}):
        util.set_from_keys(self, vals)

    @property
    def FchVenc(self):
        if not hasattr(self, '_fch_venc'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fch_venc

    @FchVenc.setter
    def FchVenc(self, val):
        self._fch_venc = util.get_fecha(val)

    @property
    def FechaEmis(self):
        if not hasattr(self, '_fecha_emis'):
            return datetime.strftime(datetime.now(), '%Y-%m-%d')
        return self._fecha_emis

    @FechaEmis.setter
    def FechaEmis(self, val):
        self._fecha_emis = util.get_fecha(val)

    @property
    def FmaPago(self):
        if not hasattr(self, '_fma_pago'):
            return 1
        return self._fma_pago

    @FmaPago.setter
    def FmaPago(self, val):
        '''
            [
                ('1','Contado'),
                ('2','Crédito'),
                ('3','Gratuito')
            ]
        '''
        self._fma_pago = val

    @property
    def Folio(self):
        if not hasattr(self, '_folio'):
            return 0
        return self._folio

    @Folio.setter
    def Folio(self, val):
        self._folio = int(val)

    @property
    def IdDoc(self):
        IdDoc = collections.OrderedDict()
        if not hasattr(self, '_tpo_dte'):
            return IdDoc
        IdDoc['TipoDTE'] = self.TipoDTE
        IdDoc['Folio'] = self.Folio
        IdDoc['FchEmis'] = self.FechaEmis
        if self.es_boleta() and self.IndServicio:
            IdDoc['IndServicio'] = self.IndServicio
        if self.TipoDespacho:
            IdDoc['TipoDespacho'] = self.TipoDespacho
        if self.IndTraslado:
            IdDoc['IndTraslado'] = self.IndTraslado
        if self.TpoImpresion:
            IdDoc['TpoImpresion'] = self.TpoImpresion
        #if self.tipo_servicio:
        #    Encabezado['IdDoc']['IndServicio'] = 1,2,3,4
        # todo: forma de pago y fecha de vencimiento - opcional
        if self.MntBruto and self.MntExe == 0 and not self.es_boleta(False):
            IdDoc['MntBruto'] = 1
        if not self.es_boleta():
            IdDoc['FmaPago'] = self.FmaPago
        if not self.MntBruto and self.es_boleta(False):
            IdDoc['IndMntNeto'] = 2
        #if self.es_boleta():
            #Servicios periódicos
        #    IdDoc['PeriodoDesde'] =
        #    IdDoc['PeriodoHasta'] =
        if not self.es_boleta(False):
            IdDoc['FchVenc'] = self.FchVenc
        return IdDoc

    @IdDoc.setter
    def IdDoc(self, vals={}):
        util.set_from_keys(self, vals)

    @property
    def impuestos(self):
        _impuestos = []
        if not hasattr(self, '_impuestos'):
            return _impuestos
        for k, v in self._impuestos.items():
            _impuestos.append(v)
        return _impuestos

    @property
    def impuesto_incluido(self):
        return self.MntBruto

    @impuestos.setter
    def impuestos(self, linea):
        if not linea:
            return
        if not hasattr(self, '_impuestos'):
            self._impuestos = {}

        def set_impuesto(val, base=0):
            imp = False
            if not isinstance(val, LineaImpuesto):
                imp = self._impuestos.get(str(val.CodImp), False)
            if not imp:
                if isinstance(val, LineaImpuesto):
                    imp = val
                else:
                    imp = LineaImpuesto({
                                'tax_id': val,
                                'base': 0,
                                'MontoImp': 0,
                                }
                            )
            imp.base += base
            imp._compute_tax()
            self._impuestos[str(imp.tax_id.CodImp)] = imp
        if isinstance(linea, LineaImpuesto):
            set_impuesto(linea)
        elif type(linea) is list:
            for l in linea:
                for i in l.Impuesto:
                    set_impuesto(i, l.MontoItem)
        else:
            for i in linea.Impuesto:
                set_impuesto(i, linea.MontoItem)

    @property
    def ImptoReten(self):
        if not hasattr(self, '_imp_reten'):
            return False
        return self._imp_reten

    @ImptoReten.setter
    def ImptoReten(self, vals):
        for val in vals:
            tax = {
                 'TasaImp': val.get('TasaImp', 19),
                 'CodImp': val.get('TipoImp', 15),
                 'Retencion': val.get('Retencion', 19),
            }
            iva = Impuestos(tax)
            impuesto = LineaImpuesto({
                                    'tax_id': iva,
                                    'MontoImp': val.get('MontoImpt', 0),
                                })
            self.impuestos = impuesto
        self._imp_reten = True

    @property
    def IndTraslado(self):
        if not hasattr(self, '_ind_traslado'):
            return False
        return self._ind_traslado

    @IndTraslado.setter
    def IndTraslado(self, val):
        self._ind_traslado = val

    @property
    def IndServicio(self):
        if not hasattr(self, '_ind_servicio'):
            return False
        return self._ind_servicio

    @IndServicio.setter
    def IndServicio(self, val):
        self._ind_servicio = val

    @property
    def IVAUsoComun(self):
        if not hasattr(self, '_iva_uso_comun'):
            return 0
        return self.MntIVA

    @IVAUsoComun.setter
    def IVAUsoComun(self, val):
        if not val:
            return
        self._iva_uso_comun = val

    @property
    def MntActivoFijo(self):
        if not hasattr(self, '_activo_fijo'):
            return 0
        return self._activo_fijo

    @MntActivoFijo.setter
    def MntActivoFijo(self, val):
        tax = {
             'TasaImp': val.get('TasaImp', 19),
             'CodImp': val.get('CodImp', 14),
             'TpoImp': val.get('TpoImp', 1),
        }
        iva = Impuestos(tax)
        impuesto = LineaImpuesto({
                                'tax_id': iva,
                                'base': val,
                                'ActivoFijo': True,
                                })
        impuesto._compute_tax()
        self.MntIVAActivoFijo = impuesto.MontoImp
        self.impuesto = impuesto
        self.activo_fijo = val

    @property
    def MntIVAActivoFijo(self):
        if not hasattr(self, '_iva_activo_fijo'):
            return 0
        return self._iva_activo_fijo

    @MntIVAActivoFijo.setter
    def MntIVAActivoFijo(self, val):
        self._iva_activo_fijo = val

    @property
    def MntIVANoRec(self):
        if not hasattr(self, '_iva_no_rec'):
            return 0
        return self._iva_no_rec

    @MntIVANoRec.setter
    def MntIVANoRec(self, val):
        self._iva_no_rec = val

    @property
    def MntBruto(self):
        if not hasattr(self, '_mnt_bruto'):
            return False
        return self._mnt_bruto

    @MntBruto.setter
    def MntBruto(self, val):
        self._mnt_bruto = val

    @property
    def MntExe(self):
        if not self._resumen and not hasattr(self, '_mnt_exe')\
                and self.Detalle:
            self._compute_monto()
        if not hasattr(self, '_mnt_exe'):
            return 0
        if self.DscRcgGlobal:
            return self._aplicar_dsc_rcg(self._mnt_exe, False, True)
        return self._mnt_exe

    @MntExe.setter
    def MntExe(self, val):
        if val == 0:
            return 0
        tax = {
                'TasaImp': 0,
                'CodImp': 0,
            }
        '''
        exento = Impuestos(tax)
        impuesto = LineaImpuesto({
                        'tax_id': exento,
                        'base': val,
                        'MontoImp': val,
                        })
        self.impuestos = impuesto'''
        self._mnt_exe = int(round(val))

    @property
    def MntIVA(self):
        if not hasattr(self, '_mnt_iva'):
            return 0
        if self.DscRcgGlobal:
            return self._aplicar_dsc_rcg(self._mnt_iva)
        return self._mnt_iva

    @MntIVA.setter
    def MntIVA(self, val):
        self._mnt_iva = int(round(val))

    @property
    def MntNeto(self):
        if not self._resumen and not hasattr(self, '_mnt_neto')\
                and self.Detalle:
            self._compute_monto()
        if not hasattr(self, '_mnt_neto'):
            return 0
        if self.DscRcgGlobal:
            return self._aplicar_dsc_rcg(self._mnt_neto)
        return self._mnt_neto

    @MntNeto.setter
    def MntNeto(self, val):
        if self._resumen and self.MntIVA == 0:
            tax = {
                'TasaImp': 19,
                'CodImp': 14,
                'TpoImp': 1
            }
            iva = Impuestos(tax)
            impuesto = LineaImpuesto({
                                'tax_id': iva,
                                'base': val
                                })
            self.impuestos = impuesto
        self._mnt_neto = int(round(val))

    @property
    def MontoOtroImpNoRec(self):
        return

    @property
    def MntTotal(self):
        if not hasattr(self, '_mnt_total') and \
         self.MntExe == 0 and self.MntNeto == 0:
            return 0
        elif self.MntExe > 0 and (not hasattr(self, '_mnt_total') \
                                  or self._mnt_total == 0):
            self._compute_monto()
        if (self.MntNeto > 0 and self.MntIVA == 0) or \
                not hasattr(self, '_mnt_total'):
            self._compute_monto()
        if self.DscRcgGlobal:
            return (self.MntNeto + self.MntIVA + self.MntExe)
        return self._mnt_total

    @MntTotal.setter
    def MntTotal(self, val):
        monto_total = int(round(val, 0))
        if self.no_product:
            monto_total = 0
        self._mnt_total = monto_total

    @MontoOtroImpNoRec.setter
    def MontoOtroImpNoRec(self, vals):
        tax = {
                'TasaImp': -1,
                'CodImp': -1,
                'no_rec': True,
            }
        no_rec = Impuestos(tax)
        impuesto = LineaImpuesto({
                        'tax_id': no_rec,
                        'base': 1,
                        'MontoImp': vals['MontoOtroImpNoRec'],
                        })
        self.impuestos = impuesto

    @property
    def no_product(self):
        if not hasattr(self, '_no_product'):
            return False
        return self._no_product

    @no_product.setter
    def no_product(self, val):
        self._no_product = val

    @property
    def NombreChofer(self):
        if not hasattr(self, '_nombre_chofer'):
            return False
        return self._nombre_chofer

    @NombreChofer.setter
    def NombreChofer(self, val):
        self._nombre_chofer = val

    @property
    def NroDTE(self):
        if not hasattr(self, '_nro_dte'):
            return 1
        return self._nro_dte

    @NroDTE.setter
    def NroDTE(self, val):
        self._nro_dte = int(val)

    @property
    def Patente(self):
        if not hasattr(self, '_patente'):
            return False
        return self._patente

    @Patente.setter
    def Patente(self, val):
        self._patente = val

    @property
    def Receptor(self):
        if not hasattr(self, '_receptor'):
            return False
        Receptor = collections.OrderedDict()
        #if self.es_boleta():
        #    Receptor['CdgIntRecep']
        Receptor['RUTRecep'] = self._receptor.RUTRecep
        Receptor['RznSocRecep'] = self._receptor.RznSocRecep
        if not self.es_boleta():
            Receptor['GiroRecep'] = self._receptor.GiroRecep
        if self._receptor.Contacto:
            Receptor['Contacto'] = self._receptor.Contacto
        if self._receptor.CorreoRecep and not self.es_boleta():
            Receptor['CorreoRecep'] = self._receptor.CorreoRecep
        Receptor['DirRecep'] = self._receptor.DirRecep
        Receptor['CmnaRecep'] = self._receptor.CmnaRecep
        Receptor['CiudadRecep'] = self._receptor.CiudadRecep
        return Receptor

    @Receptor.setter
    def Receptor(self, vals):
        self._receptor = Recep(vals)

    @property
    def Referencia(self):
        if not hasattr(self, '_referencias') or not self._referencias:
            return False
        lin_ref = 1
        ref_lines = []
        for ref in self._referencias:
                ref_line = collections.OrderedDict()
                ref_line['NroLinRef'] = lin_ref
                if not self.es_boleta():
                    if ref.TpoDocRef:
                        ref_line['TpoDocRef'] = ref.TpoDocRef
                        ref_line['FolioRef'] = ref.FolioRef
                    ref_line['FchRef'] = ref.FchRef or datetime.strftime(
                                            datetime.now(), '%Y-%m-%d')
                if hasattr(ref, 'CodRef'):
                    ref_line['CodRef'] = ref.CodRef
                    if ref.CodRef == 2:
                        dice = re.compile(r'DICE:(.*)DEBE DECIR:')
                        if len(dice.findall(ref.RazonRef.upper())) == 0:
                            raise UserError('Modificación de texto debe \
llevar estrictamente las palabras Dice: y debe decir:')
                ref_line['RazonRef'] = ref.RazonRef
                if self.es_boleta(False):
                    ref_line['CodVndor'] = self.CodVndor
                    ref_lines['CodCaja'] = self.CodCaja
                ref_lines.append({'Referencia': ref_line})
                lin_ref += 1
        return ref_lines

    @Referencia.setter
    def Referencia(self, vals=[]):
        self._referencias = []
        for ref in vals:
            self._referencias.append(Referencia(ref))

    @property
    def RUTChofer(self):
        if not hasattr(self, '_rut_chofer'):
            return False
        return self._rut_chofer

    @RUTChofer.setter
    def RUTChofer(self, val):
        self._rut_chofer = util.format_vat(val)

    @property
    def RUTTrans(self):
        if not hasattr(self, '_rut_trans'):
            return False
        return self._rut_trans

    @RUTTrans.setter
    def RUTTrans(self, val):
        self._rut_trans = util.format_vat(val)

    @property
    def sii_barcode_img(self):
        if not hasattr(self, '_sii_barcode_img'):
            return False
        return self._sii_barcode_img

    @sii_barcode_img.setter
    def sii_barcode_img(self, val):
        self._sii_barcode_img = val.decode()

    @property
    def TasaImp(self):
        if not hasattr(self, '_tasa_imp'):
            return 19
        return self._tasa_imp

    @TasaImp.setter
    def TasaImp(self, val):
        self._tasa_imp = round(val, 2)

    @property
    def TipoDespacho(self):
        if not hasattr(self, '_tipo_despacho'):
            return False
        return self._tipo_despacho

    @TipoDespacho.setter
    def TipoDespacho(self, val):
        self._tipo_despacho = val

    @property
    def TipoDTE(self):
        if not hasattr(self, '_tpo_dte'):
            return 33
        return self._tpo_dte

    @TipoDTE.setter
    def TipoDTE(self, val):
        self._tpo_dte = val

    @property
    def Totales(self):
        Totales = collections.OrderedDict()
        if self.no_product:
            Totales['MntTotal'] = 0
            return Totales
        if not self.es_boleta() or not self.MntBruto:
            Totales['MntNeto'] = self.MntNeto
        Totales['MntExe'] = self.MntExe
        if not self.es_boleta():
            Totales['TasaIVA'] = self.TasaImp
        if not self.es_boleta() or not self.MntBruto:
            Totales['IVA'] = int(round(self.MntIVA, 0))
        if self.impuestos:
            for i in self.impuestos:
                if i.tax_id.es_adicional:
                    Totales['ImptoReten'] = collections.OrderedDict()
                    Totales['ImptoReten']['TpoImp'] = i.tax_id.CodImp
                    Totales['ImptoReten']['TasaImp'] = round(i.tax_id.TasaImp, 2)
                    Totales['ImptoReten']['MontoImp'] = int(round(i.MontoImp))
        Totales['MntTotal'] = self.MntTotal
        #Totales['MontoNF']
        #Totales['TotalPeriodo']
        #Totales['SaldoAnterior']
        #Totales['VlrPagar']
        return Totales

    @Totales.setter
    def Totales(self, vals={}):
        util.set_from_keys(self, vals)

    @property
    def TpoImpresion(self):
        if not hasattr(self, '_tpo_impresion'):
            return False
        return self._tpo_impresion

    @TpoImpresion.setter
    def TpoImpresion(self, val):
        self._tpo_impresion = val

    @property
    def TpoMoneda(self):
        if not hasattr(self, '_tpo_moneda'):
            return False
        return self._tpo_moneda

    @TpoMoneda.setter
    def TpoMoneda(self, val):
        self._tpo_moneda = val

    @property
    def Transporte(self):
        if not self.IndTraslado:
            return False
        Transporte = collections.OrderedDict()
        if self.Patente:
            Transporte['Patente'] = self.Patente[:8]
        if self.IndTraslado in ['2', '3'] and self.chofer:
            if not self.Emisor.RUTEmisor:
                raise UserError("Debe llenar los datos del chofer")
            if self.IndTraslado == '2':
                Transporte['RUTTrans'] = self.Emisor.RUTEmisor
            else:
                if not self.carrier_id:
                    raise UserError("Debe especificar el RUT del transportista\
, en su ficha de receptor")
                Transporte['RUTTrans'] = self.RUTTrans
            if self.RUTChofer:
                Transporte['Chofer'] = collections.OrderedDict()
                Transporte['Chofer']['RUTChofer'] = self.RUTChofer
                Transporte['Chofer']['NombreChofer'] = self.NombreChofer[:30]
        Transporte['DirDest'] = self.DirDest
        Transporte['CmnaDest'] = self.CmnaDest
        Transporte['CiudadDest'] = self.CiudadDest
        ''' @TODO SUb Area Aduana '''
        return Transporte

    @Transporte.setter
    def Transporte(self, vals):
        util.set_from_keys(self, vals)

    def es_boleta(self, include_reference=True):
        boletas = [35, 38, 39, 41, 70, 71]
        if self.TipoDTE in boletas\
            or (include_reference and hasattr(self, '_referencias') and\
                self._referencias and \
                self._referencias[0].TpoDocRef in boletas):
            return True
        return False

    def get_agrupados(self, monto, Afectos=True, Exentos=False):
        result = {'D': 0.00, 'R': 0.00}
        for gdr in self._gdrs:
            if (Afectos and gdr.Afectos) or (Exentos and gdr.Exentos):
                result[gdr.TpoMov] += gdr.get_monto(monto)
        return result

    def _aplicar_dsc_rcg(self, monto, Afectos=True, Exentos=False):
        agrupados = self.get_agrupados(monto, Afectos, Exentos)
        monto_gdr = agrupados['R'] - agrupados['D']
        return int(round(monto + monto_gdr))

    def _compute_monto(self):
        monto_tax = 0 if self.Detalle else self.MntIVA
        monto_untaxed = 0 if self.Detalle else self.MntNeto
        monto_exe = 0 if self.Detalle else self.MntExe
        activo_fijo = 0
        iva_activo_fijo = 0
        if not hasattr(self, '_lineas_detalle'):
            _lineas_detalle = []
        else:
            _lineas_detalle = self._lineas_detalle
        for line in _lineas_detalle:
            if line.IndExe:
                monto_exe += line.MontoItem
        if not self._resumen and monto_tax != 0:
            for li in self.impuestos:
                if li.tax_id.TasaImp > 0:
                    if li.MontoImp == 0:
                        if li.base == 0 and self._resumen:
                            li.base = self.MntNeto
                        li._compute_tax()
                    if li.ActivoFijo:
                        activo_fijo += li.base
                        iva_activo_fijo += li.MontoImp
                    else:
                        monto_tax += li.MontoImp
                        monto_untaxed += li.base
        #self.MntActivoFijo = activo_fijo
        self.MntIVAActivoFijo = iva_activo_fijo
        self.MntExe = monto_exe
        self.MntNeto = monto_untaxed
        self.MntIVA = monto_tax
        self.MntTotal = monto_untaxed + monto_tax + monto_exe

    def _es_nota(self):
        return self.TipoDTE in [55, 56, 60, 61, 111, 112]
