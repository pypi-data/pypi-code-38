#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
infraless/main.py

"""
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal

from .controllers.base import Base
from .core.exc import InfralessError
from .core import helpers as hlprs

# configuration defaults
CONFIG = init_defaults('todo')
CONFIG['todo']['foo'] = 'bar'


class InfraLess(App):
    """InfraLess CLI primary application."""

    class Meta:
        label = 'infraless'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        close_on_exit = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [Base]


class InfraLessTest(TestApp, InfraLess):
    """A sub-class of InfraLess that is better suited for testing."""

    class Meta:
        label = 'infraless'


def main():
    with InfraLess() as app:
        try:
            hlprs.log('InfraLess', 'green', figlet=True, on_color='on_blue')
            # print(
            #     colored(
            #         figlet_format('Infra Less', font='slant'), 'green',
            #         'on_blue'))
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except InfralessError as e:
            hlprs.log(e, 'red')
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
