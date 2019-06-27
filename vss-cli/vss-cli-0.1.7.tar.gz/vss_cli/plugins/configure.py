"""Configuration plugin for VSS CLI (vss-cli)."""
import json
import logging
import os
from typing import Any

import click
from ruamel.yaml.parser import ParserError
from vss_cli import const
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.data_types import ConfigEndpoint
from vss_cli.helper import format_output, str2bool
from vss_cli.utils.emoji import EMOJI_UNICODE

_LOGGING = logging.getLogger(__name__)


ej_warn = EMOJI_UNICODE.get(':alien:')
ej_rkt = EMOJI_UNICODE.get(':rocket:')
ej_tada = EMOJI_UNICODE.get(':party_popper:')
ej_save = EMOJI_UNICODE.get(':floppy_disk:')
ej_check = EMOJI_UNICODE.get(':white_heavy_check_mark:')


@click.group('configure')
@pass_context
def cli(ctx: Configuration):
    """Configure VSS-CLI options."""
    ctx.auto_output('table')


@cli.command(
    'upgrade',
    short_help='Upgrade legacy configuration.'
)
@click.argument(
    'legacy_config',
    envvar='VSS_CONFIG',
    type=click.Path(exists=True),
    default=const.LEGACY_CONFIG
)
@click.option(
    '-c', '--confirm',
    is_flag=True, default=False,
    help='Proceed with migration without prompting confirmation.'
)
@click.option(
    '-o', '--overwrite',
    is_flag=True, default=False,
    help='Overwrite if target file exists.'
)
@pass_context
def upgrade(ctx: Configuration, legacy_config, confirm, overwrite):
    """Upgrade legacy configuration (config.json) to current (config.yaml)."""
    cfg_exc = False
    try:
        with open(legacy_config, 'r') as f:
            legacy_endpoints = ctx.yaml_load(f)
        endpoints = []
        if legacy_endpoints:
            n_ep = len(legacy_endpoints)
            click.echo(
                f'Found {n_ep} endpoints. Migrating to new configuration file.'
            )
            for ep_k, ep_v in legacy_endpoints.items():
                t_ep = {'url': ep_k, 'auth': ep_v['auth'],
                        'token': ep_v['token']}
                ep = ConfigEndpoint.from_json(json.dumps(t_ep))
                endpoints.append(ep)
            ep = len(endpoints)
            _LOGGING.debug(
                f'Successfully loaded {ep} endpoints '
                f'from legacy configuration.'
            )
            confirmation = confirm or click.confirm(
                f'\nWould you like to upgrade {ep} endpoint(s)? '
                f'This action will \n'
                f'create a new configuration file {ctx.config} \n'
                f'with your endpoints in it'
            )
            if confirmation:
                # load new configuration file
                config_file = ctx.load_config_template()
                config_file.update_endpoints(*endpoints)
                # check if target exists
                target_exists = os.path.isfile(ctx.config)
                if target_exists:
                    if not (overwrite or click.confirm(
                            f'\nOverwrite {ctx.config}?'
                    )):
                        raise click.Abort('Cancelled by user')
                # all ok
                ctx.write_config_file(new_config_file=config_file)
                ctx.secho(
                    f'\nSuccessfully migrated {legacy_config} {ej_tada}',
                    fg='green',
                    nl=True
                )
            else:
                raise click.Abort('Cancelled by user')
        else:
            _LOGGING.warning('No endpoints found in configuration file.')
            cfg_exc = True
    except KeyError as ex:
        _LOGGING.warning(f'Missing {str(ex)} in endpoint configuration.', )
        cfg_exc = True
    except (TypeError, ParserError) as ex:
        _LOGGING.warning(f'{str(ex)}')
        cfg_exc = True
    finally:
        if cfg_exc:
            _LOGGING.warning(
                'Try running "vss-cli configure mk" '
                'to create a new configuration file.'
            )


@cli.command(
    'mk',
    short_help='Create new endpoint configuration.'
)
@click.option(
    '-r', '--replace',
    is_flag=True, default=False,
    help='Replace existing configuration'
)
@click.option(
    '-e', '--endpoint-name',
    type=click.STRING,
    help='Custom endpoint name. Default to endpoint hostname.',
    required=False
)
@pass_context
def mk(ctx: Configuration, replace: bool, endpoint_name: str):
    """Create new configuration or add profile to config file"""
    new_endpoint = ctx.endpoint or click.prompt(
        'Endpoint',
        default=const.DEFAULT_ENDPOINT,
        type=click.STRING,
        show_default=True
    )
    endpoint_name = endpoint_name or click.prompt(
        'Endpoint Name',
        default=ctx.endpoint_name,
        type=click.STRING,
        show_default=True
    )
    username = ctx.username or click.prompt(
        'Username',
        default=ctx.username,
        show_default=True,
        type=click.STRING
    )
    password = ctx.password or click.prompt(
        'Password',
        default=ctx.password,
        show_default=False,
        hide_input=True,
        type=click.STRING,
        confirmation_prompt=True
    )
    is_configured = ctx.configure(
        username=username,
        password=password,
        endpoint=new_endpoint,
        replace=replace,
        endpoint_name=endpoint_name
    )
    if is_configured:
        # feedback message
        ctx.secho(
            f'You are ready to use the vss-cli {ej_rkt}',
            fg='green'
        )
    else:
        _LOGGING.warning(
            f'Houston, we have a problem {ej_warn}. '
            f'Could not create configuration.',
        )


COLUMNS_DETAILS = [
    ("NAME", "name"),
    ("ENDPOINT", "endpoint"),
    ("USER", "user"),
    ("PASS", "pass"),
    ("TOKEN", "token"),
    ("SOURCE", "source"),
    ('DEFAULT', 'default'),
]


@cli.command(
    'set',
    short_help='Update general settings attribute.'
)
@click.argument(
    'setting',
    type=click.Choice(
        const.GENERAL_SETTINGS.keys()
    ),
)
@click.argument(
    'value',
)
@pass_context
def set_cfg(ctx: Configuration, setting: str, value: Any):
    ctx.load_config(validate=False)
    data_type = const.GENERAL_SETTINGS[setting]
    was = None
    to = None
    try:
        was = getattr(ctx.config_file.general, setting)
        f = str2bool if data_type == bool else data_type
        to = f(value)
        if setting == 'default_endpoint_name':
            is_ok = ctx.config_file.get_endpoint(value)
            if not is_ok:
                raise click.BadArgumentUsage(
                    f'Endpoint {value} does not exist. '
                    f'Run "vss-cli configure mk -e {value}" '
                    f'to create endpoint first.'
                )
        setattr(ctx.config_file.general, setting, to)
    except ValueError:
        _LOGGING.warning(
            f'{setting} value must be {data_type}'
        )
    ctx.secho(f"Updating {setting} from {was} -> {to}.")
    ctx.write_config_file(config_general=ctx.config_file.general)
    ctx.secho(f"{ctx.config} updated {ej_save}", fg='green')
    return


@cli.command(
    'ls',
    short_help='List existing endpoint configuration'
)
@pass_context
def ls(ctx: Configuration):
    """List existing configuration"""
    from base64 import b64decode
    cfg_endpoints = list()
    try:
        config_file = ctx.load_config_file()
        ctx.set_defaults()
        default_endpoint = config_file.general.default_endpoint_name
        endpoints = config_file.endpoints or []
        # checking profiles
        for endpoint in endpoints:
            is_default = ej_check \
                if default_endpoint == endpoint.name else ''
            token = ''
            user = ''
            pwd = ''
            auth = endpoint.auth
            url = endpoint.url
            if auth:
                auth_enc = auth.encode()
                user, pwd = b64decode(auth_enc).split(b':')
                user = user.decode()
            masked_pwd = ''.join(['*' for i in range(len(pwd))])
            if endpoint.token:
                token = f"{endpoint.token[:10]}...{endpoint.token[-10:]}"

            cfg_endpoints.append(
                {
                    'default': is_default,
                    'name': endpoint.name,
                    'endpoint': url,
                    'user': user,
                    'pass': masked_pwd[:8],
                    'token': token,
                    'source': 'config file'
                }
            )
    except FileNotFoundError as ex:
        _LOGGING.error(f'{str(ex)}')
        ctx.secho(
            f'Have you run '
            f'"vss-cli configure mk"?', fg='green'
        )

    # checking env vars
    envs = [e for e in os.environ if 'VSS_' in e]
    if envs:
        user = os.environ.get('VSS_USER', '')
        pwd = os.environ.get('VSS_USER_PASS', '')
        masked_pwd = ''.join(['*' for i in range(len(pwd))])
        tk = os.environ.get('VSS_TOKEN', '')
        endpoint = os.environ.get(
            'VSS_ENDPOINT',
            const.DEFAULT_ENDPOINT
        )
        source = 'env'
        cfg_endpoints.append(
            {'endpoint': endpoint,
             'user': user, 'pass': masked_pwd,
             'token': '{}...{}'.format(tk[:10], tk[-10:]),
             'source': source}
        )
    if cfg_endpoints:
        click.echo(
            format_output(
                ctx,
                cfg_endpoints,
                columns=COLUMNS_DETAILS,
            )
        )
    else:
        ctx.echo('No configuration was found')


@cli.command(
    'edit',
    short_help='Edit configuration file.'
)
@click.option(
    '-l', '--launch',
    is_flag=True,
    help='Open config file with default editor'
)
@pass_context
def edit(ctx: Configuration, launch):
    """Edit configuration file"""
    # either launch or edit in
    if launch:
        click.launch(ctx.config, locate=True)
    else:
        # proceed to load file
        with open(ctx.config, 'r') as data_file:
            raw = data_file.read()
        # launch editor
        new_raw = click.edit(
            raw,
            extension='.yaml'
        )
        if new_raw is not None:
            ctx.secho(f"Updating {ctx.config} {ej_save}", fg='green')
            new_obj = ctx.yaml_load(new_raw)
            with open(ctx.config, 'w') as fp:
                ctx.yaml_dump_stream(
                    new_obj, stream=fp
                )
        else:
            ctx.echo("No edits/changes returned from editor.")
            return
