import os
import shutil
import string
import sys

CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
TEMPLATE_PATH = os.path.join(CURRENT_PATH, 'data/templates')
LOWER_NUMBER_AND_ = string.ascii_lowercase + string.digits + '_'


def is_package_name_valid(name: str) -> bool:
    """
    Valid rules:
    1. Length of name is between 0 and 80
    2. Characters contain only ascii_lowercase, number and _
    3. First character is neither number nor _
    """
    if not 0 < len(name) <= 80:
        return False
    first_character = name[0]
    if first_character not in string.ascii_lowercase:
        return False
    return all(c in LOWER_NUMBER_AND_ for c in name)


def parse_names(proj_name: str) -> (str, str, str):
    """
    :return: dest_dir, namespace, package_name
    """
    if not proj_name.startswith('/'):
        proj_name = './' + proj_name
    dirname = os.path.dirname(proj_name)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    if not os.path.isdir(dirname):
        print(f'Directory is not valid: {dirname}')
        exit(1)
    basename = os.path.basename(proj_name)
    namespace = basename
    package_name = namespace.lower().replace('-', '_')
    if not is_package_name_valid(package_name):
        print(f'Converted package name is not valid: {package_name}')
        exit(1)
    return dirname, namespace, package_name


def template_format(directory: str, namespace: str, package_name: str):
    print(f'Check: {directory}')
    for name in os.listdir(directory):
        if not (name.endswith('.in') or name.endswith('.py') or name.endswith('.md')):
            continue
        path_name = os.path.join(directory, name)
        if os.path.isdir(path_name):
            template_format(path_name, namespace, package_name)
        elif os.path.isfile(path_name):
            with open(path_name, 'r') as f:
                content = f.read()
            content = content.replace('{package_name}', package_name)
            content = content.replace('{namespace}', namespace)
            with open(path_name, 'w') as f:
                f.write(content)


def copy_ignored(_, names):
    return [name for name in names if '.idea' in name or '__pycache__' in name]


def gen(dest_dir: str, namespace: str, package_name: str):
    # copy directory structure from template dir to destination
    dest_full_path = os.path.join(dest_dir, namespace)
    if os.path.exists(dest_full_path) and os.path.isdir(dest_full_path):
        print(f'Path "{dest_full_path}" exists, delete it?')
        decision = input(f'Y/N: ').lower()
        if decision == 'y':
            shutil.rmtree(os.path.join(dest_dir, namespace))
        else:
            print('Exit')
            exit(0)
    shutil.copytree(TEMPLATE_PATH, os.path.join(dest_dir, namespace), ignore=copy_ignored)
    os.rename(os.path.join(dest_dir, namespace, '{package_name}'), os.path.join(dest_dir, namespace, package_name))
    template_format(os.path.join(dest_dir, namespace), namespace, package_name)


def main():
    if len(sys.argv) > 1:
        proj_name = sys.argv[1]
    else:
        proj_name = input("Project Name?: ")
    dest_dir, namespace, package_name = parse_names(proj_name)
    print('-----')
    print('{:<18}{}{}'.format('Destination dir:', dest_dir, os.path.sep))
    print('{:<18}{}'.format('Namespace:', namespace))
    print('{:<18}{}'.format('Package name:', package_name))
    print('-----')
    try:
        gen(dest_dir, namespace, package_name)
    except Exception as e:
        print(f'Initialize project fail: {e}')
        import traceback
        traceback.print_exc()
    else:
        print('Initialize project success!')
