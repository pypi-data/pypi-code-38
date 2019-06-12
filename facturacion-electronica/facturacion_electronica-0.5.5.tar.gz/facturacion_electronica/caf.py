# -*- coding: utf-8 -*-
import base64
from lxml import etree


class UserError(Exception):
    """Clase perdida"""
    pass


class Warning(Exception):
    """Clase perdida"""
    pass


class Caf(object):

    def __init__(self, cafList):
        """Recibe lista de caf strings en base64,
        decodifica y guarda."""
        self.decodedCafs = []
        for caf in cafList:
            decodedCaf = base64.b64decode(caf).decode()
            self.decodedCafs.append(decodedCaf)

    def get_caf_file(self, folio, TipoDTE):
        """Esta función es llamada desde dte"""
        if not self.decodedCafs:
            raise UserError('There is no CAF file available or in use ' +
                            'for this Document. Please enable one.')
        for decodedCaf in self.decodedCafs:
            post = etree.XML(decodedCaf)
            folio_inicial = post.find('CAF/DA/RNG/D').text
            folio_final = post.find('CAF/DA/RNG/H').text
            if folio in range(int(folio_inicial), (int(folio_final)+1)):
                return post
        if folio > int(folio_final):
            msg = '''El folio de este documento: {} está fuera de rango \
del CAF vigente (desde {} hasta {}). Solicite un nuevo CAF en el sitio \
www.sii.cl'''.format(folio, folio_inicial, folio_final)
            raise UserError(msg)
        raise UserError('No Existe Caf para %s folio %s' % (TipoDTE, folio))
