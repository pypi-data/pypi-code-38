import os
import fileutils
from sys import platform
import json


def create_project():
    file = fileutils.root_dir + '/tools/sublime.sublime-project'
    fileutils.createDirForFile(file)

    project_json = None
    if os.path.isfile(file):
        with open(file) as data_file:
            project_json = json.load(data_file)

    if project_json is None:
        project_json = {}
    if 'folders' not in project_json:
        project_json['folders'] = []

    exist = False
    for data in project_json['folders']:
        if 'path' in data:
            exist = exist or data['path'] == fileutils.root_dir

    if not exist:
        project_json['folders'].append({})
        project_json['folders'][-1]['path'] = fileutils.root_dir

    project_json['translate_tabs_to_spaces'] = True

    with open(file, 'w') as outfile:
        json.dump(project_json, outfile, indent=2)


def create_build_system():
    path = ''
    if platform == "win32":
        path = os.getenv('APPDATA') + '\\Sublime Text 3\\Packages\User\\'
    elif platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        appdata = NSSearchPathForDirectoriesInDomains(14, 1, True)[0] + '/Sublime Text 3'
        path = appdata + '/Packages/User/'
    else:
        exit(-1)
    path += 'Stereo7.sublime-build'
    fileutils.createDirForFile(path)
    open(path, 'w').write('{"shell_cmd": "stereo7 validate -r $project_path/.."}')


def run():
    create_project()
    create_build_system()
