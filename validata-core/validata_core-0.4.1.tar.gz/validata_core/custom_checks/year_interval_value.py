# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
"""
    Year Interval Value check

    Vérifie que l'on a bien une valeur du type "aaaa/aaaa" avec la première année
    inférieure à la seconde ou une année seulement (si le paramètre allow-year-only est activé)

    Messages d'erreur attendus :
    - Si la valeur n'est pas du type ^\\d{4}/\\d{4}$ (ex : "toto")
      - La valeur "toto" n'a pas le format attendu pour une période (AAAA/AAAA).
    - Si les deux années sont identiques (ex : "2017/2017")
      - Période "2017/2017 invalide. Les deux années doivent être différentes).
    - Si la deuxième année est inférieure à la première (ex : "2017/2012")
      - Période "2017/2012" invalide. La deuxième année doit être postérieure à la première (2012/2017).

    Pierre Dittgen, Jailbreak
"""


import re
from goodtables.registry import check
from goodtables.error import Error

YEAR_INTERVAL_RE = re.compile(r'^(\d{4})/(\d{4})$')
YEAR_RE = re.compile(r'^\d{4}$')

# Module API


@check('year-interval-value', type='custom', context='body')
class YearIntervalValue(object):
    """
        Year Interval Value check class
    """
    # Public

    def __init__(self, column, **options):
        self.__column = column
        self.allow_year_only = options.get('allow-year-only') in ('true', 'yes')

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

        # Don't warn on empty values
        if value == '':
            return

        # Checks for interval format
        rm = YEAR_INTERVAL_RE.match(value)
        if not rm:

            # Not an interval, is this a year only?
            if self.allow_year_only:
                ym = YEAR_RE.match(value)

                # No -> add error
                if not ym:
                    return self.err(cell,
                                    "La valeur \"{value}\" n'a pas le format attendu pour une année (AAAA) ou un intervalle d'année (AAAA/AAAA))",
                                    {'value': value})

                # This is a year, cool!
                else:
                    return

            # not a period -> add error
            return self.err(cell,
                            "La valeur \"{value}\" n'a pas le format attendu pour une période (AAAA/AAAA).",
                            {'value': value})

        year1 = int(rm.group(1))
        year2 = int(rm.group(2))
        if year1 == year2:
            return self.err(cell,
                            "Période \"{value}\" invalide. Les deux années doivent être différentes).",
                            {'value': value})

        if year1 > year2:
            return self.err(cell,
                            "Période \"{value}\" invalide. La deuxième année doit être postérieure à la première"
                            + " ({tip}).", {'value': value, 'tip': '{}/{}'.format(year2, year1)})

    def err(self, cell, msg, msg_substitutions):
        """ Create and return formatted error """
        error = Error(
            'year-interval-value',
            cell,
            message=msg,
            message_substitutions=msg_substitutions
        )
        return [error]
