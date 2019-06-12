#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""qresp_config.

Usage:
  qresp_config collection <folder_name> [<path>]
  qresp_config paper <paper_name> [<path>]
  qresp_config info <paper_name> [<path>]
  qresp_config --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --collection	Generates paper_collection which will host paper content of user(s) and creates a config file(qresp.ini).
  --paper_name 	Name of the paper.
  --path 		Path where the action should be triggered. Defaults to current location, if not specified.
  --paper		Initializes a paper with a git repo.
  --info		Provides information on how to clone the paper_name.git repo. 
  --folder_name Name of the paper collection.
  
"""
import sys
import os
from .scripts.docopt import docopt
import subprocess
import stat
import configparser
import io
import errno

flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

#current working directory
cwd = os.getcwd() 


bash_cmd= """#!/bin/bash
PROJECTDIR="$PWD"
PROJECTNAME="$1"

if [[ "$2" != "" &&  "$2" != "None" ]]; then

	PROJECTDIR="$2"

fi

if [ -d "${PROJECTDIR}" ]; then

	if [[ -d ${PROJECTDIR}/${PROJECTNAME} || -d ${PROJECTDIR}/${PROJECTNAME}.git ]]; then

		echo "Error: ${PROJECTDIR}/${PROJECTNAME} already exists, doing nothing!"

	else

		mkdir "${PROJECTDIR}"/"${PROJECTNAME}".git # the git repo
		mkdir "${PROJECTDIR}"/"${PROJECTNAME}"     # the latest snapshot of the repo

		cd "${PROJECTDIR}"
		git init --bare "${PROJECTNAME}".git

		cd ${PROJECTNAME}.git/hooks

		cat > post-receive << EOF
#!/bin/bash
TARGET="${PROJECTDIR}/${PROJECTNAME}"
GIT_DIR="${PROJECTDIR}/${PROJECTNAME}.git"
BRANCH="master"

while read oldrev newrev ref
do
# only checking out the master (or whatever branch you would like to deploy)
if [[ \$ref = refs/heads/\$BRANCH ]]; then
echo "Ref \$ref received. Deploying \${BRANCH} branch to production..."
git --work-tree=\$TARGET --git-dir=\$GIT_DIR checkout -f
else
echo "Ref \$ref received. Doing nothing: only the \${BRANCH} branch may be deployed on this server."
fi
done
EOF
		chmod +x post-receive

		echo "In order to push data: git clone ssh://<username>@<servername>:${PROJECTDIR}/${PROJECTNAME}.git"

		cd "${PROJECTDIR}"/"${PROJECTNAME}"
		cat > "${PROJECTNAME}".log << EOF
"In order to push data: git clone ssh://<username>@<servername>:${PROJECTDIR}/${PROJECTNAME}.git"
EOF
		chmod 0775 "${PROJECTNAME}".log
		fi

else

	echo "Error: Project Directory does not exist or is not valid"

fi





"""



# Make the bash script files executable.
def make_executable(filename):
	st = os.stat(filename)
	os.chmod(filename, st.st_mode | stat.S_IEXEC)
	
# Check if qresp.conf file exists.
def check_conf(path):
	st = os.stat(filename)
	os.chmod(filename, st.st_mode | stat.S_IEXEC)

	
def create_folder(folder):
	if not os.path.exists(folder):
		os.makedirs(folder)
		os.chmod(folder, stat.S_IRGRP | stat.S_IWGRP | stat.S_IWUSR | stat.S_IRUSR | stat.S_IROTH | stat.S_IXUSR | stat.S_IXGRP)
	return folder
 
def create_config(isHttpService,isGlobusService,isGitService,httpServicePath,globusServicePath,directory):
	config = configparser.ConfigParser()
	config['SERVICE'] = {}
	config['SERVICE.PATH'] = {}
	config['SERVICE']['isHttpService'] = isHttpService
	config['SERVICE']['isGlobusService'] = isGlobusService
	config['SERVICE']['isGitService'] = isGitService
	if httpServicePath:
		config['SERVICE.PATH']['http_Service_Path'] = httpServicePath
	if globusServicePath:
		config['SERVICE.PATH']['globus_Service_Path'] = globusServicePath
	with open(directory+'/qresp.ini', 'w+') as configfile:
		config.write(configfile)
		
def check_services(prompt,type):
	while True:
		service = input(prompt).strip().upper()
		if service == "Y":
			break
		elif service == "N":
			print("Please refer to http://data-curator-software.readthedocs.io/en/latest/Data_Organization.html#data-location-and-access to run a, ", type," service.")
			break
		else:
			print("Invalid input")
			continue
	return service

def check_path(prompt):
	while True:
		path = input(prompt).strip().upper()
		if path:
			break
		else:
			print("Path cannot be empty, recheck your input")
			continue
	return path

def checkIfLogExists(directory,paper_name):
	if not os.path.exists(directory+"/"+paper_name):
		sys.exit(directory + "not found")
	else:
		try:
			fobj = open(directory+"/"+paper_name+"/"+paper_name+".log")
			print(fobj.readline())
		except:
			sys.exit(directory+"/"+paper_name+"/"+paper_name+".log" + " not found")
		
	
	
def checkIfGitExists(directory):
	if not os.path.exists(directory):
		sys.exit(directory + "not found")
	else:
		try:
			config = configparser.ConfigParser()
			config.read(directory+'/qresp.ini')
			if "N" in config['SERVICE']['isgitservice']:
				sys.exit("Cannot run qresp_config paper or info without git service")
		except Exception as e:
			print(e)
			sys.exit("Cannot run qresp_config paper or info without git service. qresp.ini file not found in "+directory)

def createFile(directory):
	try:
		file_handle = os.open(directory+'/qresp_version_control.bash', flags)
	except OSError as e:
		if e.errno == errno.EEXIST:
			pass
		else:  
			raise
	else:  
		with os.fdopen(file_handle, 'w') as file_obj:
			file_obj.write(bash_cmd)
		
def main():
	args = docopt(__doc__, version='qresp 1.0')
	httpServicePath = ""
	globusServicePath = ""
	if args.get('paper'):
		paper_directory = cwd
		if args.get('<path>'):
			paper_directory = str(args.get('<path>'))
		checkIfGitExists(paper_directory)
		createFile(paper_directory)
		make_executable(paper_directory+"/"+"qresp_version_control.bash")
		subprocess.check_call([paper_directory+"/"+'qresp_version_control.bash', str(args.get('<paper_name>')), str(args.get('<path>'))])
	elif args.get('info'):
		paper_directory = cwd
		if args.get('<path>'):
			paper_directory = str(args.get('<path>'))
		checkIfGitExists(paper_directory)
		checkIfLogExists(paper_directory,str(args.get('<paper_name>')))
	elif args.get('collection'):
		folder_name = str(args.get('<folder_name>'))
		if args.get('<path>'):
			folder_name = str(args.get('<path>')) + "/" + folder_name
		else:
			folder_name = cwd + "/" + folder_name
		directory = create_folder(folder_name)
		print("Created folder ",folder_name)

		isHttpService = check_services("Is the folder " + folder_name +" publicly accessible by a http service? (Y/N) ","http")
		if isHttpService == "Y":
			httpServicePath = check_path("Enter http path/url pointing to the " + folder_name)
	
		isGlobusService = check_services("Is there a Globus service running on the server? (Y/N) ","globus")
		if isGlobusService == "Y":
			isGlobusServiceEndpoint = check_services("Is there a Globus endpoint pointing to the folder " + folder_name+"? (Y/N)","globus endpoint")
			if isGlobusServiceEndpoint == "Y":
				globusServicePath = check_path("Enter Globus endpoint pointing to the " + folder_name)
		
		isGitService =  check_services("Is there a git service running on the server? (Y/N) ","git")
		create_config(isHttpService,isGlobusService,isGitService,httpServicePath,globusServicePath,directory)
		print("Created file qresp.ini")
		
		