import angreal
import os
import subprocess
import webbrowser
from angreal import venv_required

here = os.path.realpath(os.path.dirname(__file__))
cwd = os.getcwd()


@angreal.command()
@angreal.option('--open', is_flag=True, help='generate an html report and open in a browser')
@venv_required('{{ angreal._cleaned_name }}')
def angreal_cmd(open):
    """
    run static typing
    """
    os.chdir(os.path.join(here, '..'))

    subprocess.run('mypy {{ angreal._cleaned_name }} --ignore-missing-imports --show-error-context --html-report typing_report ',
                   shell=True)

    if open:
        output_file = os.path.realpath(os.path.join(here, '..', 'typing_report', 'index.html'))
        webbrowser.open_new('file://{}'.format(output_file))
