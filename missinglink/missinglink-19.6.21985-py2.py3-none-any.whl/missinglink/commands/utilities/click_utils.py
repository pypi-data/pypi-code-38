import click


def pop_key_or_prompt_if(kws, key, src_default=None, **kwargs):
    cur_val = kws.pop(key, src_default)
    while cur_val == src_default:
        if 'default' in kwargs and kws.get('silent', False):
            click.echo('{}: {} (silent)'.format(kwargs.get('text'), kwargs.get('default')))
            return kwargs['default']
        cur_val = click.prompt(**kwargs)
    return cur_val
