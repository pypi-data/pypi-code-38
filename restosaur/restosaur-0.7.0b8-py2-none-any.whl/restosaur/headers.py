

def parse_accept_header(accept):
    result = []
    for media_range in accept.split(","):
        parts = media_range.split(";")
        media_type = parts.pop(0).strip()
        # convert vendor-specific content types into something useful (see
        # docstring)
        typ, subtyp = media_type.split('/')
        # check for a + in the sub-type
        if '+' in subtyp:
            # if it exists, determine if the subtype is a vendor-specific type
            vnd, sep, extra = subtyp.partition('+')
            media_type = '{}/{}'.format(typ, extra)
        else:
            vnd = None
        q = 1.0
        for part in parts:
            (key, value) = part.lstrip().split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "q":
                q = float(value)
        result.append((media_type, vnd, q))
    result.sort(lambda x, y: -cmp(x[2], y[2]))
    return result


def build_content_type_header(content_type, vendor):
    if vendor:
        type_, subtype = content_type.split('/')
        return '%s/%s+%s' % (type_, vendor, subtype)
    else:
        return content_type


def normalize_header_name(header):
    header = header.lower()
    if header.startswith('http_'):
        header = header.replace('http_', '', 1)
    return header.replace('_', '-')
