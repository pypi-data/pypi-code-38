from copy import deepcopy

from flask_script import Option
from munch import munchify

from probator.config import dbconfig, DBCChoice
from probator.plugins.commands import BaseCommand


class Auth(BaseCommand):
    """Changes the active auth plugin and bootstraps the new system if needed"""
    name = 'Auth'
    option_list = (
        Option(
            '-a', '--auth-system',
            dest='authsys',
            type=str,
            help='Name of the auth system to set as the active'
        ),
        Option(
            '-l', '--list',
            dest='list',
            action='store_true',
            default=False
        )
    )

    def run(self, **kwargs):
        auth_config = dbconfig.get('auth_system', 'default')
        kwargs = munchify(kwargs)

        if kwargs.list:
            self.log.info('--- List of available auth systems ---')
            for authsys in sorted(auth_config['available']):
                if authsys in auth_config['enabled']:
                    self.log.info(f'{authsys} (active)')

                else:
                    self.log.info(authsys)

            self.log.info('--- End list of Auth Systems ---')

        elif kwargs.authsys:
            if kwargs.authsys in auth_config['available']:
                if kwargs.authsys in auth_config['enabled']:
                    self.log.info(f'{kwargs.authsys} is already the active auth system')
                else:
                    itm = deepcopy(auth_config)
                    itm['enabled'] = [kwargs.authsys]
                    self.dbconfig.set('default', 'auth_system', DBCChoice(itm))
                    self.log.info(f'{kwargs.authsys} has been set as the active auth system')
            else:
                self.log.error(f'Invalid auth system: {kwargs.authsys}')

        else:
            print('You must use either -a or -l')
