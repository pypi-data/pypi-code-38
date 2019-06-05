# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import collections
import os
import time

from heatclient.v1 import client as heatclient
from heatclient import exc
import mock
import yaml

import tobiko
from tobiko.openstack import heat
from tobiko.openstack import keystone
from tobiko.tests.unit import openstack


class MyStack(heat.HeatStackFixture):
    pass


class MyStackWithStackName(heat.HeatStackFixture):
    stack_name = 'stack.name.from.class'


class MyStackWithParameters(heat.HeatStackFixture):
    parameters = {'param': 'from-class'}


class MyStackWithTemplate(heat.HeatStackFixture):
    template = {'template': 'from-class'}


class MyStackWithWaitInterval(heat.HeatStackFixture):
    wait_interval = 10


class MyTemplateFixture(tobiko.SharedFixture):

    _template = {'template': 'from-class'}
    template = None

    def __init__(self, template=None):
        super(MyTemplateFixture, self).__init__()
        if template:
            self._template = template

    def setup_fixture(self):
        self.template = heat.HeatTemplate.from_dict(self._template)


class HeatStackFixtureTest(openstack.OpenstackTest):

    def test_init(self, fixture_class=MyStack, stack_name=None, template=None,
                  parameters=None, wait_interval=None, client=None):
        stack = fixture_class(stack_name=stack_name, template=template,
                              parameters=parameters,
                              wait_interval=wait_interval, client=client)

        self.assertEqual(stack_name or fixture_class.stack_name or
                         tobiko.get_fixture_name(stack),
                         stack.stack_name)

        if tobiko.is_fixture(template):
            self.assertIsNone(stack.template)
            self.assertIs(template, stack.template_fixture)
        elif isinstance(template, collections.Mapping):
            self.assertEqual(
                heat.HeatTemplate.from_dict(template=template),
                stack.template)
            self.assertIsNone(stack.template_fixture)
        elif template:
            self.assertIs(template, stack.template)
            self.assertIsNone(stack.template_fixture)
        else:
            self.assertIsNone(stack.template)
            self.assertIsNone(stack.template_fixture)

        self.assertIs(fixture_class.parameters, stack.parameters)

        self.assertEqual(wait_interval or fixture_class.wait_interval,
                         stack.wait_interval)

        if tobiko.is_fixture(client):
            self.assertIsNone(stack.client)
            self.assertIs(client, stack.client_fixture)
        elif client:
            self.assertIs(client, stack.client)
            self.assertIsNone(stack.client_fixture)
        else:
            self.assertIsNone(stack.client)
            self.assertIsNone(stack.client_fixture)

    def test_init_with_stack_name(self):
        self.test_init(stack_name='my-stack-name')

    def test_init_with_stack_name_from_class(self):
        self.test_init(fixture_class=MyStackWithStackName)

    def test_init_with_template(self):
        self.test_init(template={'some': 'template'})

    def test_init_with_template_fixture(self):
        self.test_init(template=MyTemplateFixture())

    def test_init_with_parameters(self):
        self.test_init(parameters={'my': 'value'})

    def test_init_with_parameters_from_class(self):
        self.test_init(fixture_class=MyStackWithParameters)

    def test_init_with_wait_interval(self):
        self.test_init(wait_interval=20)

    def test_init_with_wait_interval_from_class(self):
        self.test_init(fixture_class=MyStackWithWaitInterval)

    def test_init_with_client(self):
        session = keystone.get_keystone_session()
        self.test_init(client=heatclient.Client(session=session))

    def test_init_with_client_fixture(self):
        self.test_init(client=heat.HeatClientFixture())

    def test_setup(self, fixture_class=MyStack, stack_name=None,
                   template=None, parameters=None, wait_interval=None,
                   stacks=None, create_conflict=False,
                   call_create=True, call_delete=False, call_sleep=False):
        from tobiko.openstack.heat import _client
        from tobiko.openstack.heat import _template

        client = mock.MagicMock(specs=heatclient.Client)
        get_heat_client = self.patch(_client, 'get_heat_client',
                                     return_value=client)

        stacks = stacks or [
            exc.HTTPNotFound,
            mock_stack('CREATE_IN_PROGRESS')]
        client.stacks.get.side_effect = stacks

        if create_conflict:
            client.stacks.create.side_effect = exc.HTTPConflict
        else:
            client.stacks.create.return_value = {
                'stack': {'id': '<stack-id>'}}

        sleep = self.patch(time, 'sleep')
        stack = fixture_class(stack_name=stack_name, parameters=parameters,
                              template=template, wait_interval=wait_interval)

        default_template = heat.HeatTemplate.from_dict(
            {'default': 'template'})
        get_heat_template = self.patch(_template, 'get_heat_template',
                                       return_value=default_template)

        stack.setUp()

        self.assertIs(client, stack.client)
        self.assertEqual(wait_interval or fixture_class.wait_interval,
                         stack.wait_interval)
        get_heat_client.assert_called_once_with()
        client.stacks.get.assert_has_calls([mock.call(stack.stack_name,
                                                      resolve_outputs=False)])

        if call_delete:
            client.stacks.delete.assert_called_once_with(stack.stack_id)
        else:
            client.stacks.delete.assert_not_called()

        self.assertEqual(parameters or fixture_class.parameters or {},
                         stack.parameters)
        if call_create:
            client.stacks.create.assert_called_once_with(
                parameters=stack.parameters, stack_name=stack.stack_name,
                template=yaml.safe_dump(stack.template.template))
        else:
            client.stacks.create.assert_not_called()

        if call_sleep:
            sleep.assert_has_calls([mock.call(stack.wait_interval)])

        if tobiko.is_fixture(template):
            self.assertIs(tobiko.get_fixture(template).template,
                          stack.template)
        elif isinstance(template, collections.Mapping):
            self.assertEqual(heat.HeatTemplate.from_dict(template),
                             stack.template)
        elif isinstance(template, heat.HeatTemplate):
            self.assertIs(template, stack.template)
        elif not template:
            if fixture_class.template:
                self.assertEqual(
                    heat.HeatTemplate.from_dict(fixture_class.template),
                    stack.template)
            else:
                self.assertEqual(default_template, stack.template)
        else:
            self.fail("Unsupported template type: {!r}".format(template))

        if template or fixture_class.template:
            get_heat_template.assert_not_called()
        else:
            template_file_name = stack.stack_name.rsplit('.', 1)[-1] + '.yaml'
            get_heat_template.assert_called_once_with(
                template_file=template_file_name,
                template_dirs=[os.path.dirname(__file__)])

    def test_setup_with_stack_name(self):
        self.test_setup(stack_name='my-stack-name')

    def test_setup_with_stack_name_from_class(self):
        self.test_setup(fixture_class=MyStackWithStackName)

    def test_setup_with_template(self):
        self.test_setup(template={'other': 'template'})

    def test_setup_with_template_from_class(self):
        self.test_setup(fixture_class=MyStackWithTemplate)

    def test_setup_with_template_fixture(self):
        self.test_setup(template=MyTemplateFixture(template={'template':
                                                             'from-fixture'}))

    def test_setup_with_template_fixture_type(self):
        self.test_setup(template=MyTemplateFixture)

    def test_setup_with_parameters(self):
        self.test_setup(parameters={'from_init': True})

    def test_setup_with_parameters_from_class(self):
        self.test_setup(fixture_class=MyStackWithParameters)

    def test_setup_with_wait_interval(self):
        self.test_setup(wait_interval=10.)

    def test_setup_with_wait_interval_from_class(self):
        self.test_setup(fixture_class=MyStackWithWaitInterval)

    def test_setup_when_delete_completed(self):
        self.test_setup(stacks=[mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')])

    def test_setup_when_delete_failed(self):
        self.test_setup(stacks=[mock_stack('DELETE_FAILED'),
                                mock_stack('DELETE_IN_PROGRESS'),
                                mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')],
                        call_delete=True, call_sleep=True)

    def test_setup_when_delete_failed_fast_delete(self):
        self.test_setup(stacks=[mock_stack('DELETE_FAILED'),
                                mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')],
                        call_delete=True)

    def test_setup_when_create_complete(self):
        self.test_setup(stacks=[mock_stack('CREATE_COMPLETE')],
                        call_create=False)

    def test_setup_when_create_failed(self):
        self.test_setup(stacks=[mock_stack('CREATE_FAILED'),
                                mock_stack('DELETE_IN_PROGRESS'),
                                mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')],
                        call_delete=True, call_sleep=True)

    def test_setup_when_create_failed_fast_delete(self):
        self.test_setup(stacks=[mock_stack('CREATE_FAILED'),
                                mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')],
                        call_delete=True)

    def test_setup_when_create_in_progress(self):
        self.test_setup(stacks=[mock_stack('CREATE_IN_PROGRESS')],
                        call_create=False)

    def test_setup_when_delete_in_progress_then_complete(self):
        self.test_setup(stacks=[mock_stack('DELETE_IN_PROGRESS'),
                                mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')],
                        call_sleep=True)

    def test_setup_when_delete_in_progress_then_failed(self):
        self.test_setup(stacks=[mock_stack('DELETE_IN_PROGRESS'),
                                mock_stack('DELETE_FAILED'),
                                mock_stack('DELETE_COMPLETE'),
                                mock_stack('CREATE_IN_PROGRESS')],
                        call_sleep=True, call_delete=True)

    def test_setup_when_create_conflict(self):
        self.test_setup(create_conflict=True)

    def test_cleanup(self):
        client = mock.MagicMock(specs=heatclient.Client)
        stack = MyStack(client=client)
        stack.cleanUp()
        client.stacks.delete.assert_called_once_with(stack.stack_name)

    def test_get_outputs(self):
        stack = mock_stack(status='CREATE_COMPLETE',
                           outputs=[{'output_key': 'key1',
                                     'output_value': 'value1'},
                                    {'output_key': 'key2',
                                     'output_value': 'value2'}])
        client = mock.MagicMock(specs=heatclient.Client)
        client.stacks.get.return_value = stack
        stack_fixture = MyStack(client=client)

        outputs = stack_fixture.get_outputs()

        client.stacks.get.assert_called_once_with(stack_fixture.stack_name,
                                                  resolve_outputs=True)
        self.assertEqual('value1', outputs.key1)
        self.assertEqual('value2', outputs.key2)


def mock_stack(status, stack_id='<stack-id>', outputs=None):
    return mock.MagicMock(stack_status=status,
                          id=stack_id,
                          outputs=outputs or [])
