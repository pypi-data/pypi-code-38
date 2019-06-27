import pystache

from orchestrate.core.services.base import Service


class TemplateService(Service):
  def render_template_from_file(self, relative_filename, template_args):
    template = self.services.resource_service.read('template', relative_filename)
    return pystache.render(template, template_args)
