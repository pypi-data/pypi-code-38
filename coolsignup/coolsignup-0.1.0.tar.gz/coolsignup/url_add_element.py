def url_add_element(url, element):
    if not url:
        return element
    last_char = url[-1]
    if last_char == '/' or last_char == '=':
        return url + element
    else:
        return url + '/' + element
