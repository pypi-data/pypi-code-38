import re

import pytest
from mock import Mock

from orchestrate.core.resource.service import ResourceService
from orchestrate.core.template.service import TemplateService


class TestTemplateService(object):
  @pytest.fixture
  def template_service(self):
    services = Mock()
    services.resource_service = ResourceService(services)
    return TemplateService(services)

  def test_config_map(self, template_service):
    role_config_map = template_service.render_template_from_file('eks/config_map.yml.ms', dict(
      node_roles=[dict(arn="NODE_ROLE_ARN")],
      cluster_access_role=dict(
        arn="CLUSTER_ROLE_ARN",
        name="CLUSTER_ROLE_NAME",
      ),
    ))
    assert re.search(r'\s+(- )?rolearn: NODE_ROLE_ARN', role_config_map)
    assert re.search(r'\s+(- )?rolearn: CLUSTER_ROLE_ARN', role_config_map)
    assert re.search(r'\s+(- )?username: CLUSTER_ROLE_NAME', role_config_map)
