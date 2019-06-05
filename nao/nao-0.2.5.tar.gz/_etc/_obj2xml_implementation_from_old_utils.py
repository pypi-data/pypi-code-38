






def obj2xml(obj, level=1):
    """
    recursively transform an object structure to an
    XML structure to be able to view

    to_yaml is more sane!!!
    but need serialization rule for 
    non-standard python objects!
    """
    if isinstance(obj, list):

        return '\n'.join([obj2xml(i, level+1) for i in obj])

    ats = []
    for a in obj.__dict__:
        if not a.startswith('_'):
            val = getattr(obj, a)
            ats.append('{}<attr name="{}">{}{}</attr>'.format(
                "\t"*level,
                a, 
                obj2xml(val, level+1) if isinstance(val, list) else val,
                '\n'+"\t"*level if isinstance(val, list) else '',
            ))

    return '\n{}<obj type="{}">\n{}\n{}</obj>'.format(
        "\t"*(level-1),
        type(obj),
        '\n'.join(ats),
        "\t"*(level-1),
    )





