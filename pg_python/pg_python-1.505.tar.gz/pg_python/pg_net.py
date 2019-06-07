from urllib.parse import urlparse

def get_domain(url):
    parsed_uri = urlparse(url)
    domain = ('{uri.netloc}/'.format(uri=parsed_uri)).strip("/")
    return domain

def get_proper_domain(url):
    d = get_domain(url)
    prefix_remove = ["http://", "https://", "www."]
    for prefix in prefix_remove:
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d