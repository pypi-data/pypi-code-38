class MultiValueDict(dict):
    """Very simple multi-value dictionary meant to be function-compatible with flask/werkzeug's MultiDict and Django's
    MultiValueDict for the tcell_agent.   A wrapper around dict to ensure all values are lists.
    """

    def __init__(self, key_list_dict=None, ):
        if isinstance(key_list_dict, dict):
            tmp = {}
            for key, value in key_list_dict.items():
                # for key, value in iteritems(key_list_dict):
                if isinstance(value, (tuple, list)):
                    if len(value) == 0:
                        continue
                    value = list(value)
                else:
                    value = [value]
                tmp[key] = value
            dict.__init__(self, tmp)
        else:
            tmp = {}
            for key, value in key_list_dict or ():
                tmp.setdefault(key, []).append(value)
            dict.__init__(self, tmp)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, [value])

    def getlist(self, key):
        if not dict.__contains__(self, key):
            return []
        return dict.__getitem__(self, key)

    def add(self, key, value):
        dict.setdefault(self, key, []).append(value)
