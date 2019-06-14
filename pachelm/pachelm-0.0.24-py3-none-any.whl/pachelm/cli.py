import click
import shutil
from os.path import dirname
from pachelm.core import PachydermAdminContext
from pachelm.utils import getDateTimestampAndString, mkdir_p, overwritePrompt, to_class_name, deletePrompt

VERSION='0.0.24'

entities = ['repo', 'pipeline']

templateByResource = {
  "repo": "repo_migration.py.tmpl",
  "pipeline": "pipeline_migration.py.tmpl",
  "pipeline_config": "pachyderm.json.tmpl",
  "seed": "seeds.py.tmpl"
}

fns = {
  'to_class_name': to_class_name
}

@click.group(invoke_without_command=True)
@click.option('--migrationsDir', '-m', default='./migrations', help="specify directory to keep migrations.")
@click.option('--pachydermConfigsDir', '-p', default='./configs', help="specify directory to keep pachderm json configs.")
@click.option('--dataDir', '-d', default='./data', help="specify directory to keep data for seed.")
@click.pass_context
def entry(ctx, **kwargs):
  """ Pachydelm, Main purpose is the opinionated framework to ease working with pachyderm pipeline deployment"""
  print(VERSION)
  print(kwargs)
  ctx.obj = PachydermAdminContext(**{ "version": VERSION, **kwargs })
  if ctx.invoked_subcommand is None:
    click.echo('I was invoked without subcommand')
  else:
    click.echo('Invoke %s' % ctx.invoked_subcommand)

## Credit about dynamic module in python: https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
@entry.command()
@click.pass_obj
def migrate(ctx):
  """ Migrate module"""
  ctx.tear_up()
  click.echo('Migrating...')

@entry.command()
@click.pass_obj
def rollback(ctx):
  """ Rollback module"""
  ctx.tear_down()
  click.echo('Rolling back...')

def renderResource(ctx, args, filePath, resource_type):
  template = ctx.env.get_template(templateByResource[resource_type])
  rendered = template.render(ctx=ctx, args=args, fns=fns)
  mkdir_p(dirname(filePath))
  if overwritePrompt([filePath]):
    fileObj = open(filePath, "w+")
    fileObj.write(rendered)
    fileObj.close()

@entry.command()
@click.argument('resource')
@click.option('--name', '-n', help='Resource name...', required=True)
@click.option('--migration', '-m', help='Migration file name...')
@click.pass_obj
def create(ctx, **kwargs):
  """ Create Migrations & Seeds & corresponding pachyderm json config"""
  (timestamp, datetimeStr) = getDateTimestampAndString()
  combined_migration_name = '%s_%s_%s' % (kwargs['name'], kwargs['resource'], kwargs['migration']) if kwargs['migration'] else '%s_%s_%s' % (kwargs['name'], kwargs['resource'], kwargs['name'])
  baseFileName = '%s_%s' %(datetimeStr, combined_migration_name)
  (migrationFilePath, pachydermConfigFilePath) = ctx.get_pipeline_path(baseFileName)
  kwargs = {
    **kwargs,
    "migration": kwargs['migration'] or kwargs['name'],
    "migrationFilePath": migrationFilePath,
    "pachydermConfigFilePath": pachydermConfigFilePath
  }
  try:
    renderResource(ctx, kwargs, migrationFilePath, kwargs['resource'])
    if kwargs['resource'] == 'pipeline':
      renderResource(ctx, kwargs, pachydermConfigFilePath, kwargs['resource'] + '_config')
  except KeyError:
    raise Exception('Unknown resource...')
  # except:
  #   raise Exception('Something went wrong...')

@entry.command()
@click.option('--force', '-f', is_flag=True, help="Force rollback before cleaning....")
@click.pass_obj
def clean(ctx, force):
  """ Clean all migrations & config """
  if force:
    ctx.tear_down()
  try:
    if deletePrompt([ctx.migrationsDir, ctx.pachydermConfigsDir]):
      shutil.rmtree(ctx.migrationsDir)
      shutil.rmtree(ctx.pachydermConfigsDir)
      click.echo('deleteing...\n%s\n%s' % (ctx.migrationsDir, ctx.pachydermConfigsDir))
  except FileNotFoundError:
    click.echo('Directory Not exist...')

if __name__ == '__main__':
    entry()