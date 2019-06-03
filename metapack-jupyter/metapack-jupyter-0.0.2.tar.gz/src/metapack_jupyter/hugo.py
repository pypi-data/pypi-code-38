# Copyright (c) 2019 Civic Knowledge. This file is licensed under the terms of the
# MIT License, included in this distribution as LICENSE

"""

"""

import copy
import json
import re
from datetime import datetime
from metapack.cli.core import prt, err
from metapack_jupyter.core import logger
from nbconvert.exporters.html import HTMLExporter
# from metapack.jupyter.markdown import MarkdownExporter
from nbconvert.exporters.markdown import MarkdownExporter

from nbconvert.writers import FilesWriter
from os.path import dirname, join, basename
from os.path import exists
from traitlets import default
from traitlets.config import Unicode, Config



class HugoExporter(MarkdownExporter):
    """ Export a python notebook to markdown, with frontmatter for Hugo. Not much of this is particular to
    Metapack.

    The Frontmatter is contained in a cell of type RawNBConvert, tagged with the tag 'frontmatter', and
    formatted in YAML. For instance

        https://github.com/sandiegodata/notebooks/blob/master/crime/Crime%20Monthly%20Rhythm%20Maps.ipynb

    Has this frontmatter:

        draft: false
        weight: 3
        description: Rhythm maps for San Diego Crime incidents, from 2007 to 2014
        toc: false
        show_input: hide
        section: notebooks
        authors:
        - name: Eric Busboom
        github: https://github.com/sandiegodata/notebooks/blob/master/crime/Crime%20Monthly%20Rhythm%20Maps.ipynb

    """

    hugo_dir = Unicode(help="Root of the Hugo directory").tag(config=True)

    section = Unicode(help="Hugo section in which to write the converted notebook").tag(config=True)

    @default('section')
    def _section_file_default(self):
        return 'notebooks'

    @property
    def default_config(self):
        import metapack.jupyter.templates

        c = Config({

        })

        c.TemplateExporter.template_path = [dirname(metapack.jupyter.templates.__file__)]
        c.TemplateExporter.template_file = 'markdown_hugo.tpl'

        c.MarkdownExporter.preprocessors = [
            'metapack.jupyter.preprocessors.OrganizeMetadata',
            HugoOutputExtractor
        ]

        c.merge(super(HugoExporter, self).default_config)

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

        slug = nb_copy.metadata.frontmatter.slug

        # Rebuild all of the image names
        for cell_index, cell in enumerate(nb_copy.cells):
            for output_index, out in enumerate(cell.get('outputs', [])):

                if 'metadata' in out:
                    for type_name, fn in list(out.metadata.get('filenames', {}).items()):
                        if fn in resources['outputs']:
                            html_path = join('img', slug, basename(fn))
                            file_path = join(self.hugo_dir, 'static', html_path)

                            resources['outputs'][file_path] = resources['outputs'][fn]
                            del resources['outputs'][fn]

                            # Can't put the '/' in the join() or it will be absolute

                            out.metadata.filenames[type_name] = '/' + html_path

        output = self.template.render(nb=nb_copy, resources=resources)

        section = nb_copy.metadata.frontmatter.get('section') or self.section

        # Don't know why this isn't being set from the config
        # resources['output_file_dir'] = self.config.NbConvertApp.output_base

        # Setting full path to subvert the join() in the file writer. I can't
        # figure out how to set the output directories from this function
        resources['unique_key'] = join(self.hugo_dir, 'content', section, slug)

        # Probably should be done with a postprocessor.
        output = re.sub(r'__IMGDIR__', join('/img', slug), output)

        return output, resources


def convert_hugo(nb_path, hugo_path):
    from os import environ
    from os.path import abspath

    # Total hack. Would like the -H to be allowed to have no arg, and then use the env var,
    # but I don't know how to do that. This is the case where the user types
    # -H nb_path, so just go with it.
    if hugo_path and not nb_path:
        nb_path = hugo_path
        hugo_path = environ.get('METAPACK_HUGO_DIR')

    if not hugo_path:
        err("Must specify value for -H or the METAPACK_HUGO_DIR environment var")

    if not exists(nb_path):
        err("Notebook path does not exist: '{}' ".format(nb_path))

    c = Config()
    c.HugoExporter.hugo_dir = abspath(hugo_path)  # Exports assume rel path is rel to notebook
    he = HugoExporter(config=c, log=logger)

    output, resources = he.from_filename(nb_path)

    prt('Writing Notebook to Hugo Markdown')

    prt('    Writing ', resources['unique_key'] + resources['output_extension'])
    for k, v in resources['outputs'].items():
        prt('    Writing ', k)

    fw = FilesWriter()
    fw.write(output, resources, notebook_name=resources['unique_key'])


