# Copyright (c) 2019 Civic Knowledge. This file is licensed under the terms of the
# MIT License, included in this distribution as LICENSE

"""

"""

import copy
import json
import re
from datetime import datetime
from os.path import dirname, join, basename
from os.path import exists

from metapack.cli.core import prt, err
from metapack_jupyter.core import logger
from nbconvert.exporters.html import HTMLExporter
# from metapack.jupyter.markdown import MarkdownExporter
from nbconvert.writers import FilesWriter
from traitlets.config import Unicode, Config
from .preprocessors import AttachementOutputExtractor

class WordpressExporter(HTMLExporter):
    """ Export a python notebook to markdown, with frontmatter for Hugo.
    """

    staging_dir = Unicode(help="Root of the output directory").tag(config=True)

    @property
    def default_config(self):
        import metapack_jupyter.templates

        c = Config({

        })

        c.TemplateExporter.template_path = [dirname(metapack_jupyter.templates.__file__)]
        c.TemplateExporter.template_file = 'html_wordpress.tpl'

        c.HTMLExporter.preprocessors = [
            'metapack_jupyter.preprocessors.OrganizeMetadata',
            AttachementOutputExtractor
        ]

        c.merge(super(WordpressExporter, self).default_config)

        c.ExtractOutputPreprocessor.enabled = False

        return c

    def get_creators(self, meta):

        for typ in ('wrangler', 'creator'):
            try:
                # Multiple authors
                for e in meta[typ]:
                    d = dict(e.items())
                    d['type'] = typ

                    yield d
            except AttributeError:
                # only one
                d = meta[typ]
                d['type'] = typ
                yield d
            except KeyError:
                pass

    def from_notebook_node(self, nb, resources=None, **kw):
        from nbconvert.filters.highlight import Highlight2HTML
        import nbformat

        nb_copy = copy.deepcopy(nb)

        resources = self._init_resources(resources)

        if 'language' in nb['metadata']:
            resources['language'] = nb['metadata']['language'].lower()

        # Preprocess
        nb_copy, resources = self._preprocess(nb_copy, resources)

        # move over some more metadata
        if 'authors' not in nb_copy.metadata.frontmatter:
            nb_copy.metadata.frontmatter['authors'] = list(self.get_creators(nb_copy.metadata.metatab))

        # Other useful metadata
        if not 'date' in nb_copy.metadata.frontmatter:
            nb_copy.metadata.frontmatter['date'] = datetime.now().isoformat()

        resources.setdefault('raw_mimetypes', self.raw_mimetypes)

        resources['global_content_filter'] = {
            'include_code': not self.exclude_code_cell,
            'include_markdown': not self.exclude_markdown,
            'include_raw': not self.exclude_raw,
            'include_unknown': not self.exclude_unknown,
            'include_input': not self.exclude_input,
            'include_output': not self.exclude_output,
            'include_input_prompt': not self.exclude_input_prompt,
            'include_output_prompt': not self.exclude_output_prompt,
            'no_prompt': self.exclude_input_prompt and self.exclude_output_prompt,
        }

        langinfo = nb.metadata.get('language_info', {})
        lexer = langinfo.get('pygments_lexer', langinfo.get('name', None))
        self.register_filter('highlight_code',
                             Highlight2HTML(pygments_lexer=lexer, parent=self))

        def format_datetime(value, format='%a, %B %d'):
            from dateutil.parser import parse
            return parse(value).strftime(format)

        self.register_filter('parsedatetime', format_datetime)

        slug = nb_copy.metadata.frontmatter.slug

        # Rebuild all of the image names
        for cell_index, cell in enumerate(nb_copy.cells):
            for output_index, out in enumerate(cell.get('outputs', [])):

                if 'metadata' in out:
                    for type_name, fn in list(out.metadata.get('filenames', {}).items()):
                        if fn in resources['outputs']:
                            html_path = join(slug, basename(fn))
                            file_path = join(self.staging_dir, html_path)

                            resources['outputs'][file_path] = resources['outputs'][fn]
                            del resources['outputs'][fn]

                            # Can't put the '/' in the join() or it will be absolute

                            out.metadata.filenames[type_name] = '/' + html_path

        output = self.template.render(nb=nb_copy, resources=resources)

        # Don't know why this isn't being set from the config
        # resources['output_file_dir'] = self.config.NbConvertApp.output_base

        # Setting full path to subvert the join() in the file writer. I can't
        # figure out how to set the output directories from this function
        resources['unique_key'] = join(self.staging_dir, slug)

        # Probably should be done with a postprocessor.
        output = re.sub(r'__IMGDIR__', '/' + slug, output)

        output = re.sub(r'<style scoped.*?>(.+?)</style>', '', output, flags=re.MULTILINE | re.DOTALL)

        resources['outputs'][join(self.staging_dir, slug + '.json')] = \
            json.dumps(nb_copy.metadata, indent=4).encode('utf-8')

        resources['outputs'][join(self.staging_dir, slug + '.ipynb')] = nbformat.writes(nb_copy).encode('utf-8')

        return output, resources


def convert_wordpress(nb_path, wp_path):
    from pathlib import Path
    if not exists(nb_path):
        err("Notebook path does not exist: '{}' ".format(nb_path))

    c = Config()
    c.WordpressExporter.staging_dir = wp_path
    he = WordpressExporter(config=c, log=logger)

    output, resources = he.from_filename(nb_path)

    prt('Writing Notebook to Wordpress HTML')

    output_file = resources['unique_key'] + resources['output_extension']
    prt('    Writing ', output_file)

    resource_outputs = []

    for k, v in resources['outputs'].items():
        prt('    Writing ', k)
        resource_outputs.append(k)

    fw = FilesWriter()
    fw.build_directory  = str(Path(wp_path).parent)
    fw.write(output, resources, notebook_name=resources['unique_key'])

    return output_file, resource_outputs
