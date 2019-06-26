from re import findall, sub

def remove_url_parameters(url):
    """Removes {parameter} from URL and returns the URL without the parameters

    :param url: A URL
    :return: URL without parameters
    """
    return sub(r'{[a-z-A-Z0-9\-]+}/?', '', url)


def extract_url_parameters(url):
    """Extracts {parameter} from URL and returns the parameters

    :param url: A URL
    :return: Names of all URL based parameters
    """
    return findall(r'\{([a-zA-Z0-9\-_]+)\}', url)
