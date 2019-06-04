def xstr(s):
    if s is None:
        return ''
    return str(s)


def convert_boolean_to_yes_or_no(boolean):
    if boolean:
        return "Yes"
    else:
        return "No"


def strftime_if_not_none(variable):
    if variable is not None:
        return variable.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None