def is_float(x):
    try:
        if isinstance(x, int) or isinstance(x, float) or isinstance(x, str):
            a = float(x)
        else:
            return False
    except ValueError:
        return False
    else:
        return True


def is_int(x):
    try:
        if isinstance(x, int) or isinstance(x, float) or isinstance(x, str):
            a = float(x)
            b = int(a)
        else:
            return False
    except ValueError:
        return False
    else:
        return a == b


def is_valid_operand(operand, variables):
    operand = operand.strip()
    return is_float(operand) or is_int(operand) or len(operand) == 0 or (
        variables is not None and operand in variables)
