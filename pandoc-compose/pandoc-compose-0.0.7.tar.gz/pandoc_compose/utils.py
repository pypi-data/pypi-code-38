def create_pandoc_opt(config):
    key, value = config

    if isinstance(value, list):
        value = " ".join(map(str, sorted(value)))
    if isinstance(value, bool):
        if not value:
            return ""
        value = ""

    if len(key) == 1:
        key = "-{}".format(key)
    else:
        key = "--{}".format(key)

    return "{} {}".format(key, value).strip()