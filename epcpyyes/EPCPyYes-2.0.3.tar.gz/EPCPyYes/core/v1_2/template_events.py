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
# Copyright 2018 Rob Magee.  All rights reserved.
'''
The templates package contains classes derived from the core EPCIS classes
along with Jinja2 templates for generating EPCIS event XML.  By calling any
classes' `render` function, you can obtain the output of the Jinja2 template
associated with the current class.  There are examples of this in the
*Usage* section of this documentation.
'''
from typing import List
from datetime import datetime

from EPCPyYes.core.v1_2 import events
from EPCPyYes.core.v1_2.events import Action, ErrorDeclaration
from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import \
    InstanceLotMasterDataAttribute
from EPCPyYes.core.SBDH.sbdh import StandardBusinessDocumentHeader as sbdh
from EPCPyYes.core.v1_2.json_encoders import JSONFormatMixin
from EPCPyYes.core.v1_2 import json_encoders
from jinja2 import Environment, PackageLoader


def _load_default_environment():
    '''
    Loads up the default Jinja2 environment so simple template names can
    be passed in.

    :return: The defualt Jinja2 environment for this package.
    '''
    return Environment(loader=PackageLoader('EPCPyYes', 'templates'),
                       extensions=['jinja2.ext.with_'], trim_blocks=True,
                       lstrip_blocks=True)


class TemplateMixin(JSONFormatMixin):
    '''
    Mixin class to add template support for serializing EPCIS classes to
    text using jinja templates.
    '''

    def __init__(self, *args, **kwargs):
        '''
        Will render an object event using the default 'object_event.xml'
        template or you can pass in a Jinja2 template along with a new
        Jinja2 enviornment as well if you wish.

        :param args:
        :param kwargs: env = a jinja2 Environment, template = a string
            representing the template in either the default or passed in Jinja2
            environment and render_xml_declaration which is a bool value
            used to determine whether or not to render an xml declaration during
            template rendering.  It is populated as a jinja context variable.
        '''
        # env: Environment = None, template: str = None
        self._env = kwargs.get('env') or _load_default_environment()
        self._template = kwargs.get('template')
        self._render_xml_declaration = kwargs.get('render_xml_declaration',
                                                  False)
        self._context = {'event': self,
                         'render_xml_declaration': self._render_xml_declaration}

    @property
    def template(self):
        '''
        :return: Returns a Jinja2 Template instance.
        '''
        return self._template

    @template.setter
    def template(self, value: str):
        '''
        Pass in the name of a template that has been loaded into the
        jinja2 Environment class used to intialize this mixin.

        :param value: The name of the template to load.
        :return: None
        '''
        self._template = self._env.get_template(value)
        self._template.new_context(self._context)

    @property
    def namespaces(self):
        '''
        Override to provide a list of XML namespace declarations for inclusion
        in the EPCIS body root node.

        :return: An empty list.
        '''
        return []

    def render(self):
        '''
        Renders the Class template using the _context dictionary for the
        template context.

        :param: render_namespaces: A boolean value passed into the
        template as a context variable.  Used by the default templates
        to determine whether or not to declare the XML namespaces in the
        root element.
        '''
        return self._template.render(**self._context)


TemplateEventList = List[TemplateMixin]


class ObjectEvent(events.ObjectEvent, TemplateMixin):
    '''
    Used to render an ObjectEvent using the Jinja2 environment and template
    associated with the class.  The default environment utilizes the
    `templates` directory in the root folder of the package.
    '''

    def __init__(self, event_time: datetime = datetime.utcnow().isoformat(),
                 event_timezone_offset: str = '+00:00',
                 record_time: datetime = None,
                 action: str = Action.add.value,
                 epc_list: list = None, biz_step=None, disposition=None,
                 read_point=None, biz_location=None, event_id: str = None,
                 error_declaration: ErrorDeclaration = None,
                 source_list: list = None, destination_list: list = None,
                 business_transaction_list: list = None, ilmd: list = None,
                 quantity_list: list = None, env: Environment = None,
                 template: str = None, render_xml_declaration=None):
        super().__init__(event_time, event_timezone_offset, record_time,
                         action, epc_list, biz_step, disposition, read_point,
                         biz_location, event_id, error_declaration,
                         source_list, destination_list,
                         business_transaction_list, ilmd, quantity_list)
        kwargs = {'env': env,
                  'template': template,
                  'render_xml_declaration': render_xml_declaration
                  }
        TemplateMixin.__init__(self, **kwargs)
        template = template or 'epcis/object_event.xml'
        self.template = self._env.get_template(template)
        self.encoder = json_encoders.ObjectEventEncoder()

    @property
    def namespaces(self):
        '''
        If there are any CBV ILMD attributes, we'll need to expose the
        namespace for any XML generation.  Override to provide custom
        XML namespaces if needed.
        :return: A full string of the namespace declaration for use in
        an XML root node.
        '''
        ret = []
        if self.ilmd:
            for ilmd_item in self.ilmd:
                if isinstance(ilmd_item, InstanceLotMasterDataAttribute):
                    ret.append('xmlns:cbvmd="urn:epcglobal:cbv:mda"')
                    break
        return ret


class AggregationEvent(events.AggregationEvent, TemplateMixin):
    '''
    Generates an EPCIS Aggregation Event.
    '''

    def __init__(self, event_time: datetime = datetime.utcnow().isoformat(),
                 event_timezone_offset: str = '+00:00',
                 record_time: datetime = None,
                 action: str = Action.add.value,
                 parent_id: str = None, child_epcs: list = None,
                 child_quantity_list: list = None, biz_step: str = None,
                 disposition: str = None, read_point: str = None,
                 biz_location: str = None, event_id: str = None,
                 error_declaration: ErrorDeclaration = None, source_list=None,
                 destination_list=None, business_transaction_list=None,
                 env: Environment = None,
                 template: str = None, render_xml_declaration=None
                 ):
        '''
        Creates a new EPCIS AggregationEvent instance.

        :param event_time: The date and time at which the EPCIS Capturing
            Applications asserts the event occurred.
        :param event_timezone_offset: The time zone offset in effect at the
            time and place the event occurred, expressed as an offset from UTC.
        :param action: How this event relates to the lifecycle of the
            aggregation named in this event.
        :param parent_id: (Optional when action is OBSERVE, required otherwise)
            The identifier of the parent of the association
        :param child_epcs: An unordered list of the EPCs of contained
            objects identified by instance-level identifiers.
        :param child_quantity_list: An unordered list of one or more
            QuantityElements identifying (at the class level) contained objects
        :param biz_step: The business step of which this event was a part.
        :param disposition: The business condition of the objects associated
            with the EPCs, presumed to hold true until contradicted by a
            subsequent event.
        :param read_point: The read point at which the event took place.
        :param biz_location: The business location where the objects
            associated with the containing and contained EPCs may be found,
            until contradicted by a subsequent event.
        :param event_id: (Optional) An identifier for this event as specified
            by the capturing application, globally unique across all events
            other than error declarations.
        :param error_declaration:  If present, indicates that this event
            serves to assert that the assertions made by a prior event are
            in error. See Section 7.4.1.2.
        :param source_list: An unordered list of Source elements (Section 7.3.5.4)
            that provide context about the originating endpoint of a business
            transfer of which this event is a part.
        :param destination_list:  An unordered list of Destination elements
            (Section 7.3.5.4) that provide context about the terminating
            endpoint of a business transfer of which this event is a part
        :param business_transaction_list: An unordered list of business
            transactions that define the context of this event.
        '''
        super().__init__(event_time, event_timezone_offset, record_time,
                         action, parent_id, child_epcs, child_quantity_list,
                         biz_step, disposition, read_point, biz_location,
                         event_id, error_declaration, source_list,
                         destination_list, business_transaction_list)
        kwargs = {'env': env,
                  'template': template,
                  'render_xml_declaration': render_xml_declaration
                  }
        TemplateMixin.__init__(self, **kwargs)
        self._template = self._env.get_template('epcis/aggregation_event.xml')
        self.encoder = json_encoders.AggregationEventEncoder()


class TransactionEvent(events.TransactionEvent, TemplateMixin):
    def __init__(self, event_time: datetime = datetime.utcnow().isoformat(),
                 event_timezone_offset: str = '+00:00',
                 record_time: datetime = None,
                 action: str = Action.add.value,
                 parent_id: str = None, epc_list: list = None,
                 biz_step: str = None, disposition: str = None,
                 read_point: str = None, biz_location: str = None,
                 event_id: str = None,
                 error_declaration: ErrorDeclaration = None, source_list=None,
                 destination_list=None, business_transaction_list=None,
                 quantity_list: list = None, env: Environment = None,
                 template: str = None, render_xml_declaration=None):
        super().__init__(event_time, event_timezone_offset, record_time,
                         action, parent_id, epc_list, biz_step, disposition,
                         read_point, biz_location, event_id, error_declaration,
                         source_list, destination_list,
                         business_transaction_list, quantity_list)
        kwargs = {'env': env,
                  'template': template,
                  'render_xml_declaration': render_xml_declaration
                  }
        TemplateMixin.__init__(self, **kwargs)
        self.template = 'epcis/transaction_event.xml'
        self.encoder = json_encoders.TransactionEventEncoder()


class TransformationEvent(events.TransformationEvent, TemplateMixin):
    def __init__(self, event_time: datetime = datetime.utcnow().isoformat(),
                 event_timezone_offset: str = '+00:00',
                 record_time: datetime = None,
                 event_id: str = None,
                 input_epc_list=None, input_quantity_list=None,
                 output_epc_list=None, output_quantity_list=None,
                 transformation_id=None, biz_step: str = None,
                 disposition: str = None, read_point: str = None,
                 biz_location: str = None, business_transaction_list=None,
                 source_list=None, destination_list=None, ilmd=None,
                 error_declaration: ErrorDeclaration = None,
                 env: Environment = None,
                 template: str = None, render_xml_declaration=None
                 ):
        super().__init__(event_time, event_timezone_offset, record_time,
                         event_id, input_epc_list, input_quantity_list,
                         output_epc_list, output_quantity_list,
                         transformation_id, biz_step, disposition, read_point,
                         biz_location, business_transaction_list, source_list,
                         destination_list, ilmd, error_declaration)
        kwargs = {'env': env,
                  'template': template,
                  'render_xml_declaration': render_xml_declaration
                  }
        TemplateMixin.__init__(self, **kwargs)
        self.template = 'epcis/transformation_event.xml'
        self.encoder = json_encoders.TransformationEventEncoder()


class EPCISDocument(events.EPCISDocument, TemplateMixin):
    def __init__(self,
                 header: sbdh = None,
                 object_events: list = [], aggregation_events: list = [],
                 transaction_events: list = [],
                 transformation_events: list = [],
                 render_xml_declaration: bool = False,
                 created_date: str = None,
                 template: str = 'epcis/epcis_document.xml'):
        super().__init__(header, object_events, aggregation_events,
                         transaction_events,
                         transformation_events, render_xml_declaration,
                         created_date)
        TemplateMixin.__init__(self)
        self._template = self._env.get_template(template)
        self.encoder = json_encoders.EPCISDocumentEncoder()

    def render(self, render_namespaces=False, render_xml_declaration=False):
        context = {'header': self.header,
                   'object_events': self.object_events,
                   'aggregation_events': self.aggregation_events,
                   'transaction_events': self.transaction_events,
                   'transformation_events': self.transformation_events,
                   'created_date': self.created_date,
                   'render_xml_declaration': self.render_xml_declaration,
                   }
        return self._template.render(**context)


class EPCISEventListDocument(events.EPCISDocument, TemplateMixin):
    '''
    This template event of the EPCISDocument type allows you to specify
    a generic list of EPCPyYes events of any type in any order- as opposed
    to the EPCISDocument template class in this same module which has separate
    lists for each event type.

    The EPCISEventListDocument has a single list called
    `template_events` which can be supplied in the constructor or
    can be accessed via the property of the same name.  The class must
    be initialized, however, with at least one event in the
    `template_events` parameter.
    '''

    def __init__(self, template_events: TemplateEventList,
                 header: sbdh = None,
                 render_xml_declaration: bool = True,
                 created_date: str = None,
                 render_namespaces=False,
                 template='epcis/epcis_events_document.xml',
                 additional_context:dict = None):
        '''
        Initializes the class with at least one event in the
        `template_events` paramter.
        :param template_events: A list of
        `EPCPyYes.core.v1_2.template_event.TemplateMixin` objects.
        :param header: An EPCPyYes SBDH object.
        :param render_xml_declaration:
        :param created_date: Created date or the current UTC now.
        :param render_namespaces: Whether or not to render namespaces in the
        header. Default = False
        :param template: The Jinja2 template path. Default is
        `epcis/epcis_events_document.xml`
        '''
        super().__init__(header=header,
                         render_xml_declaration=render_xml_declaration,
                         created_date=created_date)
        TemplateMixin.__init__(self)
        self._template_events = template_events
        self._render_namespaces = render_namespaces
        self._template = self._env.get_template(template)
        self.encoder = json_encoders.EPCISDocumentEncoder()
        self.additional_context = additional_context

    def render(self):
        # we remove transformation events from the main event
        # list since they must go into the <extension> element.
        for event in self.template_events:
            if isinstance(event, TransformationEvent):
                self.transformation_events.append(event)
                self.template_events.remove(event)
        context = {
            'header': self.header,
            'template_events': self.template_events,
            'transformation_events': self.transformation_events,
            'render_namespaces': self._render_namespaces,
            'render_xml_declaration': self.render_xml_declaration,
            'created_date': self.created_date,
            'additional_context': self.additional_context
        }
        return self._template.render(**context)

    @property
    def template_events(self):
        return self._template_events

    @template_events.setter
    def template_events(self, value):
        self._template_events = value
