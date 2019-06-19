#!/usr/bin/env python

import os
import shutil
import datetime

import click
import jinja2
import pkg_resources

from . import bdt

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


def copy_file(template, output_dir):
  '''Copies a file from the template directory to the output directory

  Args:

    template: The path to the template, from the internal templates directory
    output_dir: Where to save the output
  '''

  template_file = pkg_resources.resource_filename(__name__, os.path.join('..',
    'templates', template))
  output_file = os.path.join(output_dir, template)

  basedir = os.path.dirname(output_file)
  if not os.path.exists(basedir):
    logger.info('mkdir %s', basedir)
    os.makedirs(basedir)

  logger.info('cp -a %s %s', template_file, output_file)
  shutil.copy2(template_file, output_file)


def render_template(jenv, template, context, output_dir):
  '''Renders a template to the output directory using specific context

  Args:

    jenv: The Jinja2 environment to use for rendering the template
    template: The path to the template, from the internal templates directory
    context: A dictionary with the context to render the template with
    output_dir: Where to save the output
  '''

  output_file = os.path.join(output_dir, template)

  basedir = os.path.dirname(output_file)
  if not os.path.exists(basedir):
    logger.info('mkdir %s', basedir)
    os.makedirs(basedir)

  with open(output_file, 'wt') as f:
    logger.info('rendering %s', output_file)
    T = jenv.get_template(template)
    f.write(T.render(**context))


@click.command(epilog='''
Examples:

  1. Generates a new project for Bob:

     $ bdt new -vv bob/bob.newpackage "John Doe" "joe@example.com"
''')
@click.argument('package')
@click.argument('author')
@click.argument('email')
@click.option('-t', '--title', show_default=True,
    default='New package', help='This entry defines the package title. ' \
        'The package title should be a few words only.  It will appear ' \
        'at the description of your package and as the title of your ' \
        'documentation')
@click.option('-l', '--license', type=click.Choice(['bsd', 'gplv3']),
    default='gplv3', show_default=True,
    help='Changes the default licensing scheme to use for your package')
@click.option('-o', '--output-dir', help='Directory where to dump the new ' \
          'project - must not exist')
@verbosity_option()
@bdt.raise_on_error
def new(package, author, email, title, license, output_dir):
    """Creates a folder structure for a new Bob/BEAT package
    """

    if '/' not in package:
        raise RuntimeError('PACKAGE should be specified as "group/name"')

    group, name = package.split('/')

    # creates the rst title, which looks like this:
    # =======
    #  Title
    # =======
    rst_title = ('=' * (2+len(title))) + '\n ' + title + '\n' + \
        ('=' * (2+len(title)))

    # the jinja context defines the substitutions to be performed
    today = datetime.datetime.today()
    context = dict(
        package = package,
        group = group,
        name = name,
        author = author,
        email = email,
        title = title,
        rst_title = rst_title,
        license = license,
        year = today.strftime('%Y'),
        date = today.strftime('%c'),
        )

    # copy the whole template structure and de-templatize the needed files
    if output_dir is None:
      output_dir = os.path.join(os.path.realpath(os.curdir), name)
    logger.info('Creating structure for %s at directory %s', package,
        output_dir)

    if os.path.exists(output_dir):
      raise IOError('The package directory %s already exists - cannot '
          'overwrite!' % output_dir)

    logger.info('mkdir %s', output_dir)
    os.makedirs(output_dir)

    # base jinja2 engine
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('bob.devtools', 'templates'),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    # other standard files
    simple = [
        'requirements.txt',
        'buildout.cfg',
        'MANIFEST.in',
        'setup.py',
        '.gitignore',
        'doc/index.rst',
        'doc/conf.py',
        'doc/links.rst',
        '.gitlab-ci.yml',
        'README.rst',
        'version.txt',
        ]
    for k in simple:
      render_template(env, k, context, output_dir)

    # handles the license file
    if license == 'gplv3':
      render_template(env, 'COPYING', context, output_dir)
    else:
      render_template(env, 'LICENSE', context, output_dir)

    # creates the base python module structure
    template_dir = pkg_resources.resource_filename(__name__, os.path.join('..',
      'templates'))
    logger.info('Creating base %s python module', group)
    shutil.copytree(os.path.join(template_dir, 'pkg'),
        os.path.join(output_dir, group))

    # copies specific images to the right spot
    copy_file(os.path.join('doc', 'img', '%s-favicon.ico' % group), output_dir)
    copy_file(os.path.join('doc', 'img', '%s-128x128.png' % group), output_dir)
    copy_file(os.path.join('doc', 'img', '%s-logo.png' % group), output_dir)

    # finally, render the conda recipe template-template!
    # this one is special since it is already a jinja2 template
    conda_env = jinja2.Environment(
        loader=jinja2.PackageLoader('bob.devtools', 'templates'),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        block_start_string='(%', block_end_string='%)',
        variable_start_string='((', variable_end_string='))',
        comment_start_string='(#', comment_end_string='#)',
        )
    render_template(conda_env, os.path.join('conda', 'meta.yaml'), context,
        output_dir)
