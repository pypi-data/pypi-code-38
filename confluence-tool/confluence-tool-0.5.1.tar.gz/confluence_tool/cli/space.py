from .cli import *

space_command = command.add_subcommands('space', help="working spaces")

@space_command('ls', arg_format(default="{key:10s} {name}"), arg_write_format(default='format'), arg_expand, arg_status, arg_label,
    arg('-t', '--type', choices=('global', 'personal', 'all'), default="global", help="space type"),
    arg_field,
    )
def space_list(config):
    # type, status, label, expand
    kwargs = config.dict('expand', 'status', 'type', 'label')
    if kwargs['type'] == 'all':
        del kwargs['type']

    results = [ r for r in config.confluence_api.listSpaces(**kwargs) ]

    if config.get('write') == 'format':
        if config.get('format'):
            for result in results:
                if '{}' in config['format']:
                    fields = [ result[f] for f in config['field'] ]
                    print(config['format'].format(*fields))
                else:
                    print(unicode(config['format']).format(**result))
    else:
        if config['write'] == 'json':
            import json
            json.dump(results, sys.stdout)

        elif config['write'] == 'yaml':
            import pyaml
            pyaml.p(results)
