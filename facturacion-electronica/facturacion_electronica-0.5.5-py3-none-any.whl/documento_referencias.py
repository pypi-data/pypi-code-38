# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util


class Referencia(object):
    def __init__(self, vals):
        util.set_from_keys(self, vals)

    @property
    def CodRef(self):
        if not hasattr(self, '_cod_ref'):
            return 1
        return self._cod_ref

    @CodRef.setter
    def CodRef(self, val):
        '''[
            ('1','Anula Documento de Referencia'),
           ('2','Corrige texto Documento Referencia'),
           ('3','Corrige montos')
        ]'''
        self._cod_ref = val

    @property
    def FchRef(self):
        if not hasattr(self, '_fch_ref'):
            return False
        return self._fch_ref

    @FchRef.setter
    def FchRef(self, val):
        self._fch_ref = val

    @property
    def FolioRef(self):
        if not hasattr(self, '_folio_ref'):
            return False
        return self._folio_ref

    @FolioRef.setter
    def FolioRef(self, val):
        self._folio_ref = val

    @property
    def NroLinRef(self):
        if not hasattr(self, '_nro_lin_ref'):
            return False
        return self._nro_lin_ref

    @NroLinRef.setter
    def NroLinRef(self, val):
        self._nro_lin_ref = val

    @property
    def RazonRef(self):
        if not hasattr(self, '_razon_ref'):
            return False
        return self._razon_ref

    @RazonRef.setter
    def RazonRef(self, val):
        self._razon_ref = val

    @property
    def TpoDocRef(self):
        if not hasattr(self, '_tpo_doc_ref'):
            return False
        return self._tpo_doc_ref

    @TpoDocRef.setter
    def TpoDocRef(self, val):
        self._tpo_doc_ref = val
