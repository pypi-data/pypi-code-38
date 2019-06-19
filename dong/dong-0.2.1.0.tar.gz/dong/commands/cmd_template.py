import os
import click

from dong import utils
from dong import templates


template_help = """module name for to be generated {} module from the template."""

@click.group(invoke_without_command=True)
@click.option('--data-module', default=None, help=template_help.format('data'))
@click.option('--model-init-module', default=None, help=template_help.format('model init'))
@click.option('--model-serializer-module', default=None, help=template_help.format('model serializer'))
@click.option('--model-train-module', default=None, help=template_help.format('model train'))
@click.option('--model-module', default=None, help=template_help.format('model'))
@click.option('--config-module', default=None, help=template_help.format('config'))
@click.option('--service-module', default=None, help=template_help.format('service'))
@click.option('--tune-module', default=None, help=template_help.format('tune'))
# handle model compose later
@click.pass_context
def command(ctx,
            data_module,
            model_init_module,
            model_serializer_module,
            model_train_module,
            model_module,
            config_module,
            service_module,
            tune_module):
    """Generate module files from template, if not provided, the corresponding module won't be generated."""

    modules = {
        'data': data_module,
        'model/init': model_init_module,
        'model/serializer': model_serializer_module,
        'model/train': model_train_module,
        'model': model_module,
        'config': config_module,
        'service': service_module,
        'tune': tune_module,
    }

    if all( modules[key] is None for key in modules.keys() ):
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit(1)
        return

    # NOTICE: should do exception handling when there is no setup.py
    project_name = utils.get_project_name('./setup.py')

    
    for name in modules.keys():
        if modules[name] is None:
            continue

        module_dir = './' + project_name + '/' + name

        if not os.path.isdir(module_dir):
            utils.eprint('Directory ' + name + "/ doesn't exist. Are you inside a dong project?")
            continue

        # by modules[name] we get the name of the module to be generated
        utils.create_file(os.path.join(module_dir, modules[name] + '.py'),
                          templates.make_template(name,
                                                  { 'class_name': modules[name].title() + name.title().replace('/', '')}))
