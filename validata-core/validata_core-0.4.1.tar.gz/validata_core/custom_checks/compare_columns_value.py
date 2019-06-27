# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
"""
    Compare columns value check

    Pour deux colonnes données, si les deux comportent une valeur, vérifie que la valeur de la première est :
    - supérieure (>)
    - supérieure ou égale (>=)
    - égale (==)
    - inférieure ou égale (<=)
    - inférieure (<)
    à la valeur de la deuxième colonne

    Si les deux valeurs sont numériques, c'est une comparaison numérique qui est utilisée.
    Si les deux valeurs ne sont pas numériques, c'est une comparaison lexicographique qui est utilisée.
    Si une valeur est numérique et l'autre lexicographique, une erreur est relevée.

    Paramètres :
    - column : le nom de la première colonne
    - column2 : le nom de la deuxième colonne
    - op : l'opérateur de comparaison (">", ">=", "==", "<=" ou "<")

    Messages d'erreur attendus :
    - Opérateur [??] invalide
    - La valeur de la colonne {col1} [{val1}] n'est pas comparable avec la valeur de la colonne {col2} [{val2}]
    - La valeur de la colonne {col1} [{val1}] devrait être {opérateur} à la valeur de la colonne {col2} [{val2}]

    Pierre Dittgen, Jailbreak
"""

from goodtables.registry import check
from goodtables.error import Error

# Module API

OP_LABELS = {
    '>': 'supérieure',
    '>=': 'supérieure ou égale',
    '==': 'égale',
    '<=': 'inférieure ou égale',
    '<': 'inférieure',
}


@check('compare-columns-value', type='custom', context='body')
class CompareColumnsValue(object):
    """Compare columns value check class"""
    # Public

    def __init__(self, column, **options):
        """Gets and store column names to check"""

        self.column = column
        self.column2 = options['column2']
        self.op = options['op']

    @staticmethod
    def valued(val):
        return val != ''

    def check_row(self, cells):
        cell = None
        value1 = None
        value2 = None

        # Gets column values
        for item in cells:
            if item['header'] == self.column:
                cell = item
                value1 = item['value']
            elif item['header'] == self.column2:
                value2 = item['value']

        # 1 column doesn't exist
        if value1 is None or value2 is None:
            return

        # one of the columns is not valued
        if not CompareColumnsValue.valued(value1) or not CompareColumnsValue.valued(value2):
            return

        # Op validity
        if not self.op in OP_LABELS:
            return self.err(cell,
                            'Opérateur `{}` invalide'.format(self.op), {'operator': self.op})

        # Compare
        comparison_str = CompareColumnsValue.compute_comparison_str(value1, self.op, value2)
        if comparison_str is None:
            return self.err(cell,
                            "La valeur de la colonne {} `{}` n'est pas comparable avec la valeur de la colonne {} `{}`"
                            .format(self.column, value1, self.column2, value2),
                            {'column1': self.column, 'value1': value1, 'column2': self.column2, 'value2': value2})

        compare_result = eval(comparison_str)
        if not compare_result:
            return self.err(cell,
                            "La valeur de la colonne {} `{}` devrait être {} à la valeur de la colonne {} `{}`"
                            .format(self.column, value1, OP_LABELS[self.op], self.column2, value2),
                            {'column1': self.column, 'value1': value1, 'column2': self.column2, 'value2': value2, 'op': OP_LABELS[self.op]})

    @staticmethod
    def compute_comparison_str(value1, op, value2):
        """ Computes comparison_str """

        # number vs number
        if value1.isnumeric() and value2.isnumeric():
            return '{} {} {}'.format(value1, op, value2)

        # string vs string
        if not value1.isnumeric() and not value2.isnumeric():
            n_value1 = value1.replace('"', '\\"')
            n_value2 = value2.replace('"', '\\"')
            return '"{}" {} "{}"'.format(n_value1, op, n_value2)

        # potato vs cabbage?
        return None

    def err(self, cell, msg, msg_substitutions):
        """ Create and return formatted error """
        error = Error(
            'compare-columns-value',
            cell,
            message=msg,
            message_substitutions=msg_substitutions
        )
        return [error]
