# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util


class GlobalDescuentoRecargo(object):

    def __init__(self, vals=False):
        util.set_from_keys(self, vals)

    @property
    def NroLinDR(self):
        if not hasattr(self, '_nro_lin_dr'):
            return 1
        return self._nro_lin_dr

    @NroLinDR.setter
    def NroLinDR(self, val):
        self._nro_lin_dr = val

    @property
    def TpoMov(self):
        if not hasattr(self, '_tpo_mov'):
            return 1
        return self._tpo_mov

    @TpoMov.setter
    def TpoMov(self, val):
        self._tpo_mov = val

    @property
    def ValorDR(self):
        if not hasattr(self, '_valor_dr'):
            return 0
        return self._valor_dr

    @ValorDR.setter
    def ValorDR(self, val):
        self._valor_dr = round(float(val), 2)

    @property
    def TpoValor(self):
        if not hasattr(self, '_tpo_valor'):
            return 'D'
        return self._tpo_valor

    @TpoValor.setter
    def TpoValor(self, val):
        self._tpo_valor = val

    @property
    def GlosaDR(self):
        if not hasattr(self, '_glosa_dr'):
            return 1
        return self._glosa_dr

    @GlosaDR.setter
    def GlosaDR(self, val):
        self._glosa_dr = val

    @property
    def monto(self):
        if not hasattr(self, '_monto'):
            return 0
        return self._monto

    @monto.setter
    def monto(self, val):
        self._monto = val

    @property
    def Afectos(self):
        if not hasattr(self, '_afectos'):
            return True
        return self._afectos

    @Afectos.setter
    def Afectos(self, val):
        self._afectos = val

    @property
    def Exentos(self):
        if not hasattr(self, '_exentos'):
            return False
        return self._exentos

    @Exentos.setter
    def Exentos(self, val):
        self._exentos = val

    def get_monto(self, afecto):
        dr = self.ValorDR
        if self.TpoValor in ['%']:
            if afecto == 0.00:
                return 0.00
            if afecto > 0:
                dr = round((afecto * (dr / 100.0)))
        return dr

    def get_monto_exentos(self, afecto):
        dr = self.ValorDR
        if self.TpoValor in ['%']:
            if afecto == 0.00:
                return 0.00
            #exento = 0 #@TODO Descuento Global para exentos
            if afecto > 0:
                dr = round((afecto * (dr / 100.0)))
        return dr
