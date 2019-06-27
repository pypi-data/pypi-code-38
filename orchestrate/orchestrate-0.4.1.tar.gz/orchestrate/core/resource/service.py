import shutil
import tempfile

import pkg_resources

from orchestrate.common import safe_format
from orchestrate.core.services.base import Service


class ResourceService(Service):
  def get_package_name(self, package):
    return safe_format('orchestrate.core.{}', package)

  def stream(self, package, resource):
    return pkg_resources.resource_stream(self.get_package_name(package), resource)

  def open(self, package, resource, **kwargs):
    contents_fp = tempfile.NamedTemporaryFile('wb+')
    with self.stream(package, resource) as source:
      shutil.copyfileobj(source, contents_fp)
    contents_fp.seek(0)
    return contents_fp

  def read(self, package, resource):
    return pkg_resources.resource_string(self.get_package_name(package), resource)
