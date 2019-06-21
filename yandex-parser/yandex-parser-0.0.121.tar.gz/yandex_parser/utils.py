# -*- coding:utf-8 -*-
import re
import unicodedata
from urllib import quote, unquote
from urlparse import urlparse, urlunsplit, urlsplit


def to_unicode(content, from_charset=None):
    u"""Безопасное приведение к юникоду

    :type  content: str
    :param content: текст
    :type  from_charset: str
    :param from_charset: Кодировка исходного текста

    :rtype: unicode
    :returns: текст, преобразованный в юникод
    """
    if type(content) == unicode:
        return content

    charsets = {
        'utf-8' : 'utf8',
        'utf8' : 'utf8',
        'cp1251' : 'cp1251',
        'cp-1251' : 'cp1251',
        'windows-1251' : 'cp1251',
        'win-1251' : 'cp1251',
        '1251' : 'cp1251',
        'русdows-1251': 'cp1251',
        'koi8-r' : 'koi8-r'
    }
    if type(from_charset) in (str, unicode):
        from_charset = str(from_charset.lower())

    try:
        from_charset = charsets[from_charset]
        return unicode(content, encoding=from_charset)

    except KeyError:
        for from_charset in ('utf8', 'cp1251', 'koi8-r', None):
            try:
                if from_charset is not None:
                    return unicode(content, encoding=from_charset)
                else:
                    return unicode(content)
            except UnicodeError:
                continue

        raise UnicodeError('Can not be converted to Unicode')

    except UnicodeError:
        return unicode(content, encoding=from_charset, errors='ignore')
    
def get_full_domain_without_scheme(url):
    absolute_url = normalize(url).replace('//www.', '//')
    parsed = urlparse(absolute_url)
    return urlunsplit(('', parsed.netloc, '', '', '')).replace('//', '')
    
        
def normalize(url, charset='utf-8'):
    def _clean(string):
        string = unicode(unquote(string), 'utf-8', 'replace')
        return unicodedata.normalize('NFC', string).encode('utf-8')

    default_port = {
        'ftp': 21,
        'telnet': 23,
        'http': 80,
        'gopher': 70,
        'news': 119,
        'nntp': 119,
        'prospero': 191,
        'https': 443,
        'snews': 563,
        'snntp': 563,
    }

    if isinstance(url, unicode):
        url = url.encode(charset, 'ignore')

    if url[0] not in ['/', '-'] and ':' not in url[:7]:
        url = 'http://' + url

    url = url.replace('#!', '?_escaped_fragment_=')

    scheme, auth, path, query, fragment = urlsplit(url.strip())
    (userinfo, host, port) = re.search('([^@]*@)?([^:]*):?(.*)', auth).groups()

    scheme = scheme.lower()

    host = host.lower()
    if host and host[-1] == '.':
        host = host[:-1]
        # take care about IDN domains
    try:
        host = host.decode(charset).encode('idna')  # IDN -> ACE
    except Exception:
        host = host.decode(charset)

    path = quote(_clean(path), "~:/?#[]@!$&'()*+,;=")
    fragment = quote(_clean(fragment), "~")

    query = "&".join(["=".join([quote(_clean(t), "~:/?#[]@!$'()*+,;=") for t in q.split("=", 1)]) for q in query.split("&")])

    if scheme in ["", "http", "https", "ftp", "file"]:
        output = []
        for part in path.split('/'):
            if part == "":
                if not output:
                    output.append(part)
            elif part == ".":
                pass
            elif part == "..":
                if len(output) > 1:
                    output.pop()
            else:
                output.append(part)
        if part in ["", ".", ".."]:
            output.append("")
        path = '/'.join(output)

    if userinfo in ["@", ":@"]:
        userinfo = ""

    if path == "" and scheme in ["http", "https", "ftp", "file"]:
        path = "/"

    if port and scheme in default_port.keys():
        if port.isdigit():
            port = str(int(port))
            if int(port) == default_port[scheme]:
                port = ''

    auth = (userinfo or "") + host
    if port:
        auth += ":" + port
    if url.endswith("#") and query == "" and fragment == "":
        path += "#"
    return urlunsplit((scheme, auth, path, query, fragment))