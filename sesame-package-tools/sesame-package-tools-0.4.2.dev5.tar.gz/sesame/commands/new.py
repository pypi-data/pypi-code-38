# -*- coding: utf-8 -*-

import argparse
import os
import pathlib
import re

import sesame

def new_cmd(args):
    """Creates a new package recipe"""
    parser = argparse.ArgumentParser(description=new_cmd.__doc__, prog='sesame new')
    parser.add_argument('name_version', help='Package name and version (name/version)')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--tool', action='store_true')
    group.add_argument('--header-only', action='store_true')
    args = parser.parse_args(*args)
    files = _new(args)
    _save_files(os.getcwd(), files)

def _save(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = 'wb'
    with open(path, mode) as f:
        f.write(_to_file_bytes(content))

def _to_file_bytes(content):
    if not isinstance(content, bytes):
        content = bytes(content, "utf-8")
    return content

def _save_files(path, files):
    for name, content in list(files.items()):
        _save(os.path.join(path, name), content)

def _new(args):
    pattern = re.compile(r'[\W_]+')
    package_name_version = args.name_version.partition('/')
    name = package_name_version[0]
    version = package_name_version[2]
    package_name = pattern.sub('', name).capitalize()

    gitattributes_file = pathlib.Path(sesame.get_template_path('gitattributes-template.txt')).read_text()
    gitignore_file = pathlib.Path(sesame.get_template_path('gitignore-template.txt')).read_text()
    license_file = pathlib.Path(sesame.get_template_path('license-template.txt')).read_text()
    test_package_cmakelists_txt_file = pathlib.Path(sesame.get_template_path('test-package-cmakelists-template.txt')).read_text()
    test_package_conanfile_file = pathlib.Path(sesame.get_template_path('test-package-conanfile-template.txt')).read_text()
    test_package_cpp_file = pathlib.Path(sesame.get_template_path('test-package-cpp-template.txt')).read_text()
    tool_test_package_conanfile_file = pathlib.Path(sesame.get_template_path('tool-test-package-conanfile-template.txt')).read_text()

    normal = not args.header_only and not args.tool
    if normal:
        normal_build_file = pathlib.Path(sesame.get_template_path('normal-build-template.txt')).read_text()
        normal_build_sesame_file = pathlib.Path(sesame.get_template_path('normal-build-sesame-template.txt')).read_text()
        normal_conanfile_file = pathlib.Path(sesame.get_template_path('normal-conanfile-template.txt')).read_text()
        files = {
            '.gitignore': gitignore_file.format(name=name, version=version, package_name=package_name),
            '.gitattributes': gitattributes_file.format(name=name, version=version, package_name=package_name),
            'build.py': normal_build_file.format(name=name, version=version, package_name=package_name),
            'build-sesame.py': normal_build_sesame_file.format(name=name, version=version, package_name=package_name),
            'conanfile.py': normal_conanfile_file.format(name=name, version=version, package_name=package_name),
            'LICENSE.md': license_file.format(name=name, version=version, package_name=package_name),
            'test_package/CMakeLists.txt': test_package_cmakelists_txt_file.format(name=name, version=version, package_name=package_name),
            'test_package/conanfile.py': test_package_conanfile_file.format(name=name, version=version, package_name=package_name),
            'test_package/test_package.cpp': test_package_cpp_file.format(name=name, version=version, package_name=package_name),
        }
    elif args.tool:
        tool_build_file = pathlib.Path(sesame.get_template_path('tool-build-template.txt')).read_text()
        tool_build_sesame_file = pathlib.Path(sesame.get_template_path('tool-build-sesame-template.txt')).read_text()
        tool_conanfile_file = pathlib.Path(sesame.get_template_path('tool-conanfile-template.txt')).read_text()
        files = {
            '.gitignore': gitignore_file.format(name=name, version=version, package_name=package_name),
            '.gitattributes': gitattributes_file.format(name=name, version=version, package_name=package_name),
            'build.py': tool_build_file.format(name=name, version=version, package_name=package_name),
            'build-sesame.py': tool_build_sesame_file.format(name=name, version=version, package_name=package_name),
            'conanfile.py': tool_conanfile_file.format(name=name, version=version, package_name=package_name),
            'LICENSE.md': license_file.format(name=name, version=version, package_name=package_name),
            'test_package/conanfile.py': tool_test_package_conanfile_file.format(name=name, version=version, package_name=package_name),
        }
    elif args.header_only:
        header_only_build_file = pathlib.Path(sesame.get_template_path('header-only-build-template.txt')).read_text()
        header_only_build_sesame_file = pathlib.Path(sesame.get_template_path('header-only-build-sesame-template.txt')).read_text()
        header_only_conanfile_file = pathlib.Path(sesame.get_template_path('header-only-conanfile-template.txt')).read_text()
        files = {
            '.gitignore': gitignore_file.format(name=name, version=version, package_name=package_name),
            '.gitattributes': gitattributes_file.format(name=name, version=version, package_name=package_name),
            'build.py': header_only_build_file.format(name=name, version=version, package_name=package_name),
            'build-sesame.py': header_only_build_sesame_file.format(name=name, version=version, package_name=package_name),
            'conanfile.py': header_only_conanfile_file.format(name=name, version=version, package_name=package_name),
            'LICENSE.md': license_file.format(name=name, version=version, package_name=package_name),
            'test_package/CMakeLists.txt': test_package_cmakelists_txt_file.format(name=name, version=version, package_name=package_name),
            'test_package/conanfile.py': test_package_conanfile_file.format(name=name, version=version, package_name=package_name),
            'test_package/test_package.cpp': test_package_cpp_file.format(name=name, version=version, package_name=package_name),
        }

    return files
