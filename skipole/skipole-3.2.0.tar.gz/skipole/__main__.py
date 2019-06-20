#
# This script is meant to be run from the command line using
#
# python3 -m skipole mynewproj /path/to/projectfiles
#
#

import sys, os, re, shutil

from . import version

DESCRIPTION = """Usage is

python3 -m skipole mynewproj /path/to/projectfiles

Which creates a directory /path/to/projectfiles
containing three sub directories:

mynewproj - a subdirectory containing a new project
skis - a project serving needed javascript files, necessary for all projects
skiadmin - a project used to help develop 'mynewproj'

You should replace 'mynewproj' with your preferred name for a new project.
This is an optional argument. If not given then only the skis and skiadmin
projects will be created.

The path "/path/to/projectfiles" must be given, and is the path to a directory
where you will develop your project. Multiple projects can be created in one
'projectfiles' directory, or you could have multiple such directories holding
different projects.

If the directory already exists, any existing skiadmin and skis projects will
be overwritten, this facility is used to upgrade skis and skiadmin if a new
version of skipole is installed.

If mynewproj already exists in the directory, it will not be changed.
"""


# a search for anything none-alphanumeric and not an underscore
_AN = re.compile('[^\w]')


args = sys.argv

if len(args) == 3:
    project_name = args[1]
    projectfiles = os.path.abspath(os.path.expanduser(args[2]))
    if _AN.search(project_name):
        print( "Error: Invalid project name, alphanumeric only")
        sys.exit(1)
    if '_' in project_name:
        print( "Error: Invalid project name, alphanumeric only (no underscore).")
        sys.exit(1)
    if (project_name == 'skis') or (project_name=='skiadmin'):
        print("Error: This project name is reserved")
        sys.exit(2)
elif len(args) == 2:
    if args[1] == "--version":
        print(version)
        sys.exit(0)
    project_name = None
    projectfiles = os.path.abspath(os.path.expanduser(args[1]))
else:
    print( "Invalid input. " + DESCRIPTION)
    sys.exit(3)


# get the location of the directories to be copied
template_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template_projects')

if not os.path.isdir(template_directory):
    print("Error: Cannot find the template data for the skis and skiadmin projects")
    sys.exit(4)
template_skis_directory = os.path.join(template_directory, 'skis')
if not os.path.isdir(template_skis_directory):
    print("Error: Cannot find the template data for the skis project")
    sys.exit(5)
template_skiadmin_directory = os.path.join(template_directory, 'skiadmin')
if not os.path.isdir(template_skiadmin_directory):
    print("Error: Cannot find the template data for the skiadmin project")
    sys.exit(6)
template_newproj_directory = os.path.join(template_directory, 'newproj')
if not os.path.isdir(template_newproj_directory):
    print("Error: Cannot find the template data for the newproj project")
    sys.exit(7)



# If the given projectfiles directory does not exist
if not os.path.isdir(projectfiles):

    # create the directory by copying the template_directory
    shutil.copytree(template_directory, projectfiles)

    # new directory which has been created
    newproj_directory = os.path.join(projectfiles, 'newproj')

    if project_name is None:
        # remove the new project
        shutil.rmtree(newproj_directory)
        print("Project directory %s created" % (projectfiles,))
        sys.exit(0)

    # A project name is given, change the name of the newproj_directory to project_name
    project_directory = os.path.join(projectfiles, project_name)
    os.rename(newproj_directory, project_directory)


    new_code_path = os.path.join(project_directory, "code", project_name + ".py")
    print("Creating %s" % (new_code_path,))

    # change newproj.py to project_name.py, including the contents
    ## READ newproj.py
    newproj_file = os.path.join(project_directory, "code", "newproj.py")
    with open(newproj_file, "r") as tnf:
        templatecontents = tnf.read()
    os.remove(newproj_file)
    ## REPLACE newproj with the new project name
    newcontents = templatecontents.replace("newproj", project_name)
    ## WRITE the new file
    with open(new_code_path, "w") as pf:
        pf.write(newcontents)

    # change data/project.json contents
    ## READ project.json
    data_file = os.path.join(project_directory, "data", "project.json")
    with open(data_file, "r") as tdf:
        templatedatacontents = tdf.read()
    os.remove(data_file)
    ## REPLACE newproj with the new project name
    newdatacontents = templatedatacontents.replace("newproj", project_name)
    ## WRITE the new file
    with open(data_file, "w") as tdf2:
        tdf2.write(newdatacontents)


    print("Project directory %s created, with new project %s" % (projectfiles,project_name))
    print("""Use the command:
python3 %s
To serve the project at url localhost:8000
and localhost:8000/skiadmin for the admin pages""" % (new_code_path,))
    sys.exit(0)

# The given projectfiles does exist, so use it for the new project

print("Replacing project skis")
# if skis exists, delete it, then copy the template
skis_directory = os.path.join(projectfiles, 'skis')
if os.path.isdir(skis_directory):
    shutil.rmtree(skis_directory)
shutil.copytree(template_skis_directory, skis_directory)

print("Replacing project skiadmin")
# if skiadmin exists, delete it, then copy the template
skiadmin_directory = os.path.join(projectfiles, 'skiadmin')
if os.path.isdir(skiadmin_directory):
    shutil.rmtree(skiadmin_directory)
shutil.copytree(template_skiadmin_directory, skiadmin_directory)

if project_name is None:
    print("skis and skiadmin have been replaced.")
    sys.exit(0)

project_directory = os.path.join(projectfiles, project_name)
if os.path.isdir(project_directory):
    print("skis and skiadmin have been replaced, however project % already exists, and has not been altered." % (project_name,))
    sys.exit(0)

# create a new project
shutil.copytree(template_newproj_directory, project_directory)

new_code_path = os.path.join(project_directory, "code", project_name + ".py")
print("Creating %s" % (new_code_path,))

# change newproj.py to project_name.py, including the contents
## READ newproj.py
newproj_file = os.path.join(project_directory, "code", "newproj.py")
with open(newproj_file, "r") as tnf:
    templatecontents = tnf.read()
os.remove(newproj_file)
## REPLACE newproj with the new project name
newcontents = templatecontents.replace("newproj", project_name)
## WRITE the new file
with open(new_code_path, "w") as pf:
    pf.write(newcontents)

# change data/project.json contents
## READ project.json
data_file = os.path.join(project_directory, "data", "project.json")
with open(data_file, "r") as tdf:
    templatedatacontents = tdf.read()
os.remove(data_file)
## REPLACE newproj with the new project name
newdatacontents = templatedatacontents.replace("newproj", project_name)
## WRITE the new file
with open(data_file, "w") as tdf2:
    tdf2.write(newdatacontents)

print("skis and skiadmin have been replaced, and new project %s created." % (project_name,))
print("""Use the command:
python3 %s
To serve the project at url localhost:8000
and localhost:8000/skiadmin for the admin pages""" % (new_code_path,))
sys.exit(0)



