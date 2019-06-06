import re


def to_re(m):
    if m.group(0) == '*':
        return '.*'
    elif m.group(0) == '?':
        return '.'
    else:
        return re.escape(m.group(0))


class TagPattern(object):
    def __init__(self, raw):
        self.raw = raw

        as_re = re.sub(r'\*|\?|[^*?]*', to_re, raw) + '$'
        self.compiled = re.compile(as_re)

    def __eq__(self, other):
        return self.raw == other.raw

    def __hash__(self):
        return hash(self.raw)

    def matches(self, tag):
        return self.compiled.match(tag) is not None

    def __repr__(self):
        return 'TagPattern({!r})'.format(self.raw)


if __name__ == '__main__':
    tp = TagPattern('latest')
    assert not tp.matches('late')
    assert tp.matches('latest')
    tp = TagPattern('?atest')
    assert tp.matches('latest')
    assert not tp.matches('llatest')
    tp = TagPattern('?ate*')
    assert tp.matches('latest')
    assert tp.matches('latester')
    assert not tp.matches('')

    s = {TagPattern(x) for x in ['latest', 'lat*', 'latest']}
    assert len(s) == 2
