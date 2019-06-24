# -*- coding: utf-8 -*-
import locale


def format_quantity(quantity):
    """
        format the quantity
    """
    if quantity is not None:
        result = locale.format('%g', quantity, grouping=True)
        if isinstance(result, str):
            result = result.decode('utf-8')
        return result
    else:
        return ""
