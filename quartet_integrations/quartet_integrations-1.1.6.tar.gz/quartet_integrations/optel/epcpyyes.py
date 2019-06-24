# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
from datetime import datetime

from jinja2.environment import Environment
from jinja2.loaders import ChoiceLoader, PackageLoader

from EPCPyYes.core.v1_2 import template_events
from EPCPyYes.core.v1_2.events import ErrorDeclaration, Action


def get_default_environment():
    '''
    Loads up the default Jinja2 environment so simple template names can
    be passed in.  This includes the local templates on top of the
    existing EPCPyYes templates.

    :return: The defualt Jinja2 environment for this package.
    '''
    loader = ChoiceLoader(
        [
            PackageLoader('EPCPyYes', 'templates'),
            PackageLoader('quartet_integrations', 'templates')
        ]
    )
    env = Environment(loader=loader,
                      extensions=['jinja2.ext.with_'], trim_blocks=True,
                      lstrip_blocks=True)
    return env


class ObjectEvent(template_events.ObjectEvent):

    def __init__(self, event_time: datetime = datetime.utcnow().isoformat(),
                 event_timezone_offset: str = '+00:00',
                 record_time: datetime = None, action: str = Action.add.value,
                 epc_list: list = None, biz_step=None, disposition=None,
                 read_point=None, biz_location=None, event_id: str = None,
                 error_declaration: ErrorDeclaration = None,
                 source_list: list = None, destination_list: list = None,
                 business_transaction_list: list = None, ilmd: list = None,
                 quantity_list: list = None, env: Environment = None,
                 template: str = None, render_xml_declaration=None):
        env = get_default_environment()
        template = 'optel/object_event.xml'
        super().__init__(event_time, event_timezone_offset, record_time,
                         action, epc_list, biz_step, disposition, read_point,
                         biz_location, event_id, error_declaration,
                         source_list, destination_list,
                         business_transaction_list, ilmd, quantity_list, env,
                         template, render_xml_declaration)

