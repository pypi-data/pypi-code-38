import os
import click

import dong.utils as utils
import dong.structure as structure

def init_project(project=None):
    if project:
        utils.create_directory(project)
        click.secho('Generate ML project:' + project + ' successful!', fg='green')

    opts = {}
    if not project:
        cwd = os.getcwd()
        opts['project'] = cwd.split(os.sep)[-1]
    else:
        opts['project'] = project
    opts['package'] = opts['project']

    struct = structure.define_structure(opts)
    structure.create_structure(struct, opts, project)

    # Cannot use new under the project folder
    # File already exists (same name) message should be beauty