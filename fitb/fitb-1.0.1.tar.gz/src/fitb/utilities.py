def build_default_config(spec):
    """Create a default config dict.

    Args:
        spec: An iterable of (path, Option) tuples. Each path is an iterable of strings describing the path to the 
            option in the config.  

    Returns: A dict tree with all of the options in the spec represented by their default value.
    """
    config = {}
    for path, option in spec:
        dest = config
        for segment in path:
            dest = dest.setdefault(segment, {})
            if not isinstance(dest, dict):
                raise ValueError('Conflicting path: {} {}'.format(path, option))
        assert isinstance(dest, dict)

        if option.name in dest:
            raise ValueError('Conflicting option: {} {}'.format(path, option))

        dest[option.name] = option.default

    return config


def merge(dest, src):
    """Merge two config dicts.
    
    `dest` is updated in-place with the contents of `src`.
    """
    for src_name, src_val in src.items():
        if isinstance(src_val, dict):
            dest_val = dest.setdefault(src_name, {})
            if not isinstance(dest_val, dict):
                raise ValueError('Incompatible config structures')

            merge(dest_val, src_val)
        else:
            dest[src_name] = src_val
