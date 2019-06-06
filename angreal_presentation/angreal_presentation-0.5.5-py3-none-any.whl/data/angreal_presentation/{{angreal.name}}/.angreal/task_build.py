import angreal
import os
import subprocess
import webbrowser

from angreal.integrations.virtual_env import venv_required

here = os.path.realpath(os.path.dirname(__file__))
doc_roots = os.path.realpath(os.path.join(here, '..'))
doc_build = os.path.realpath(os.path.join(doc_roots, '_build', 'html', 'index.html'))
cwd = os.getcwd()


@angreal.command()
@angreal.option('--no_open', is_flag=True, help="Don't open in browser")
@venv_required('{{angreal.name}}')
def angreal_cmd(no_open):
    """
    compile the presentation
    """
    os.chdir(doc_roots)
    subprocess.run('sphinx-apidoc -fMTeE -o source ../{{ angreal.name }}', shell=True)
    subprocess.run('make clean', shell=True)
    subprocess.run('make html', shell=True)

    if not no_open:
            webbrowser.open_new_tab('file://{}'.format(doc_build))

    os.chdir(cwd)  # not strictly necessary

    return
