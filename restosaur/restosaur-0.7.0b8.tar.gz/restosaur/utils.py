import six

from . import contentnegotiation


class Collection(object):
    def __init__(
            self, context, iterable, key=None, totalcount=None,
            totalcount_key=None):

        self.totalcount = totalcount or len(iterable)
        self.iterable = iterable
        self.totalcount_key = totalcount_key or 'totalCount'
        self.key = key or 'items'


def join_content_type_with_vnd(content_type, vnd):
    if not vnd:
        return content_type

    x, y = content_type.split('/')
    return '%s/%s+%s' % (x, vnd, y)


def split_mediatype(mt):
    """
    Split media type into (content_type, vnd, params) tuple

    Function converts `type/[tree.]subtype[+suffix][;params]`
    into generic mediatype together with subtype without suffix.
    Extra parameteres are returned as third element of the tuple.
    """

    type_, subtype, args = contentnegotiation.parse_media_type(mt)
    suffix = subtype.split('+')[-1] if '+' in subtype else None

    if suffix and suffix not in (
            'json', 'zip', 'ber', 'der', 'fastinfoset', 'wbxml'):
        raise ValueError('Suffix "%s" is not supported (see: RFC6839)')

    ct = '%s/%s' % (type_, suffix or subtype)
    vnd = subtype.split('+')[0] if suffix else None
    return ct, vnd, args


def generic_mediatype(mt):
    return split_mediatype(mt)[0]


def force_bytes(s, encoding='utf-8', errors='strict'):
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if isinstance(s, memoryview):
        return bytes(s)
    try:
        return s.encode(encoding, errors)
    except AttributeError:
        return str(s).encode(encoding, errors)


def force_text(s, encoding='utf-8', errors='strict'):
    if issubclass(type(s), six.text_type):
        return s
    try:
        if not issubclass(type(s), six.string_types):
            if six.PY3:
                if isinstance(s, bytes):
                    s = six.text_type(s, encoding, errors)
                else:
                    s = six.text_type(s)
            elif hasattr(s, '__unicode__'):
                s = six.text_type(s)
            else:
                s = six.text_type(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join(force_text(arg, encoding, errors) for arg in s)
    return s


def get_types_to_check(cls):
    if cls is None:
        return [None]
    else:
        return type.mro(cls)
