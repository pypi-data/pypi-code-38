import re


_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


def redact_uri(uri, redact=True):
	return _safe_uri_replace.sub(r'\1://\2@', uri) if '@' in uri and redact else uri
