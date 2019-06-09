from . import segment


def generate(s):
    # Split on dots, then use [ and ] to split out indices
    s = s.strip()
    if s.startswith('.'):
        s = s[1:]
    if s.endswith('.'):
        raise ValueError

    for i, part in enumerate(s.split('.')):
        yield from _split_parts(i, part)


def _split_parts(i, part):
    part = part.strip()
    if not part:
        raise ValueError

    head, *rest = part.split('[')

    # If we had e.g. 'xxx()[yyy]()[zzz]()()'
    # Now we have first='xxx()' and rest = 'yyy]()', 'zzz]()()'
    before, head, after = _extract_calls(head)

    if before:
        # A call () is only allowed to start the first segment -
        # for example, an address like a.() is forbidden.
        if i or head:
            raise ValueError
        yield from before

    elif head:
        yield segment.Attribute(head)
        yield from after

    elif i:
        # An index [] is only allowed to start the first segment -
        # for example, an address like a.[2] is forbidden.
        raise ValueError

    for r in rest:
        before, r, after = _extract_calls(r)
        if before:
            # A segment cannot contain a () - they must all be at top level
            raise ValueError

        # A segment must have exactly one ']', exactly at the end.
        index, between = r.split(']', 1)
        if between:
            raise ValueError

        index = int(index) if index.isdigit() else index
        yield segment.Index(index)
        yield from after


def _extract_calls(p):
    # Extract () pairs from start and finish of a string
    before, after = [], []
    while p.startswith('()'):
        before.append(segment.Call())
        p = p[2:]

    while p.endswith('()'):
        after.append(segment.Call())
        p = p[:-2]

    if '(' in p or ')' in p:
        raise ValueError

    return before, p, after
