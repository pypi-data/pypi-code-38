from .cli import command, arg
import pyaml

@command('config',
    arg('-u', '--update', action="store_true", help="show data unless this specified"),
    arg('--update-password', action="store_true", help="unless specified, password will not be updated if not needed"),
    arg('--show-password', action="store_true", help="unless specified, password will not be shown"),
    )
def config(config):
    """\
    Get or set configuration.

    For configuring the default base
    """

    if config.get('update') or config.get('update_password'):
        config.setConfig(config.get('update_password'))
        return

    if config.get('baseurl'):
        config.setConfig()
    else:
        cfg = config.getConfig()

        if cfg.get('show_password') and not config.get('show_password'):
            cfg['password'] = '******'

        pyaml.p(cfg)
