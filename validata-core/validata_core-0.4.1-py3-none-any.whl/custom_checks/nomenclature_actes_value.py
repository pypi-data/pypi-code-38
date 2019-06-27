# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
import unicodedata

"""
    Comme indiqué par Loïc Haÿ dans son mail du 5/7/2018

> Document de référence dans les spécifications SCDL : http://www.moselle.gouv.fr/content/download/1107/7994/file/nomenclature.pdf
>
> Dans la nomenclature Actes, les valeurs avant le "/" sont :
>
> Commande publique
> Urbanisme
> Domaine et patrimoine
> Fonction publique
> Institutions et vie politique
> Libertés publiques et pouvoirs de police
> Finances locales
> Domaines de compétences par thèmes
> Autres domaines de compétences
>
> Le custom check devra accepter minuscules et majuscules, accents et sans accents ...

    Pierre Dittgen, JailBreak
"""

from simpleeval import simple_eval
import stdnum.fr.siret
from goodtables.registry import check
from goodtables.error import Error


# Module API

AUTHORIZED_VALUES = [
    "Commande publique",
    "Urbanisme",
    "Domaine et patrimoine",
    "Fonction publique",
    "Institutions et vie politique",
    "Libertés publiques et pouvoirs de police",
    "Finances locales",
    "Domaines de compétences par thèmes",
    "Autres domaines de compétences",
]


@check('nomenclature-actes-value', type='custom', context='body')
class NomenclatureActesValue(object):

    # Public

    def __init__(self, column, **options):
        self.__column = column

        # Inits allowed values
        self.nomenclatures = set(map(NomenclatureActesValue.norm_str, AUTHORIZED_VALUES))

    @staticmethod
    def norm_str(s):
        """ Normalize string, i.e. removing accents and turning into lowercases """
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower())
                       if unicodedata.category(c) != 'Mn')

    def check_row(self, cells):
        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['column-number'], item['header']]:
                cell = item
                break

        # Check cell
        if not cell:
            return

        # Check value
        value = cell.get('value')
        if not value:
            return

        if not '/' in value:
            return self.err(cell, "La valeur \"{value}\" ne contient pas de caractère oblique (/)", {'value': value})

        nomenc = value[:value.find('/')]
        if NomenclatureActesValue.norm_str(nomenc) not in self.nomenclatures:
            return self.err(cell, "Le préfixe de nomenclature Actes \"{}\" n'est pas reconnu".format(nomenc),
                            {'prefix': nomenc})

    def err(self, cell, msg, msg_substitutions):
        """ Create and return formatted error """
        error = Error(
            'delib-matiere-value',
            cell,
            message=msg,
            message_substitutions=msg_substitutions
        )
        return [error]
