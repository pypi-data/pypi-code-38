# -*- coding: utf-8 -*-
from collections import namedtuple

def namedtuple_fetchall(cursor):
    """
    Zwraca wszystkie wiersze z kursora jako namedtuple
    """

    description = cursor.description
    result = namedtuple('Result', [col[0] for col in description])
    return [result(*row) for row in cursor.fetchall()]
