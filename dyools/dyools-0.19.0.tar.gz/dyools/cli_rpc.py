from __future__ import (absolute_import, division, print_function, unicode_literals)

import base64
import code
import os
import signal
import sys
from pprint import pformat
from threading import Thread

import click
from past.types import basestring

from .klass_date import Date
from .klass_data import Data
from .klass_eval import Eval
from .klass_odoo_rpc import RPC, CONFIG_FILE
from .klass_operator import Operator
from .klass_path import Path
from .klass_print import Print
from .klass_tool import Tool
from .klass_xml import Xml
from .klass_yaml_config import YamlConfig

ORDER = dict(id=1, display_name=2, name=2, key=3, user_id=4, partner_id=5, product_id=6)
LANGS = dict(fr='fr_FR', fr_FR='fr_FR', en='en_US', en_US='en_US')


class ConfigEnum(object):
    HOST = 'host'
    PORT = 'port'
    DATABASE = 'database'
    USER = 'user'
    PASSWORD = 'password'
    SUPERADMINPASSWORD = 'superadminpassword'
    PROTOCOL = 'protocol'
    MODE = 'mode'
    PRODUCTION = 'production'
    TEST = 'test'
    DEVELOPEMENT = 'development'
    MODES = [PRODUCTION, TEST, DEVELOPEMENT]
    JSONRPC = 'jsonrpc'
    JSONRPC_SSL = 'jsonrpc+ssl'
    PROTOCOLS = [JSONRPC, JSONRPC_SSL]
    DEFAULT = 'default'


DEFAULT_CONFIG = {
    ConfigEnum.HOST: 'localhost',
    ConfigEnum.PORT: 8069,
    ConfigEnum.DATABASE: 'demo',
    ConfigEnum.USER: 'admin',
    ConfigEnum.PASSWORD: 'admin',
    ConfigEnum.SUPERADMINPASSWORD: 'admin',
    ConfigEnum.PROTOCOL: 'jsonrpc',
    ConfigEnum.MODE: 'dev',
    ConfigEnum.DEFAULT: False,
}


def _config_to_server(config):
    schema = 'http://' if config.get(ConfigEnum.PROTOCOL, ConfigEnum.JSONRPC) == ConfigEnum.JSONRPC else 'https://'
    fmt = '{schema}{host}:{port}/?database={database}&user={user}&password={password}&mode={mode}'
    return fmt.format(schema=schema, **config)


def _check_production(config):
    if config.get(ConfigEnum.MODE, ConfigEnum.PRODUCTION) == ConfigEnum.PRODUCTION:
        click.confirm('Production environment, do you want to continue?', abort=True)


def fmt_login(config):
    fmt = 'database={database} as {user} mode={mode}'
    return fmt.format(**config)


def fmt_connect(config):
    fmt = '{host}:{port}, database={database} mode={mode}'
    if 'timeout_min' in config:
        fmt += ' timeout={timeout_min} min'
    return fmt.format(**config)


@click.group()
@click.option('--database', '-d', type=click.STRING, default=None, help="Database")
@click.option('--host', '-h', type=click.STRING, default=None, help="Host")
@click.option('--load', '-l', type=click.STRING, help="Name")
@click.option('--config', '-c',
              type=click.Path(
                  exists=True,
                  file_okay=True,
                  dir_okay=False,
                  writable=True,
                  readable=True,
                  resolve_path=True
              ), default=CONFIG_FILE, help="Path of the configuration")
@click.option('--port', '-p', type=click.INT, default=None, help="Port")
@click.option('--user', '-u', type=click.STRING, default=None, help="User")
@click.option('--password', '-w', type=click.STRING, default=None, help="Password")
@click.option('--superadminpassword', '-s', type=click.STRING, default=None, help="Super admin password")
@click.option('--protocol', type=click.Choice(ConfigEnum.PROTOCOLS), default=None, help="Protocol")
@click.option('--mode', '-m', type=click.Choice(ConfigEnum.MODES), default=None, help="Mode")
@click.option('--timeout', '-t', type=click.INT, default=10, help="Timeout in minutes")
@click.option('--yes', is_flag=True, default=False, help='Prevent showing confirmation prompts')
@click.option('--no-context', is_flag=True, default=False, help='Not send the context to Odoo')
@click.option('--debug', is_flag=True, default=False, help='Launch in debug mode')
@click.pass_context
def cli_rpc(ctx, database, host, port, user, password, superadminpassword, protocol, timeout, config, load, mode, yes,
            no_context, debug):
    """Load configuration and connect to an Odoo instance"""
    Print.info('Now: {}'.format(Date()))
    yaml_obj = YamlConfig(config, create_if_not_exists=True)
    configs = yaml_obj.get_data()
    ctx.obj = {}
    rpc = False
    if load:
        if load not in configs:
            Print.error('The configuration [{}] not found!'.format(load))
        current_config = yaml_obj.get_values(_name=load)
    else:
        current_config = yaml_obj.get_values(default=True) or DEFAULT_CONFIG
    if host is not None:
        current_config[ConfigEnum.HOST] = host
    if port is not None:
        current_config[ConfigEnum.PORT] = port
    if database is not None:
        current_config[ConfigEnum.DATABASE] = database
    if user is not None:
        current_config[ConfigEnum.USER] = user
    if password is not None:
        current_config[ConfigEnum.PASSWORD] = password
    if superadminpassword is not None:
        current_config[ConfigEnum.SUPERADMINPASSWORD] = superadminpassword
    if protocol is not None:
        current_config[ConfigEnum.PROTOCOL] = protocol
    if mode is not None:
        current_config[ConfigEnum.MODE] = mode
    current_config.update(dict(timeout=timeout * 60., timeout_min=timeout))

    def action_connect():
        global rpc
        _check_production(current_config)
        try:
            Print.info('Try to connect to the server {fmt_connect}'.format(fmt_connect=fmt_connect(current_config)))
            rpc = RPC(**current_config)
            current_config.update(dict(version=rpc.version))
            rpc.odoo.config['auto_context'] = not no_context
            Print.success('Connected to {fmt_connect}'.format(fmt_connect=fmt_connect(current_config)))
        except:
            Print.error('Cannot connect to server {fmt_connect}'.format(fmt_connect=fmt_connect(current_config)))
        return rpc

    def action_login():
        global rpc
        rpc = action_connect()
        if rpc:
            rpc = RPC(**current_config)
            try:
                Print.info('Try to login to {fmt_login}'.format(fmt_login=fmt_login(current_config)))
                rpc.login()
                Print.success('Connected to {fmt_login}'.format(fmt_login=fmt_login(current_config)))
            except:
                Print.error('Cannot connect to {fmt_login}'.format(fmt_login=fmt_login(current_config)))
        return rpc

    def new_rpc(config_name, login=False, state={}):
        if config_name not in configs:
            Print.error('The configuration [{%s}] not found'.format(config_name))
        new_config = configs[config_name]
        _check_production(new_config)
        try:
            Print.info('Try to connect to the server {fmt_connect}'.format(fmt_connect=fmt_connect(new_config)))
            internal_rpc = RPC(**new_config)
            new_config.update(dict(version=internal_rpc.version))
            internal_rpc.odoo.config['auto_context'] = not no_context
            Print.success('Connected to {fmt_connect}'.format(fmt_connect=fmt_connect(new_config)))
            state['connected'] = True
            if login:
                try:
                    Print.info('Try to login to {fmt_login}'.format(fmt_login=fmt_login(new_config)))
                    internal_rpc.login()
                    Print.success('Connected to {fmt_login}'.format(fmt_login=fmt_login(new_config)))
                    state['logged'] = True
                except:
                    internal_rpc = False
                    Print.error('Cannot connect to {fmt_login}'.format(fmt_login=fmt_login(new_config)))
                    state['logged'] = False
        except:
            internal_rpc = False
            Print.error('Cannot connect to server {fmt_connect}'.format(fmt_connect=fmt_connect(new_config)))
            state['connected'] = False
        return internal_rpc

    def update_list():
        global odoo
        if odoo:
            Print.info('Updating the list of modules ...')
            odoo.env['ir.module.module'].update_list()

    ctx.obj['config_obj'] = yaml_obj
    ctx.obj['configs'] = configs
    ctx.obj['current_config'] = current_config
    ctx.obj['action_connect'] = action_connect
    ctx.obj['action_login'] = action_login
    ctx.obj['update_list'] = update_list
    ctx.obj['new_rpc'] = new_rpc
    ctx.obj['rpc'] = rpc
    ctx.obj['yes'] = yes
    ctx.obj['no_context'] = no_context
    ctx.obj['debug'] = debug


######################################################################
###
###                   CONFIGURATIONS OPERATIONS
###
#######################################################################
def __list_configurations(ctx, grep=False, index=False):
    configs = ctx.obj['configs']
    data = Data(configs)
    tbl = data.get_pretty_table(add_index=True, grep=grep, index=index)
    Print.info(tbl, header="List of configurations", total=len(tbl._rows), )


@cli_rpc.command('create')
@click.argument('name')
@click.pass_context
def __create_config(ctx, name):
    """Create a new configuration"""
    configs = ctx.obj['configs']
    current_config = ctx.obj['current_config']
    if name in configs:
        if not click.confirm('The name [{}] is already exists ! continue to update ?'.format(name)):
            ctx.abort()
    host = click.prompt(ConfigEnum.HOST, default=current_config[ConfigEnum.HOST], type=str)
    port = click.prompt(ConfigEnum.PORT, default=current_config[ConfigEnum.PORT], type=int)
    database = click.prompt(ConfigEnum.DATABASE, default=current_config[ConfigEnum.DATABASE], type=str)
    user = click.prompt(ConfigEnum.USER, default=current_config[ConfigEnum.USER], type=str)
    password = click.prompt(ConfigEnum.PASSWORD, default=current_config[ConfigEnum.PASSWORD], type=str)
    superadminpassword = click.prompt(ConfigEnum.SUPERADMINPASSWORD,
                                      default=current_config[ConfigEnum.SUPERADMINPASSWORD], type=str)
    protocol = click.prompt(ConfigEnum.PROTOCOL, default=current_config[ConfigEnum.PROTOCOL], type=str)
    mode = click.prompt(ConfigEnum.MODE, default=current_config[ConfigEnum.MODE], type=str)
    data = DEFAULT_CONFIG.copy()
    data.update(dict(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        superadminpassword=superadminpassword,
        protocol=protocol,
        mode=mode))
    ctx.obj['config_obj'].add(name, **data)
    ctx.obj['config_obj'].switch(name, 'default', True, False)
    ctx.obj['config_obj'].dump()


@cli_rpc.command('list')
@click.argument('grep', required=False)
@click.pass_context
def __list(ctx, grep):
    """List of configurations"""
    __list_configurations(ctx, grep)


@cli_rpc.command('which')
@click.pass_context
def __which(ctx):
    """Show which configuration is current"""
    Data(ctx.obj['current_config']).show()


@cli_rpc.command('use')
@click.argument('grep', required=False)
@click.pass_context
def __use(ctx, grep):
    """Load and use a configuration"""
    configs = ctx.obj['configs']
    data = Data(configs)
    __list_configurations(ctx, grep)
    if not grep:
        grep = click.prompt('Enter the name or the index of a configuration to use')
    name = index = False
    for i, item in enumerate(data.get_lines(), 1):
        if grep:
            if isinstance(grep, basestring) and grep.strip().isdigit() and int(grep) == i:
                name = item[0]
                index = i
            if item[0] == grep:
                name = item[0]
                index = i
    if not name:
        Print.error('please retry with an other grep !')
    ctx.obj['config_obj'].switch(name, ConfigEnum.DEFAULT, True, False)
    ctx.obj['config_obj'].dump()
    __list_configurations(ctx, False, index=index)


@cli_rpc.command('delete')
@click.argument('grep', required=False)
@click.pass_context
def __delete(ctx, grep):
    """Delete a configuration"""
    configs = ctx.obj['configs']
    data = Data(configs)
    __list_configurations(ctx, grep)
    if not grep:
        grep = click.prompt('Enter the name or the index of a configuration to delete')
    name = index = False
    for i, item in enumerate(data.get_lines(), 1):
        if grep:
            if isinstance(grep, basestring) and grep.strip().isdigit() and int(grep) == i:
                name = item[0]
                index = i
            if item[0] == grep:
                name = item[0]
                index = i
    if not name:
        Print.error('please retry with an other grep !')
    click.confirm('Are you sure you want to delete the configuration [{}]'.format(name), abort=True)
    ctx.obj['config_obj'].delete(name=name)
    ctx.obj['config_obj'].dump()
    __list_configurations(ctx, False, index=index)


@cli_rpc.command('login')
@click.argument('user', required=False)
@click.argument('password', required=False)
@click.pass_context
def __login(ctx, user, password):
    """Login to the database"""
    if user:
        ctx.obj['current_config'].update(dict(user=user))
    if password:
        ctx.obj['current_config'].update(dict(password=password))
    ctx.obj['action_login']()


@cli_rpc.command('connect')
@click.argument('host', required=False)
@click.argument('port', required=False)
@click.pass_context
def __connect(ctx, host, port):
    """Connect to the server"""
    if host:
        ctx.obj['current_config'].update(dict(host=host))
    if port:
        ctx.obj['current_config'].update(dict(port=port))
    ctx.obj['action_connect']()


######################################################################
###
###               DATABASE AND SERVER OPERATIONS
###
#######################################################################

@cli_rpc.command('db_list')
@click.pass_context
def __db_list(ctx):
    """List databases"""
    ctx.obj['action_connect']().list_db()


@cli_rpc.command('ping')
@click.option('--login/--no-login', default=False, required=False, help='Specify if it should ping a database or not')
@click.pass_context
def __db_ping(ctx, login):
    """Ping all servers and databases"""
    configs = ctx.obj['configs']

    def _check(config_name, config_values):
        state = dict(connected=False, logged=False)
        try:
            ctx.obj['new_rpc'](config_name, login=login, state=state)
        except:
            pass
        server = _config_to_server(config_values)
        config_values.update(dict(server=server))
        config_values.update(state)

    threads = []
    for k, v in configs.items():
        t = Thread(target=_check, args=(k, v))
        t.start()
        threads.append(t)
    [t.join() for t in threads]
    if login:
        header = ['name', 'connected', 'logged', 'server']
    else:
        header = ['name', 'connected', 'server']
    Data(configs, header=header, name='name').show()


@cli_rpc.command('db_dump')
@click.argument('destination', type=click.STRING, required=True)
@click.option('--drop/--no-drop', default=False, required=False,
              help='Case destination is a configuration, drop the destination database')
@click.option('--zip/--no-zip', default=True, required=False, help='Backup in a zip mode (default=zip)')
@click.pass_context
def __db_dump(ctx, destination, drop, zip):
    """Backup a database and restore it to another server if destination is a name of a configuration"""
    configs = ctx.obj['configs']
    rpc = ctx.obj['action_connect']()
    assert destination in configs or os.path.isdir(destination), 'The destination [{}] is not found'.format(destination)
    if destination in configs:
        destination_rpc = ctx.obj['new_rpc'](destination)
        with Path.tempdir() as tmp:
            path = rpc.dump_db(dest=tmp, zip=zip)
            destination_rpc.restore_db(path, drop=drop)
    else:
        rpc.dump_db(destination)


@cli_rpc.command('db_restore')
@click.argument('source', type=click.STRING, required=True)
@click.option('--drop/--no-drop', default=False, required=False, help='Drop the database before the restore')
@click.pass_context
def __db_restore(ctx, source, drop):
    """Restore a database from a file or from a configuration"""
    configs = ctx.obj['configs']
    rpc = ctx.obj['action_connect']()
    assert source in configs or os.path.isfile(source), 'The source [{}] is not found'.format(source)
    if source in configs:
        source_rpc = ctx.obj['new_rpc'](source)
        with Path.tempdir() as tmp:
            path = source_rpc.dump_db(dest=tmp)
            rpc.restore_db(path, drop=drop)
    else:
        rpc.restore_db(source, drop=drop)


@cli_rpc.command('db_drop')
@click.argument('grep', nargs=-1, required=False)
@click.pass_context
def __db_drop(ctx, grep):
    """Drop a database"""
    rpc = ctx.obj['action_connect']()
    grep = grep or rpc.dbname
    yes = ctx.obj['yes']
    databases = Operator.unique(Operator.split_and_flat(',', grep))
    if yes or click.confirm('Are you sure you want to delete the databases : {}'.format(databases)):
        for db_name in databases:
            rpc.drop_db(db_name)


@cli_rpc.command('db_create')
@click.argument('database', required=False)
@click.option('--with-demo', is_flag=True, default=False, help='Load the demonstration data, default=False', )
@click.option('--language', '-l', type=click.STRING, default='fr_FR', help='Code of the locale, default=fr_FR', )
@click.pass_context
def __db_create(ctx, database, with_demo, language):
    """Create a new database"""
    rpc = ctx.obj['action_connect']()
    rpc.create_db(database or rpc.dbname, with_demo, language)


######################################################################
###
###                   MODULES MANAGEMENT
###
#######################################################################

@cli_rpc.command('install')
@click.argument('addons', type=click.STRING, nargs=-1, required=False)
@click.pass_context
def __module_install(ctx, addons):
    """Install modules"""
    addons = Operator.split_and_flat(',', addons)
    rpc = ctx.obj['action_login']()
    rpc.install(addons)


@cli_rpc.command('upgrade')
@click.argument('addons', type=click.STRING, nargs=-1, required=False)
@click.pass_context
def __module_upgrade(ctx, addons):
    """Upgrades modules"""
    addons = Operator.split_and_flat(',', addons)
    rpc = ctx.obj['action_login']()
    rpc.upgrade(addons)


@cli_rpc.command('uninstall')
@click.argument('addons', type=click.STRING, nargs=-1, required=False)
@click.pass_context
def __module_uninstall(ctx, addons):
    """Uninstall modules"""
    addons = Operator.split_and_flat(',', addons)
    rpc = ctx.obj['action_login']()
    rpc.uninstall(addons)


@cli_rpc.command('update_list')
@click.pass_context
def __module_update_list(ctx):
    """Update module's list """
    rpc = ctx.obj['action_login']()
    rpc.update_list()


######################################################################
###
###                   DATA OPERATIONS
###
#######################################################################

@cli_rpc.command('param')
@click.argument('key', default=None, required=False)
@click.argument('value', default=None, required=False)
@click.pass_context
def __params(ctx, key, value):
    """Manage parameters
    rpc param  => list all parameters
    rpc param key1  => get value
    rpc param key1 value1 => set value1 to key1
    """
    rpc = ctx.obj['action_login']()
    fields = ['id', 'key', 'value']
    domain = []
    result = None
    if key:
        result = rpc.get_param(key)
    if value is not None:
        result = rpc.set_param(key, value)
    if result is None:
        data = Data(rpc.read('ir.config_parameter', domain=domain, fields=fields), header=fields)
        Print.info(data.get_pretty_table())
    else:
        Print.info('[{} => {}]'.format(key, result))


@cli_rpc.command('data')
@click.argument('model', default=None, required=True)
@click.option('domain', '-d', type=click.STRING, default='', help="Domain")
@click.option('limit', '-l', type=click.INT, default=0, help="Limit")
@click.option('order', '-o', type=click.STRING, default='', help="Order")
@click.option('fields', '-f', multiple=True, type=click.STRING, default='', help="Fields to show")
@click.pass_context
def __data(ctx, model, domain, limit, order, fields):
    """Show records"""
    fields = Operator.split_and_flat(',', fields) if fields else ['id', 'name']
    rpc = ctx.obj['action_login']()
    kwargs = dict(domain=domain, fields=fields)
    if limit: kwargs.update(dict(limit=limit))
    if order: kwargs.update(dict(order=order))
    Data(rpc.read(model, **kwargs), header=fields).show()


@cli_rpc.command('count')
@click.argument('model', default=None, required=True)
@click.option('domain', '-d', type=click.STRING, default='', help="Domain")
@click.pass_context
def __count(ctx, model, domain):
    """Count the records"""
    rpc = ctx.obj['action_login']()
    domain = Tool.construct_domain_from_str(domain)
    Data([[rpc[model].search(domain, count=True)]], header=['Count']).show(header='Count of records')


@cli_rpc.command('func')
@click.argument('model', default=None, required=True)
@click.argument('func', default=None, required=True)
@click.argument('args', nargs=-1, required=False)
@click.option('--arg', '-a', type=click.STRING, nargs=2, multiple=True, help="Provide keywords values")
@click.option('--ids', '-id', type=click.STRING, nargs=1, multiple=True, help="Pass IDS to consider an api.multi")
@click.pass_context
def __func(ctx, model, func, args, arg, ids):
    """Execute a function"""
    args = Eval(Operator.split_and_flat(',', ids)).eval() + Eval(args).eval()
    rpc = ctx.obj['action_login']()
    res = getattr(rpc[model], func)(*args, **dict(Eval(arg).eval()))
    Print.info('Result : {}'.format(pformat(res)))


@cli_rpc.command('fields')
@click.argument('model', default=None, required=True)
@click.option('--fields', '-f', multiple=True, type=click.STRING, default='', help="Fields to show")
@click.option('--grep', '-g', type=click.STRING, default=False, help="Grep the result")
@click.pass_context
def __fields(ctx, model, fields, grep):
    """Fields of a model"""
    rpc = ctx.obj['action_login']()
    fields = Operator.unique(['name', 'type', 'relation'] + Operator.split_and_flat(',', fields))
    Data(rpc.env[model].fields_get(), header=fields, name='name').show(grep=grep)


@cli_rpc.command('menus')
@click.option('--debug/--no-debug', default=False, required=False, help='Show also the debug menus')
@click.option('--xmlid/--no-xmlid', default=False, required=False, help='Show the menus XmlIds')
@click.option('--action/--no-action', default=False, required=False, help='Show th related actions')
@click.option('--model/--no-model', default=False, required=False, help='Show the model')
@click.option('--domain/--no-domain', default=False, required=False, help='Show the domain')
@click.option('--context/--no-context', default=False, required=False, help='Show the context')
@click.option('--crud/--no-crud', default=False, required=False, help='Show the CRUD')
@click.pass_context
def __menus(ctx, debug, xmlid, action, model, domain, context, crud):
    """Show menus"""
    rpc = ctx.obj['action_login']()
    rpc.menus(debug=debug, xmlid=xmlid, action=action, model=model, domain=domain, context=context, crud=crud)


######################################################################
###
###                   VIEWS & QWEB OPERATIONS
###
#######################################################################


@cli_rpc.command('find')
@click.argument('expr', type=click.STRING, required=True)
@click.option('--model', '-m', type=click.STRING, required=False, multiple=True,
              help='Specify a model to restrict the search')
@click.option('--type', '-t', type=click.STRING, required=False, multiple=True,
              help='Specify the type to restrict the search')
@click.pass_context
def __find(ctx, expr, model, type):
    """Searching for the expression in the views"""
    rpc = ctx.obj['action_login']()
    domain = [('arch_db', 'ilike', expr)]
    if model:
        domain.append(('model', 'in', model), )
    if type:
        domain.append(('type', 'in', type), )
    Print.info('Domain : {}'.format(pformat(domain)))
    Data(rpc.get_ir_ui_view(domain), header=["id", "name", "type", "model", "xml_id", "mode"]).show()


@cli_rpc.command('arch')
@click.argument('view', type=click.STRING, required=True)
@click.pass_context
def __arch(ctx, view):
    """Cat the arch of the view"""
    rpc = ctx.obj['action_login']()
    if view.isdigit():
        view = rpc.get_ir_ui_view([('id', '=', int(view))])
    else:
        view = rpc.xmlid_to_object(view)
    Print.info(Xml.SEPARATOR, )
    Print.info(Xml(view.arch).pretty(), )
    Print.info(Xml.SEPARATOR, )


@cli_rpc.command('combined')
@click.argument('view', type=click.STRING, required=True)
@click.pass_context
def __combined(ctx, view):
    """Combined view architecture"""
    rpc = ctx.obj['action_login']()
    if view.isdigit():
        view = rpc.get_ir_ui_view([('id', '=', int(view))])
    else:
        view = rpc.xmlid_to_object(view)
    xml = view.read_combined(['arch'])['arch']
    Print.info(Xml.SEPARATOR, )
    Print.info(Xml(xml).pretty(), )
    Print.info(Xml.SEPARATOR, )


######################################################################
###
###                   SHELL MODE
###
#######################################################################

def raise_keyboard_interrupt(*a):
    raise KeyboardInterrupt()


class Console(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        try:
            import readline
            import rlcompleter
        except ImportError:
            print('readline or rlcompleter not available, autocomplete disabled.')
        else:
            readline.set_completer(rlcompleter.Completer(locals).complete)
            readline.parse_and_bind("tab: complete")


class Shell(object):
    def init(self):
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)

    def console(self, local_vars):
        if not os.isatty(sys.stdin.fileno()):
            exec(sys.stdin, local_vars)
        else:
            Console(locals=local_vars).interact()


@cli_rpc.command()
@click.pass_context
def shell(ctx):
    """Shell mode"""
    rpc = ctx.obj['action_login']()
    env = rpc.env
    Shell().console(locals())


######################################################################
###
###                 XMLID AND METADATA
###
#######################################################################


@cli_rpc.command('xmlid')
@click.argument('xmlid', type=click.STRING, required=True)
@click.option('--fields', '-f', multiple=True, type=click.STRING, default='', help="Fields to show")
@click.pass_context
def __xmlid(ctx, xmlid, fields):
    """Show the related model and ID associated to the given XMLID, also fields if provided"""
    fields = Operator.split_and_flat(',', fields)
    rpc = ctx.obj['action_login']()
    view = rpc.xmlid_to_object(xmlid)
    Data({'model': view._name, 'id': view.id}).show()
    if fields:
        Data(view, header=fields).show()


@cli_rpc.command('metadata')
@click.argument('model', type=click.STRING, required=True)
@click.argument('id_', metavar='ID', type=click.INT, required=True)
@click.pass_context
def __metadata(ctx, model, id_):
    """Show metadata of a model/id"""
    rpc = ctx.obj['action_login']()
    record = rpc[model].browse(id_)
    Data(record.get_metadata()).show()


######################################################################
###
###                 LOAD YAMLS MANAGEMENTS
###
#######################################################################

@cli_rpc.command('load')
@click.argument('datas', type=click.STRING, required=True, nargs=-1, )
@click.option('--assets', '-a',
              type=click.Path(
                  exists=True,
                  file_okay=False,
                  dir_okay=True,
                  readable=True,
                  resolve_path=True
              ), default=os.getcwd(), help="Path of the assets")
@click.option('--start', type=click.INT, help="Start index")
@click.option('--stop', type=click.INT, help="Stop index")
@click.pass_context
def __load(ctx, datas, assets, start, stop):
    """Process yaml files"""
    rpc = ctx.obj['action_login']()
    rpc.load_yaml(path=datas, assets=assets, start=start, stop=stop, auto_commit=False)


######################################################################
###
###                 TRANSLATION MANAGEMENT
###
#######################################################################

@cli_rpc.command('po_export')
@click.argument('addons', type=click.STRING, required=True)
@click.option('--lang', type=click.STRING, default='fr', required=True, help='Code of locale, default=fr')
@click.option('--output', '-o', type=click.Path(
    exists=True,
    file_okay=False,
    dir_okay=True,
    readable=True,
    resolve_path=True
), default=os.getcwd(), help='Output directory')
@click.pass_context
def __po_export(ctx, addons, output, lang):
    """Export PO file of a module"""
    global LANGS
    dest_file = os.path.join(output, '{}.po'.format(lang))
    rpc = ctx.obj['action_login']()
    export_model = rpc['base.language.export']
    module_model = rpc['ir.module.module']
    module_ids = module_model.search([('name', 'in', Operator.split_and_flat(',', addons))])
    if not module_ids:
        raise ValueError('The addons not found in the database')
    export_id = export_model.create({
        'lang': LANGS[lang],
        'format': 'po',
        'modules': [(6, 0, module_ids)],
    })
    export_record = export_model.browse(export_id)
    export_record.act_getfile()
    data = export_record.read(['data'])[0]['data']
    Path.create_file(path=dest_file, content=base64.decodestring(bytes(data, 'utf-8')))
    Print.success('File: %s' % dest_file)


@cli_rpc.command('po_import')
@click.argument('po_file', type=click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True
), required=True)
@click.option('--name', type=click.STRING, default='Français', required=True, help='Name, default=Français')
@click.option('--lang', type=click.STRING, default='fr', required=True, help='Code of the locale, default=fr')
@click.option('--overwrite', is_flag=True, default=False, help='Overwrite existing terms')
@click.pass_context
def __po_import(ctx, po_file, name, lang, overwrite):
    """Import PO file"""
    global LANGS
    rpc = ctx.obj['action_login']()
    import_model = rpc['base.language.import']
    with open(po_file, 'rb') as f:
        import_id = import_model.create({
            'name': name,
            'code': LANGS[lang],
            'overwrite': overwrite,
            'filename': os.path.basename(po_file),
            'data': base64.encodestring(f.read()).decode('utf-8'),
        })
        import_record = import_model.browse(import_id)
        import_record.import_lang()
    Print.success('The file: %s is loaded' % po_file)
