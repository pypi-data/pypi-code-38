'''Meta command which draws a graph of chapters with Graphviz'''

import yaml

from pathlib import Path


from foliant.meta_commands.base import BaseMetaCommand
from foliant.meta_commands.generate import generate_meta

from .chapters_graph import ChaptersGraph


class MetaCommand(BaseMetaCommand):
    config_section = 'project_graph'

    def run(self, config_file_name='foliant.yml', project_path=Path('.')):
        self.logger.debug('Meta command draw started')

        meta_filename = generate_meta(self.context, self.logger)
        src_path = self.project_path / self.config['src_dir']

        with open(meta_filename) as f:
            chapters_meta = yaml.load(f)
        chapters = ChaptersGraph(chapters_meta,
                                 src_path=src_path.resolve(),
                                 config=self.options)
        chapters.draw()
        self.logger.debug('Meta command draw finished')
