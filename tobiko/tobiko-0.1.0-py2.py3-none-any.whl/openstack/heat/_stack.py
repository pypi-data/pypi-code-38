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
import time

from heatclient import exc
from oslo_log import log

import tobiko
from tobiko.openstack.heat import _client
from tobiko.openstack.heat import _template


LOG = log.getLogger(__name__)

# Status
INIT_IN_PROGRESS = 'INIT_IN_PROGRESS'
INIT_COMPLETE = 'INIT_COMPLETE'
INIT_IN_PROGRESS = 'INIT_FAILED'
CREATE_IN_PROGRESS = 'CREATE_IN_PROGRESS'
CREATE_COMPLETE = 'CREATE_COMPLETE'
CREATE_FAILED = 'CREATE_FAILED'
DELETE_IN_PROGRESS = 'DELETE_IN_PROGRESS'
DELETE_COMPLETE = 'DELETE_COMPLETE'
DELETE_FAILED = 'DELETE_FAILED'


TEMPLATE_FILE_SUFFIX = '.yaml'


class HeatStackFixture(tobiko.SharedFixture):
    """Manages Heat stacks."""

    client = None
    client_fixture = None
    retry_create_stack = 1
    wait_interval = 5
    stack_name = None
    template = None
    template_fixture = None
    parameters = None
    stack = None

    def __init__(self, stack_name=None, template=None, parameters=None,
                 wait_interval=None, client=None):
        super(HeatStackFixture, self).__init__()
        self.stack_name = stack_name = (stack_name or
                                        self.stack_name or
                                        self.fixture_name)

        template = template or self.template
        if tobiko.is_fixture(template):
            self.template = None
            self.template_fixture = template
        elif isinstance(template, collections.Mapping):
            self.template = _template.HeatTemplate.from_dict(template)
            self.template_fixture = None
        elif template:
            msg = "Invalid type for template parameter: {!r}".format(template)
            raise TypeError(msg)
        self._parameters = parameters

        if tobiko.is_fixture(client):
            self.client_fixture = client
        elif client:
            self.client = client

        if wait_interval:
            self.wait_interval = wait_interval

    def setup_fixture(self):
        self.setup_template()
        self.setup_parameters()
        self.setup_client()
        self.setup_stack()

    def setup_template(self):
        template_fixture = self.template_fixture
        if template_fixture:
            self.template = tobiko.setup_fixture(template_fixture).template
        elif not self.template:
            template_name = self.stack_name.rsplit('.')[-1]
            self.template = _template.get_heat_template(
                template_file=(template_name + TEMPLATE_FILE_SUFFIX),
                template_dirs=[tobiko.get_fixture_dir(self)])

    def setup_parameters(self):
        self.parameters = {}
        # Merge all parameters dictionaries in the class hierarchy
        for cls in reversed(type(self).__mro__):
            parameters = cls.__dict__.get('parameters')
            if parameters:
                self.parameters.update(parameters)

        if self._parameters:
            self.parameters.update(self._parameters)

        # Add template's missing stack parameters
        if 'parameters' in self.template.template:
            for name in self.template.template['parameters']:
                if name not in self.parameters:
                    value = getattr(self, name, None)
                    if value is not None:
                        self.parameters[name] = value

    def setup_client(self):
        client_fixture = self.client_fixture
        if client_fixture:
            self.client = tobiko.setup_fixture(client_fixture).client
        elif not self.client:
            self.client = _client.get_heat_client()

    def setup_stack(self):
        self.create_stack()

    def create_stack(self, retry=None):
        """Creates stack based on passed parameters."""
        created_stack_ids = set()
        retry = retry or self.retry_create_stack or 1
        while True:
            stack = self.wait_for_stack_status(
                expected_status={CREATE_COMPLETE, CREATE_FAILED,
                                 CREATE_IN_PROGRESS, DELETE_COMPLETE,
                                 DELETE_FAILED})
            stack_status = getattr(stack, 'stack_status', DELETE_COMPLETE)
            expected_status = {CREATE_COMPLETE, CREATE_IN_PROGRESS}
            if stack_status in expected_status:
                LOG.debug('Stack created: %r (id=%r)', self.stack_name,
                          stack.id)
                for stack_id in created_stack_ids:
                    if self.stack.id != stack_id:
                        LOG.warning("Concurrent stack creation: delete "
                                    "duplicated stack is %r (id=%r).",
                                    self.stack_name, stack_id)
                        self.delete_stack(stack_id)

                return stack

            if not retry:
                status_reason = getattr(stack, 'stack_status_reason', None)
                raise HeatStackCreationFailed(name=self.stack_name,
                                              observed=stack_status,
                                              expected=expected_status,
                                              status_reason=status_reason)

            retry -= 1
            if stack_status.endswith('_FAILED'):
                LOG.debug('Delete existing failed stack: %r (id=%r)',
                          self.stack_name, stack.id)
                self.delete_stack()
                stack = self.wait_for_stack_status(
                    expected_status={DELETE_COMPLETE})

            self.stack = self._outputs = None
            try:
                LOG.debug('Creating stack %r (re-tries left %d)...',
                          self.stack_name, retry)
                stack_id = self.client.stacks.create(
                    stack_name=self.stack_name,
                    template=self.template.yaml,
                    parameters=self.parameters)['stack']['id']
            except exc.HTTPConflict:
                LOG.debug('Stack %r already exists.', self.stack_name)
            else:
                created_stack_ids.add(stack_id)
                LOG.debug('Creating stack %r (id=%r)...', self.stack_name,
                          stack_id)

    def cleanup_fixture(self):
        self.setup_client()
        self.cleanup_stack()

    def cleanup_stack(self):
        self.delete_stack()

    def delete_stack(self, stack_id=None):
        """Deletes stack."""
        if not stack_id:
            stack_id = self.stack_id
            self.stack = self._outputs = None
        try:
            self.client.stacks.delete(stack_id)
        except exc.NotFound:
            LOG.debug('Stack already deleted: %r (id=%r)', self.stack_name,
                      stack_id)
        else:
            LOG.debug('Deleting stack %r (id=%r)...', self.stack_name,
                      stack_id)

    @property
    def stack_id(self):
        stack = self.stack
        if stack:
            return stack.id
        else:
            return self.stack_name

    def get_stack(self, resolve_outputs=False):
        """Returns stack ID."""
        try:
            self.stack = stack = self.client.stacks.get(
                self.stack_name, resolve_outputs=resolve_outputs)
        except exc.HTTPNotFound:
            self.stack = stack = None
        finally:
            self._outputs = None
        return stack

    def wait_for_create_complete(self, check=True):
        return self.wait_for_stack_status(expected_status={CREATE_COMPLETE},
                                          check=check)

    def wait_for_delete_complete(self, check=True):
        return self.wait_for_stack_status(expected_status={DELETE_COMPLETE},
                                          check=check)

    def wait_for_stack_status(self, expected_status, check=True):
        """Waits for the stack to reach the given status."""
        stack = self.stack or self.get_stack()
        while (stack and stack.stack_status.endswith('_IN_PROGRESS') and
               stack.stack_status not in expected_status):
            LOG.debug("Waiting for %r (id=%r) stack status "
                      "(observed=%r, expected=%r)", self.stack_name,
                      stack.id, stack.stack_status, expected_status)
            time.sleep(self.wait_interval)
            stack = self.get_stack()

        if check:
            if stack is None:
                if DELETE_COMPLETE not in expected_status:
                    raise HeatStackNotFound(name=self.stack_name)
            else:
                check_stack_status(stack, expected_status)
        return stack

    _outputs = None

    @property
    def outputs(self):
        return self.wait_for_outputs()

    def get_outputs(self):
        stack = self.stack
        if not hasattr(stack, 'outputs'):
            stack = self.get_stack(resolve_outputs=True)
        check_stack_status(stack, {CREATE_COMPLETE})
        self._outputs = outputs = HeatStackOutputs(
            stack_name=self.stack_name,
            outputs={output['output_key']: output['output_value']
                     for output in stack.outputs})
        return outputs

    def wait_for_outputs(self):
        if self._outputs:
            return self._outputs
        else:
            self.wait_for_create_complete()
            return self.get_outputs()


class HeatStackOutputs(object):

    def __init__(self, stack_name, outputs):
        self.stack_name = stack_name
        self.outputs = outputs

    def __getattr__(self, name):
        try:
            return self.outputs[name]
        except KeyError:
            raise InvalidHeatStackOutputKey(name=self.stack_name,
                                            key=name)


def check_stack_status(stack, expected):
    observed = stack.stack_status
    if observed not in expected:
        if observed == CREATE_FAILED:
            error_class = HeatStackCreationFailed
        elif observed == DELETE_FAILED:
            error_class = HeatStackDeletionFailed
        else:
            error_class = InvalidHeatStackStatus
        raise error_class(name=stack.stack_name,
                          observed=observed,
                          expected=expected,
                          status_reason=stack.stack_status_reason)


class InvalidHeatStackOutputKey(tobiko.TobikoException):
    message = "output key {key!r} not found in stack {name!r}"


class HeatStackNotFound(tobiko.TobikoException):
    message = "stack {name!r} not found"


class InvalidHeatStackStatus(tobiko.TobikoException):
    message = ("stack {name!r} status {observed!r} not in {expected!r}\n"
               "{status_reason!s}")


class HeatStackCreationFailed(InvalidHeatStackStatus):
    pass


class HeatStackDeletionFailed(InvalidHeatStackStatus):
    pass
