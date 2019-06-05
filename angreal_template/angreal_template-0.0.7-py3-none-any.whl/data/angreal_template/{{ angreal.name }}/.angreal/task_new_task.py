import angreal

import os


here = os.path.abspath(os.path.dirname(__file__))


task_template = '''
import angreal
import os

here = os.path.dirname(__file__)


@angreal.command()
@angreal.argument('arg_name')
@angreal.option('--option_name',is_flag=True, help='help message')
def angreal_cmd(arg_name,option_name):
    """[summary]

    [description]

    """
    return

'''[1:-1]


@angreal.command()
@angreal.argument('name')
def angreal_cmd(name):
    """
    Create a new task.
    """

    task_name = 'task_{}.py'.format(name)

    task_path = os.path.join(here,
                             '..',
                             {%raw%}'{{ angreal.name }}'{%endraw%},
                             '.angreal',
                             task_name)

    with open(task_path, 'w') as f:
        f.write(task_template)
        pass

    return
