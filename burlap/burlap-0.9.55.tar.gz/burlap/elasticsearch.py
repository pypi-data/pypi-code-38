from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class ElasticSearchSatchel(ServiceSatchel):

    name = 'elasticsearch'

    def set_defaults(self):

        self.env.conf_path = '/etc/elasticsearch/elasticsearch.yml'
        self.env.script_engine_groovy_inline_search = False

        self.env.service_commands = {
            START:{
                UBUNTU: 'service elasticsearch start',
            },
            STOP:{
                UBUNTU: 'service elasticsearch stop',
            },
            DISABLE:{
                UBUNTU: 'chkconfig elasticsearch off',
                (UBUNTU, '14.04'): 'update-rc.d -f elasticsearch remove',
            },
            ENABLE:{
                UBUNTU: 'chkconfig elasticsearch on',
                (UBUNTU, '14.04'): 'update-rc.d elasticsearch defaults',
            },
            RESTART:{
                UBUNTU: 'service elasticsearch restart',
            },
            STATUS:{
                UBUNTU: 'service elasticsearch status',
            },
        }

    @property
    def packager_system_packages(self):
        return {
            DEBIAN: ['elasticsearch'],
            UBUNTU: ['elasticsearch'],
        }

    @task(precursors=['packager', 'user', 'cron'])
    def configure(self):
        r = self.local_renderer

        if self.env.enabled:

            if self.env.script_engine_groovy_inline_search:

                # Turn on online groovy search.
                r.sed(
                    filename=self.env.conf_path,
                    before='script.engine.groovy.inline.search: off',
                    after='script.engine.groovy.inline.search: on',
                    use_sudo=True,
                )
                # Remove off.
#                 r.sudo(
#                     "sed '/script.engine.groovy.inline.search: off/d' {conf_path}"\
#                         .format(conf_path=self.env.conf_path))
                # Add on.
#                 r.sudo(
#                     "echo 'script.engine.groovy.inline.search: on' >> {conf_path}"\
#                         .format(conf_path=self.env.conf_path))
#                 r.append(
#                     text='script.engine.groovy.inline.search: on',
#                     filename=self.env.conf_path,
#                     use_sudo=True)
            else:
#                 r.sudo(
#                     "sed '/script.engine.groovy.inline.search: on/d' {conf_path}"\
#                         .format(conf_path=self.env.conf_path))
                r.sed(
                    filename=self.env.conf_path,
                    before='script.engine.groovy.inline.search: on',
                    after='script.engine.groovy.inline.search: off',
                    use_sudo=True,
                )

            self.enable()
            self.restart()
        else:
            self.disable()
            self.stop()

elasticsearch = ElasticSearchSatchel()
