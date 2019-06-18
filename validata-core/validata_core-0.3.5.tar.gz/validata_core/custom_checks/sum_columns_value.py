# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
"""
    Sum columns value check

    Pour une colonne donnée (column) et une liste de colonnes (columns), on vérifie que la première colonne
    contient bien la somme des valeurs entières des autres colonnes

    La vérification ne s'effectue pas si l'ensemble des colonnes est vide

    Paramètres :
    - column : le nom de la première colonne contenant la somme
    - columns : le nom des colonnes contenant les valeurs à ajouter

    Messages d'erreur attendus :
    - La valeur de la colonne {col} [val] n'est pas entière, il n'est pas possible de vérifier que {col} = {col1} + {col2} + ...
    - La valeur des colonnes {col1}, {col2}, ... ne sont pas entières, il n'est pas possible de vérifier que {col} = {col1} + {col2} + ...
    - La somme des valeurs des colonnes {col1}, {col2}, ... est {sum}, ce nombre est différent de celui attendu dans {col} [val]

    Pierre Dittgen, Jailbreak
"""
from collections import OrderedDict
import re
from simpleeval import simple_eval
from goodtables.registry import check
from goodtables.error import Error

# Module API

INT_RE = re.compile(r'^\d+$')


@check('sum-columns-value', type='custom', context='body')
class SumColumnsValue(object):
    """
        Sum columns value check class
    """
    # Public

    def __init__(self, column, **options):
        """ Gets and store column names to check """

        self.column = column
        self.columns = options['columns']

    @staticmethod
    def valued(val):
        """ Return True if the given string value is not empty """
        return val != ''

    @staticmethod
    def is_int(str_value):
        """ Return True if the given string contains an integer """
        return INT_RE.match(str_value)

    def check_row(self, cells):
        """ Main method """
        cell = None

        # Gets column values
        dict_values = OrderedDict()
        for item in cells:
            if item['header'] == self.column:
                cell = item
                dict_values[item['header']] = item['value']
            elif item['header'] in self.columns:
                dict_values[item['header']] = item['value']

        # If the main column doesn't exist
        if cell is None:
            return

        #  If one of the columns doesn't exist
        if len(dict_values) < (len(self.columns) + 1):
            return

        # If one of the columns is not valued
        if not all((SumColumnsValue.valued(val) for val in dict_values.values())):
            return

        # Checks that all values are integer
        cols_val_int = ((header, val, SumColumnsValue.is_int(val)) for header, val in dict_values.items())
        bad_col_vals = list(map(lambda t: (t[0], t[1]), filter(lambda t: not t[2], cols_val_int)))
        if bad_col_vals:
            sum_str = '{} = {}'.format(self.column, ' + '.join(self.columns))
            if len(bad_col_vals) == 1:
                msg = "La valeur de la colonne {colname}[{val}] n'est pas entière,"
                msg += " il n'est pas possible de vérifier que {sum}"
                params = {'colname': bad_col_vals[0][0], 'val': bad_col_vals[0][1], 'sum': sum_str}
                return self.err(cell, msg.format(**params), params)
            else:
                msg = "La valeur des colonnes {column_list} n'est pas entière,"
                msg += " il n'est pas possible de vérifier que {sum}"
                params = {'column_list': ', '.join(colname for colname, _ in bad_col_vals), 'sum': sum_str}
                return self.err(cell, msg.format(**params), params)

        # Check sum
        computed_sum = sum([int(val) for col, val in dict_values.items() if col != self.column])
        column_sum = int(dict_values[self.column])
        if computed_sum != column_sum:
            msg = "La somme des valeurs des colonnes {column_value_list} est {computed_sum},"
            msg += " ce nombre est différent de celui attendu dans {column} [{column_sum}]"
            items_wo_column = (item for item in dict_values.items() if item[0] != self.column)
            params = {'column_value_list': ', '.join("{} [{}]".format(*item) for item in items_wo_column),
                      'computed_sum': computed_sum, 'column': self.column, 'column_sum': column_sum}
            return self.err(cell, msg.format(**params), params)

    def err(self, cell, msg, msg_substitutions):
        """ Create and return formatted error """
        error = Error(
            'compare-columns-value',
            cell,
            message=msg,
            message_substitutions=msg_substitutions
        )
        return [error]
