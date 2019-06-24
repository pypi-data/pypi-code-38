from .base import BaseProcessor

import markdown2

template = """
{{% extends('{template}') %}}
{{% block article %}}
{content}
{{% endblock %}}
"""

class MarkdownProcessor(BaseProcessor):

    def process(self, input, vars):
        #we add an offset if requested
        if self.params.get('h-offset') is not None:
            offset = self.params['h-offset']
            lines = input.split('\n')
            input = ""
            for line in lines:
                if line.startswith('#'):
                    line = '#'*offset+line
                input += line + "\n"
        result = markdown2.markdown(input, extras=['footnotes','fenced-code-blocks'])
        if self.params.get('bare'):
            return result
        template_filename = self.params.get('template', 'article.html')
        template_result = template.format(template=template_filename, content=result)
        return template_result