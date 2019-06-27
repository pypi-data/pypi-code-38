# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
"""
    Cohesive columns value check

    Vérifie que pour une liste de colonnes donnée, toutes les colonnes ont une valeur ou aucune des colonnes n'a
    une valeur

    Paramètres :
    - column : la première colonne
    - othercolumns : les autres colonnes qui doivent être remplies (ou non)

    Messages d'erreur attendus :
    - Colonne(s) non trouvée(s) : {liste de noms de colonnes non trouvées}
    - Les colonnes {liste des noms de colonnes} doivent toutes comporter une valeur ou toutes être vides

    Pierre Dittgen, Jailbreak
"""


import re
from simpleeval import simple_eval
from goodtables.registry import check
from goodtables.error import Error

# Module API


@check('cohesive-columns-value', type='custom', context='body')
class CohesiveColumnsValue(object):
    """
        Cohesive columns value check class
    """
    # Public

    def __init__(self, column, **options):
        """ Gets and store column names to check """

        self.column = column
        column_names = [column]
        column_names.extend(options['othercolumns'])
        self.column_names = column_names
        self.column_nb = len(self.column_names)

    @staticmethod
    def valued(val):
        return val != ''

    def check_row(self, cells):
        cell = None

        # Gets column values
        values_dict = {}
        for item in cells:
            if item['header'] in self.column_names:
                values_dict[item['header']] = item['value']
                if item['header'] == self.column:
                    cell = item

        # Main column
        if cell is None:
            return

        # Missing columns
        if len(values_dict) != self.column_nb:
            missing_columns = [name for name in self.column_names if not name in values_dict]
            return self.err(cell,
                            "Colonne(s) non trouvée(s) : {}".format(', '.join(missing_columns)),
                            {'code': 'missing-columns', 'missing-columns': missing_columns})

        # test if all columns are valued or all columns are empty
        if not all(CohesiveColumnsValue.valued(v) for _, v in values_dict.items()) \
                and not all(not CohesiveColumnsValue.valued(v) for _, v in values_dict.items()):
            return self.err(cell,
                            "Les colonnes {} doivent toutes comporter une valeur ou toutes être vides"
                            .format(", ".join(self.column_names)),
                            {'code': 'empty-valued-col-mix', 'columns': self.column_names})

    def err(self, cell, msg, msg_substitutions):
        """ Create and return formatted error """
        error = Error(
            'cohesive-columns-value',
            cell,
            message=msg,
            message_substitutions=msg_substitutions
        )
        return [error]
