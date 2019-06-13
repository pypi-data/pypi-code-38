

def do(
    stringified_response: str,
    cut_limit: int = 4000,
    cut_line: str = '<...>'
):
    try:
        half_cut_limit = abs(int(cut_limit / 2))
    except TypeError:
        half_cut_limit = 2000
    was_cut = False
    stringified_response_len = len(stringified_response)
    if stringified_response_len > half_cut_limit * 2:
        was_cut = True
        stringified_response = '"{head}\\n{cut}\\n{tail}"'.format(**{
            'head': stringified_response[:half_cut_limit],
            'cut': cut_line.format(**{
                'cut_limit': cut_limit,
                'ttl_len': stringified_response_len
            }),
            'tail': stringified_response[-half_cut_limit:],
        })

    return stringified_response, stringified_response_len, was_cut
