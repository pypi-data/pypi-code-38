def list_handler(VALUE, PARENT_PATH):
    for idx in range(len(VALUE)):
        value = VALUE[idx]
        if isinstance(value, dict):
            dict_handler(value, "{KEY}[{IDX}]".format(
                KEY=PARENT_PATH, IDX=idx))
        elif isinstance(value, list):
            list_handler(value, "{KEY}[{IDX}]".format(
                KEY=PARENT_PATH, IDX=idx))
        elif isinstance(value, str):
            print('.{KEY}[{IDX}] = "{VALUE}"'.format(
                KEY=PARENT_PATH, IDX=idx, VALUE=value))
        else:
            print(".{KEY}[{IDX}] = {VALUE}".format(
                KEY=PARENT_PATH, IDX=idx, VALUE=value))


def dict_handler(VALUE, PARENT_PATH):
    for key in VALUE:
        value = VALUE.get(key)
        if isinstance(value, dict):
            dict_handler(value, PARENT_PATH + "." + key)
        elif isinstance(value, list):
            list_handler(value, PARENT_PATH + "." + key)
        elif isinstance(value, str):
            print('.{PARENT_PATH}.{KEY} = "{VALUE}"'.format(
                PARENT_PATH=PARENT_PATH, KEY=key, VALUE=value))
        else:
            print(".{PARENT_PATH}.{KEY} = {VALUE}".format(
                PARENT_PATH=PARENT_PATH, KEY=key, VALUE=value))


def jcat(JSON):
    for key in JSON:
        value = JSON.get(key)
        if isinstance(value, dict):
            dict_handler(value, key)
        elif isinstance(value, list):
            list_handler(value, key)
        elif isinstance(value, str):
            print('.{KEY} = "{VALUE}"'.format(KEY=key, VALUE=value))
        else:
            print(".{KEY} = {VALUE}".format(KEY=key, VALUE=value))
