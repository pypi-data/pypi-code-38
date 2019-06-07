

def arg_build(var_name, var_type, required, requires_value, allowed_values, description=None):


    if not isinstance(var_name, str):
        print("invalid type for parameter name")
        return

    if not isinstance(var_name, str):
        print("invalide type for parameter type")
        return

    if not isinstance(required, bool):
        print('invalid type for parameter required')
        return

    if not isinstance(requires_value, bool):
        print('invalide type for parameter required value')
        return

    if not isinstance(allowed_values, list):
        print("inavlid type for parameter allowed values")
        return


    obj = {
        "name"              : var_name,
        "type"              : var_type,
        "Required"          : required,
        "requires_value"    : requires_value,
        "allowed_values"    : allowed_values,
    }

    if description != None:
        obj['description'] = description

    return obj
