# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util


class LineaImpuesto(object):

    def __init__(self, vals):
        self._iniciar()
        util.set_from_keys(vals)
        self.tax_id = vals['tax_id']
        self._compute_tax()

    @property
    def ActivoFijo(self):
        if not hasattr(self, '_activo_fijo'):
            return False
        return self._activo_fijo

    @ActivoFijo.setter
    def ActivoFijo(self, val):
        self._activo_fijo = val

    @property
    def base(self):
        if not hasattr(self, '_base'):
            return 0
        if self.tax_id and self.tax_id.price_include and self.tax_id.TasaImp != 0:
            return self._base / (1 + (self.tax_id.TasaImp / 100.0))
        return self._base

    @base.setter
    def base(self, val):
        self._base = int(round(val))

    @property
    def MontoImp(self):
        if not hasattr(self, '_monto'):
            return 0
        return self._monto

    @MontoImp.setter
    def MontoImp(self, val):
        self._monto = int(round(val))

    def _iniciar(self):
        self.tax_id = None

    def _compute_tax(self):
        if not self.tax_id or self.tax_id.TasaImp == 0:
            return 0.0
        monto = (self.base * (self.tax_id.TasaImp / 100.0))
        self.MontoImp = monto

    def get_tax_monto(self):
        self._compute_tax()
        return int(round(self.MontoImp))
