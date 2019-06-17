__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

# from pocketlab.init import logging circular dependency
from jsonmodel.validators import jsonModel

def inject_defaults(command_schema, default_schema):

    default_model = jsonModel(default_schema)
    for key, value in default_model.schema.items():
        if not key in command_schema['schema'].keys():
            command_schema['schema'][key] = value
    for key, value in default_model.components.items():
        if not key in command_schema['components'].keys():
            command_schema['components'][key] = value

    return command_schema

def compile_model(command_schema, cli_schema):
    
    '''
        a method to create a jsonmodel object for command fields with cli metadata
         
    :param command_schema: dictionary with jsonmodel valid schema for command arguments
    :param cli_schema: dictionary with jsonmodel valid schema for command line interface metadata
    :return: jsonmodel object for command fields
    '''

# validate model structure
    if not 'components' in command_schema.keys():
        command_schema['components'] = {}
    if not 'metadata' in command_schema.keys():
        command_schema['metadata'] = {}

# construct cli_model
    cli_model = jsonModel(cli_schema)

# inject cli fields into the metadata for each field
    for key, value in command_schema['schema'].items():
        field_key = '.%s' % key
        if not field_key in command_schema['components'].keys():
            command_schema['components'][field_key] = {}
        if not 'field_metadata' in command_schema['components'][field_key].keys():
            command_schema['components'][field_key]['field_metadata'] = {}
        cli_fields = command_schema['components'][field_key]['field_metadata']
        command_schema['components'][field_key]['field_metadata'] = cli_model.ingest(**cli_fields)

# inject cli fields into metadata field
    command_schema['metadata'] = cli_model.ingest(**command_schema['metadata'])

    return jsonModel(command_schema)

def extract_signature(module_name, command_name):

# retrieve command method
    from importlib import import_module
    import inspect
    command_module = import_module('%s.commands.%s' % (module_name, command_name))
    command_method = getattr(command_module, command_name)

# extract argument list from signature
    command_signature = inspect.signature(command_method)
    command_signature = str(command_signature)[1:-1]
    argument_list = command_signature.replace('\n','').replace(' ','').split(',')

    return argument_list

def compile_arguments(command_name, argument_list, fields_model):

# construct placeholder response
    default_args = {
        'command': command_name
    }
    optional_args = []
    positional_args = []
    exclusive_args = {}

# define dummy variables
    empty_defaults = {
        'string': '',
        'boolean': False,
        'number': 0.0,
        'list': [],
        'map': {},
        'null': None
    }

# define type parser
    def _return_type(value):
        if isinstance(value, bool):
            return bool
        elif isinstance(value, int):
            return int
        elif isinstance(value, float):
            return float
        elif isinstance(value, str):
            return str
        elif isinstance(value, dict):
            return dict
        elif isinstance(value, list):
            return list
        else:
            return None

# define default parser
    def _determine_default(input):

        if input.lower() == 'true':
            default = True
        elif input.lower() == 'false':
            default = False
        elif input.lower() == 'none':
            default = None
        else:
            try:
                try:
                    default = int(input)
                except:
                    default = float(input)
            except:
                default = input
                if default.find('{') > -1 or default.find('[') > -1:
                    default = None

        return default

# construct argument details
    for argument in argument_list:

    # parse name and default from argument string
        name_value = argument.split('=')
        arg_name = name_value[0]
        arg_default = ''
        if len(name_value) > 1:
            arg_default = name_value[1]

    # construct default details
        details = {
            'name': arg_name,
            'option': 'positional',
            'args': [],
            'kwargs': {
                'dest': arg_name,
                'type': None,  # datatypes
                'default': None,  # datatypes
                'metavar': '',
                'nargs': None,  # int or '*', '?', '+'
                'choices': None,  # range() or []
                'action': '',
                # 'const': object(),
                'help': 'replace this message with "cli_help" in field metadata'
            }
        }
        if arg_default:
            details['option'] = 'optional'

    # modify defaults based upon values from fields model
        if not arg_name in fields_model.schema.keys():
            print('%s(%s) missing from fields model.' % (command_name, arg_name))
        else:
            key_map = fields_model.keyMap['.%s' % arg_name]
            cli_details = key_map['field_metadata']

        # determine type
            list_map = {}
            if key_map['value_datatype'] == 'list':
                key_map = fields_model.keyMap['.%s[0]' % arg_name]
                list_map = fields_model.keyMap['.%s' % arg_name]
            details['kwargs']['type'] = _return_type(key_map['declared_value'])

        # skip if dict or None
            if details['kwargs']['type'] in { dict, None }:
                continue

        # determine default
        #     default_value = None
        #     if arg_default:
        #         default_value = _determine_default(arg_default)
        #     if default_value != None:
        #         details['kwargs']['default'] = default_value
            if 'default_value' in key_map.keys():
                details['kwargs']['default'] = key_map['default_value']
            else:
                if key_map['value_datatype'] == 'number':
                    if isinstance(key_map['declared_value'], int):
                        details['kwargs']['default'] = 0
                    else:
                        details['kwargs']['default'] = 0.0
                else:
                    details['kwargs']['default'] = empty_defaults[key_map['value_datatype']]

        # determine help
            if cli_details['cli_help']:
                details['kwargs']['help'] = cli_details['cli_help']

        # determine metavar
            if cli_details['cli_metavar']:
                details['kwargs']['metavar'] = cli_details['cli_metavar']
            elif details['kwargs']['type'] == int:
                details['kwargs']['metavar'] = 'INT'
            elif details['kwargs']['type'] == float:
                details['kwargs']['metavar'] = 'FLOAT'
            elif details['kwargs']['type'] == str:
                details['kwargs']['metavar'] = 'STRING'
            else:
                del details['kwargs']['metavar']

        # determine nargs
            if list_map:
                details['kwargs']['nargs'] = '*'
                if 'max_size' in list_map.keys():
                    if list_map['max_size'] == 1:
                        details['kwargs']['nargs'] = '?'
                if 'min_size' in list_map.keys():
                    if list_map['min_size'] == 1:
                        details['kwargs']['nargs'] = '+'

        # determine choices
            if 'discrete_values' in key_map.keys():
                if key_map['value_datatype'] == 'string':
                    details['kwargs']['choices'] = key_map['discrete_values']
            elif 'min_value' in key_map.keys() and 'max_value' in key_map.keys():
                if key_map['value_datatype'] == 'number':
                    if isinstance(key_map['declared_value'], int):
                        max_value = key_map['max_value'] + 1
                        details['kwargs']['choices'] = range(key_map['min_value'], max_value)

        # determine flags
            if details['option'] == 'positional':
                details['args'] = arg_name
                del details['kwargs']['dest']
            elif cli_details['cli_flags']:
                details['args'] = cli_details['cli_flags']
            else:
                key_flag = '--%s' % arg_name
                details['args'] = [key_flag]

        # modify boolean fields
            if details['kwargs']['type'] == bool:
                del details['kwargs']['nargs']
                del details['kwargs']['choices']
                del details['kwargs']['type']
                if details['kwargs']['default']:
                    details['kwargs']['action'] = 'store_false'
                else:
                    details['kwargs']['action'] = 'store_true'
                del details['kwargs']['default']

        # modify string fields
            elif details['kwargs']['type'] in { int, float, str }:
                if cli_details['cli_action']:
                    details['kwargs']['action'] = cli_details['cli_action']

        # TODO add byte streams

        # remove empty fields
            prop_list = [ 'nargs', 'choices', 'action' ]
            for prop in prop_list:
                if prop in details['kwargs'].keys():
                    if not details['kwargs'][prop]:
                        del details['kwargs'][prop]

    # add details to appropriate list
            if not cli_details['cli_group']:
                if details['option'] == 'positional':
                    positional_args.append(details)
                else:
                    optional_args.append(details)
            else:
                if not cli_details['cli_group'] in exclusive_args.keys():
                    exclusive_args[cli_details['cli_group']] = []
                exclusive_args[cli_details['cli_group']].append(details)


    return default_args, optional_args, positional_args, exclusive_args

def compile_commands(folder_path, module_name, fields_model, preferred_order=None, preserve_markdown=False):

    import re
    import inspect
    from importlib import import_module
    from os import listdir

# retrieve list of commands
    command_list = []
    py_file = re.compile('\\.pyc?$')
    for file in listdir(folder_path):
        if file != '__init__.py':
            if py_file.findall(file):
                command_list.append(py_file.sub('', file))
        command_list.sort()

# customize the order of commands in help
    for i in range(len(preferred_order)):
        if preferred_order[i] not in command_list:
            preferred_order.pop(i)
    for command in command_list:
        if command not in preferred_order:
            preferred_order.append(command)
    command_list = preferred_order

# construct each command model
    command_models = []
    for command in command_list:
        command_module = import_module('%s.commands.%s' % (module_name, command))
        try:
            command_help = getattr(command_module, '_%s_details' % command, None)
            command_method = getattr(command_module, command)

    # compile arguments from method signature
            command_signature = inspect.signature(command_method)
            command_signature = str(command_signature)[1:-1]
            command_signature = command_signature.replace('\n', '').replace(' ', '')
            argument_list = command_signature.split(',')
            argument_kwargs = {
                'command_name': command,
                'argument_list': argument_list,
                'fields_model': fields_model
            }
            def_args, opt_args, pos_args, exc_args = compile_arguments(**argument_kwargs)

    # build command details
            command_details = {
                'description': 'replace this message with "description" in _%s_details' % command,
                'help': 'replace this message with "help" in _%s_details' % command,
                'title': command.capitalize(),
                'benefit': 'replace this message with "benefit" in _%s_details' % command,
                'epilog': ''
            }
            if command_help:
                for key, value in command_details.items():
                    if key in command_help.keys():
                        if value.__class__ == command_help[key].__class__:
                            help_value = command_help[key]
                            if isinstance(help_value, str) and not preserve_markdown:
                                help_value = help_value.replace('```$ ','\'').replace('```', '\'')
                            command_details[key] = help_value
            command_details['name'] = command
            command_details['default_args'] = def_args
            command_details['optional_args'] = opt_args
            command_details['positional_args'] = pos_args
            command_details['exclusive_args'] = exc_args
            command_models.append(command_details)

        except Exception as err:
            # logging.debug(err)
            pass

    return command_models

if __name__ == '__main__':

    from pocketlab import __module__
    command_name = 'home'
    from pocketlab.init import fields_model
    argument_list = extract_signature(__module__, command_name)
    print(argument_list)
    d_args, o_args, p_args, e_args = compile_arguments(command_name, argument_list, fields_model)
    print(d_args)
    print(o_args)
    print(p_args)
    print(e_args)
