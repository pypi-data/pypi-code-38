from os import chdir as cd, makedirs, system, getcwd as pwd
from os.path import exists, join, dirname
import argparse
import re

def mkdirs(*dirs):
    for dir in dirs:
        if not exists(dir):
            makedirs(dir)

data_dir = join(dirname(__file__), "data")

def RMW(file, op, outputFile=None):
    with open(join(data_dir, file), "r") as fin:
        content = fin.read()
    content = op(content)
    with open(outputFile if outputFile else file, "w") as fout:
        fout.write(content)

def regularize(name):
    return name[0].upper() + name[1:]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help="The name of your project.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-shared", action='store_true', help="shared library")
    group.add_argument("-exe", action='store_true', help="executable")
    group.add_argument("-static", action='store_true', help="static library")
    args = parser.parse_args()
    if not args.exe and not args.shared and not args.static:
        args.exe = True
    project_name = args.project_name.strip()
    if not re.match(r"[a-zA-Z][a-zA-Z0-9_\-]*", project_name):
        print("Invalid project name! name pattern: [a-zA-Z][a-zA-Z0-9_-]*")
        return
    mkdirs(project_name)
    cd(project_name)
    project_path = pwd()
    mkdirs("cmake", "src", "test")
    
    replace_project_name = lambda content: content.replace("{project_name}", project_name)
    replace_library_shared = lambda content: content.replace("{project_name}", project_name).replace(
        "{is_shared}", 'True')
    replace_library_static = lambda content: content.replace("{project_name}", project_name).replace(
        "{is_shared}", 'False')
    copy = lambda content: content
    if args.exe:
        RMW("conanfile.py", replace_library_static)
        RMW("ExeCMakeLists.txt", replace_project_name, "CMakeLists.txt")
    elif args.static:
        RMW("conanfile.py", replace_library_static)
        RMW("LibraryCMakeLists.txt", replace_project_name, "CMakeLists.txt")
    elif args.shared:
        RMW("conanfile.py", replace_library_shared)
        RMW("LibraryCMakeLists.txt", replace_project_name, "CMakeLists.txt")
    else:
        raise Exception('Unknown project type! should be one of [exe, static, shared]!')
    RMW(".gitlab-ci.yml", copy)
    RMW("build.py", copy)
    RMW("CMakeSettings.json", copy)
    RMW(".clang-format", copy)
    RMW("gitignore", copy, ".gitignore")
    RMW("README.md", replace_project_name)
    
    cd("src")
    if args.exe:
        RMW("main.cpp", copy)
    else:
        RMW("mainlibrary.cpp", copy, "main.cpp")
        RMW("main.h", copy)
    
    cd("../test")
    if args.exe:
        RMW("test.cpp", copy)
    else:
        RMW("testLibrary.cpp", copy, "test.cpp")
    
    cd("../cmake")
    RMW("conan.cmake", copy)
    RMW("symlink.cmake", replace_project_name)
    RMW("symlink.py", copy)
    
    cd("..")
    system("git init")
    system("git add .gitignore")
    system("git add -A")
    result = 'Created new '
    if args.exe:
        result += "exe"
    elif args.shared:
        result += "shared library"
    else:
        result += "static library"
    print(f'{result} project: {project_name} (located in {project_path})')
