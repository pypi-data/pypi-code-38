import inspect


def check(kwds, name):
    if kwds:
        msg = ', '.join('"%s"' % s for s in sorted(kwds))
        s = '' if len(kwds) == 1 else 's'
        raise ValueError('Unknown attribute%s for %s: %s' % (s, name, msg))


def set_reserved(value, section, name=None, data=None, **kwds):
    check(kwds, '%s %s' % (section, value.__class__.__name__))
    value.name = name
    value.data = data


ERROR = '{message} in {label} {function.__name__}{signature}: {error}'


def _check(message, function, *args, **kwds):
    def fail(error, *args):
        error = error % args
        if isinstance(function, type):
            label = 'class constructor'
        else:
            label = 'function call'

        label = 'class' if isinstance(function, type) else 'function'
        signature = str(inspect.signature(function))
        raise ValueError(ERROR.format(locals()))

    parameters = inspect.signature(function).parameters.values()

    # Parameters appear in this order:
    # required, positional_or_keyword, keyword_only

    required = len(parameters)
    for i, p in enumerate(parameters):
        if p.kind == p.KEYWORD_ONLY or p.default != p.empty:
            required = i
            break

    if len(args) < required:
        fail('Not enough positional arguments: %d < %d', len(args), required)

    keyword_only = len(parameters)
    for i, p in enumerate(parameters):
        if p.kind == p.KEYWORD_ONLY:
            keyword_only = i
            break

    if len(args) > keyword_only:
        fail('Too many positional arguments: %d > %d', len(args), keyword_only)

    # All the keyword-only arguments need to be in kwds
    missing = set(p.name for p in parameters[keyword_only:]) - set(kwds)
    if missing:
        fail(
            'Missing required keyword arguments: %s', ' '.join(sorted(missing))
        )

    unknown = set(kwds) - set(p.name for p in parameters[required:])
    if unknown:
        fail('Do not understand these keywords: %s', ' '.join(sorted(unknown)))
