# -*- coding: utf-8 -*-
from facturacion_electronica.impuestos import Impuestos
from facturacion_electronica.linea_impuesto import LineaImpuesto


class Boletas(object):

    def __init__(self, vals, TpoDoc=35):
        self._iniciar()

    @property
    def TipoDTE(self):
        if not hasattr(self, '_tipo_dte'):
            return 35
        return self._tipo_dte

    @TipoDTE.setter
    def TipoDTE(self, val):
        self._tipo_dte = val

    @property
    def Folio(self):
        if not hasattr(self, '_folio'):
            return 0
        return self._folio

    @property
    def MntNeto(self):
        if not hasattr(self, '_mnt_neto'):
            return 0
        return self._mnt_neto

    @MntNeto.setter
    def MntNeto(self, val):
        self._mnt_neto = val

    @property
    def MntExento(self):
        if not hasattr(self, '_mnt_exento'):
            return 0
        return self._mnt_exento

    @MntExento.setter
    def MntExento(self, val):
        self._mnt_exento = val

    @property
    def MntIVA(self):
        if not hasattr(self, '_mnt_iva'):
            return 0
        return self._mnt_iva

    @MntIVA.setter
    def MntIVA(self, val):
        self._mnt_iva = val

    @property
    def MntTotal(self):
        if not hasattr(self, '_mnt_total'):
            return 0
        return self._mnt_total

    @MntTotal.setter
    def MntTotal(self, val):
        self._mnt_total = val

    @property
    def TasaImp(self):
        if not hasattr(self, '_tasa_imp'):
            return 0
        return self._tasa_imp

    @TasaImp.setter
    def TasaImp(self, vals):
        tax = {
                'monto': vals['TasaImp'],
                'sii_code': vals.get('CodImp', 14),
                'sii_type': vals.get('TpoImp', 1),
                'no_rec': True if 'CodIVANoRec' in vals else False,
                'price_include': True,
            }
        iva = Impuestos(tax)
        impuesto = LineaImpuesto({
                'tax_id': iva,
                'base': self.neto,
                'monto': self.monto_impuesto
            })
        self._impuesto = impuesto

    def _iniciar(self):
        self.rango_inicial = 0
        self.rango_final = 0

    def _monto_total(self):
        monto_impuesto = 0
        if self.impuesto and self.impuesto.monto > 0:
            monto_impuesto = self. monto_impuesto = self.neto * (self.impuesto.monto / 100)
        self.monto_total = self.neto + monto_impuesto

    def get_cantidad(self):
        if not self.rango_inicial or not self.rango_final:
            return
        if self.rango_final < self.rango_inicial:
            raise UserError("¡El rango Final no puede ser menor al inicial")
        self.cantidad_boletas = self.rango_final - self.rango_inicial +1
