# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util


class Emisor(object):

    def __init__(self, vals):
        util.set_from_keys(self, vals)

    @property
    def Actecos(self):
        if not hasattr(self, '_actecos'):
            return []
        return self._actecos

    @Actecos.setter
    def Actecos(self, val):
        self._actecos = val

    @property
    def CdgSIISucur(self):
        if not hasattr(self, '_cdg_sii_sucur'):
            return False
        return self._cdg_sii_sucur

    @CdgSIISucur.setter
    def CdgSIISucur(self, val):
        self._cdg_sii_sucur = val

    @property
    def CiudadOrigen(self):
        if not hasattr(self, '_ciudad_origen'):
            return False
        return self._ciudad_origen

    @CiudadOrigen.setter
    def CiudadOrigen(self, val):
        self._ciudad_origen = val

    @property
    def CmnaOrigen(self):
        if not hasattr(self, '_cmna_origen'):
            return False
        return self._cmna_origen

    @CmnaOrigen.setter
    def CmnaOrigen(self, val):
        self._cmna_origen = val

    @property
    def CorreoEmisor(self):
        if not hasattr(self, '_correo_emisor'):
            return False
        return self._correo_emisor

    @CorreoEmisor.setter
    def CorreoEmisor(self, val):
        self._correo_emisor = val

    @property
    def DirOrigen(self):
        if not hasattr(self, '_dir_origen'):
            return False
        return self._dir_origen

    @DirOrigen.setter
    def DirOrigen(self, val):
        self._dir_origen = val

    @property
    def FchResol(self):
        if not hasattr(self, '_fch_resol'):
            return False
        return self._fch_resol

    @FchResol.setter
    def FchResol(self, val):
        self._fch_resol = val

    @property
    def GiroEmis(self):
        if not hasattr(self, '_giro_emisor'):
            return False
        return self._giro_emisor

    @GiroEmis.setter
    def GiroEmis(self, val):
        self._giro_emisor = val

    @property
    def Modo(self):
        if not hasattr(self, '._modo'):
            return 'certificacion'
        return self._modo

    @Modo.setter
    def Modo(self, val):
        self._modo = val

    @property
    def NroResol(self):
        if not hasattr(self, '_nro_resol'):
            return 0
        return self._nro_resol

    @NroResol.setter
    def NroResol(self, val):
        self._nro_resol = val

    @property
    def RUTEmisor(self):
        if not hasattr(self, '_rut_emisor'):
            return False
        return self._rut_emisor

    @RUTEmisor.setter
    def RUTEmisor(self, val):
        self._rut_emisor = val

    @property
    def RznSoc(self):
        if not hasattr(self, '_rzn_soc'):
            return False
        return self._rzn_soc

    @RznSoc.setter
    def RznSoc(self, val):
        self._rzn_soc = val

    @property
    def Sucursal(self):
        if not hasattr(self, '_sucursal'):
            return False
        return self._sucursal

    @Sucursal.setter
    def Sucursal(self, val):
        self._sucur = val

    @property
    def Telefono(self):
        if not hasattr(self, '_telefono'):
            return False
        return self._telefono

    @Telefono.setter
    def Telefono(self, val):
        self._telefono = val

    @property
    def ValorIva(self):
        if not hasattr(self, '_valor_iva'):
            return 19
        return self._valor_iva

    @ValorIva.setter
    def ValorIva(self, val):
        self._valor_iva = val

    @property
    def Website(self):
        if not hasattr(self, '_website'):
            return 'localhost'
        return self._website

    @Website.setter
    def Website(self, val):
        self._website = val
