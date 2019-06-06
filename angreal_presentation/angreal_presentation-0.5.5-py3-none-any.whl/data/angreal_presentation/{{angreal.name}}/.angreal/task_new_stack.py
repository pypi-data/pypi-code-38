import angreal
import os
import re


from angreal.integrations.git import Git


stack_dir = os.path.join(os.path.dirname(__file__), '..', 'source')


@angreal.command()
@angreal.argument('stack_name')
def angreal_cmd(stack_name):
    """
    Create a new slide stack for the presentation
    """

    if not os.path.isdir(stack_dir):
        exit("{} doesn't appear to exist!".format(stack_dir))

    # Get a list of current leading digits and sort them in reverse order
    # i.e [03, 02, 01, 00 ]
    stack_regular_expression = re.compile('^(\d+)_.*\.rst$')
    current_stacks = [stack_regular_expression.match(f).group(1) for f in os.listdir(stack_dir) if stack_regular_expression.match(f)]
    current_stacks.sort(reverse=True)

    if len(current_stacks) == 0:
        this_stack_num = '00'
    else:
        this_stack_num = increment_episode(current_stacks[0])

    this_stack_name = stack_name.replace('-', '_')
    this_stack_name = this_stack_name.replace(' ', '_')

    this_stack_name = os.path.join(stack_dir, '_'.join([this_stack_num, this_stack_name]) + '.rst')

    with open(this_stack_name, 'w') as f:
        print('''.. revealjs:: {}'''.format(stack_name), file=f)

    git = Git()
    git.add(this_stack_name)
    git.commit('-am', 'Starting work on {}'.format(os.path.basename(this_stack_name)))


def increment_episode(x):
    """
    increment a zero padded number by one
    """
    return str(int(x) + 1).zfill(len(x))

