# -*- coding: utf-8 -*-
from facturacion_electronica.impuestos import Impuestos
from facturacion_electronica import clase_util as util


class LineaDetalle(object):

    def __init__(self, vals, currency=None, valor_iva=19, NroLinDet=1):
        self._valor_iva = valor_iva
        util.set_from_keys(self, vals)
        if not vals.get('Impuesto'):
            self._impuestos = [Impuestos({})]
        self.uom_id = vals.get('UnmdItem', 'Unid')
        self._compute_price()

    @property
    def CdgItem(self):
        if not hasattr(self, '_cdgs'):
            return []
        return self._cdgs

    @CdgItem.setter
    def CdgItem(self, cdgs):
        if not hasattr(self, '_cdgs'):
            self._cdgs = []
        if type(cdgs) is dict:
            self._cdgs.append(cdgs)
        else:
            for cdg in cdgs:
                self._cdgs.append(cdg)

    @property
    def DscItem(self):
        if not hasattr(self, '_dsc_item'):
            return False
        return self._dsc_item

    @DscItem.setter
    def DscItem(self, val):
        self._dsc_item = val
        if val and val != self.name:
            self.name = util._acortar_str(val, 1000)

    @property
    def DescuentoMonto(self):
        if not hasattr(self, '_descuento_monto'):
            return 0.0
        return self._descuento_monto

    @DescuentoMonto.setter
    def DescuentoMonto(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._descuento_monto = int(round(float(val), 0))

    @property
    def DescuentoPct(self):
        if not hasattr(self, '_descuento_pct'):
            return 0.0
        return self._descuento_pct

    @DescuentoPct.setter
    def DescuentoPct(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._descuento_pct = round(float(val), 4)

    @property
    def IndExe(self):
        if not hasattr(self, '_ind_exe'):
            return False
        return self._ind_exe

    @IndExe.setter
    def IndExe(self, val):
        self._ind_exe = val

    @property
    def Impuesto(self):
        if not hasattr(self, '_impuestos'):
            return []
        return self._impuestos

    @Impuesto.setter
    def Impuesto(self, vals):
        if self.IndExe:
            return False
        if not vals:
            return vals
        self._impuestos = []
        for tax in vals:
            if not tax.get('CodImp') or tax['CodImp'] in [14, 15]:
                tax['TasaImp'] = self._valor_iva
            if not tax.get('CodImp') and tax['TasaImp'] == self._valor_iva:
                tax['CodImp'] = 14
            impuesto = Impuestos(tax)
            self._impuestos.append(impuesto)
        self._compute_price()

    @property
    def MontoItem(self):
        if not hasattr(self, '_monto_item'):
            return 0
        return self._monto_item

    @MontoItem.setter
    def MontoItem(self, val):
        if type(val) is str:
            val = val.replace(',', '.')
        self._monto_item = int(round(float(val)))

    @property
    def MntBruto(self):
        if not hasattr(self, '_mnt_bruto'):
            return False
        return self._mnt_bruto

    @MntBruto.setter
    def MntBruto(self, val):
        self._mnt_bruto = val

    @property
    def NmbItem(self):
        if not hasattr(self, '_name'):
            dsc = self.DscItem
            return dsc
        return self._name

    @NmbItem.setter
    def NmbItem(self, val):
        self._name = util._acortar_str(val, 80)

    @property
    def NroLinDet(self):
        if not hasattr(self, '_nro_lin_det'):
            return 1
        return self._nro_lin_det

    @NroLinDet.setter
    def NroLinDet(self, val):
        self._nro_lin_det = int(val)

    @property
    def PrcItem(self):
        if not hasattr(self, '_prc_item'):
            return False
        return self._prc_item

    @PrcItem.setter
    def PrcItem(self, val):
        prc_item = val
        if type(val) is str:
            prc_item = val.replace(',', '.')
        self._prc_item = round(float(prc_item), 4)

    @property
    def QtyItem(self):
        if not hasattr(self, '_qty_item'):
            return 0
        return self._qty_item

    @QtyItem.setter
    def QtyItem(self, val):
        qty_item = val
        if type(val) is str:
            qty_item = val.replace(',', '.')
        self._qty_item = round(float(qty_item), 4)

    def _compute_price(self):
        total = self.QtyItem * self.PrcItem
        if self.DescuentoPct > 0:
            self.DescuentoMonto = (total * ((self.DescuentoPct or 0.0) / 100.0))
        if self.DescuentoMonto > 0:
            total -= self.DescuentoMonto
        self.MontoItem = total
