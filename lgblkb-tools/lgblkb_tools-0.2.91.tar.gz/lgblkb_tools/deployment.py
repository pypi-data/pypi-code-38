import os
import time
from box import Box

import lgblkb_tools.folder_utils
from lgblkb_tools.remote_opers import SshFolder
from . import global_support as gsup
from .global_support import run_command
from . import log_support as logsup

flower_port=5553
app_name='celery_worker'

def deploy(sshmanager,lgblkb_tools_version,commit_message,detached=True,downup=True):
	run_command(f'git commit -a -m "{commit_message}"')
	run_command('git push')
	time.sleep(5)
	with sshmanager.cd_to_working_dir():
		# sshmanager.put('configs.yaml','configs.yaml')
		sshmanager.run(f"""
		git stash
		git fetch
		git pull
		sed -i "s/ENV LGBLKB_TOOLS_VERSION=''/ENV LGBLKB_TOOLS_VERSION='{lgblkb_tools_version}'/g" Dockerfile
		docker build -t hub.egistic.kz/imgback:latest .
		
		""")  #--build-arg UID=$(id -u) --build-arg GID=$(id -g)
		if downup:
			sshmanager.run(f"""
		docker-compose down
		docker-compose up {'-d' if detached else ''}""")

def get_updated_lgblkb_tools(dry=False,with_commit=False):
	import git
	version_getter=lambda:Box.from_yaml(filename='/home/lgblkb/PycharmProjects/lgblkb_tools/package_info.yaml').version
	if dry:
		lgblkb_tools_version=version_getter()
	else:
		package_name="lgblkb-tools"
		run_command(f"""
	. ~/.virtualenvs/lgblkb_tools/bin/activate
	cd /home/lgblkb/PycharmProjects/lgblkb_tools
	python ./setup.py sdist bdist_wheel
	twine upload dist/*
			""")
		lgblkb_tools_version=version_getter()
		run_command(f"""
	. ~/.virtualenvs/korsum/bin/activate
	pip install --upgrade {package_name}=={lgblkb_tools_version}
	pip install --upgrade {package_name}=={lgblkb_tools_version}
		""")
		if with_commit:
			repo=git.Repo(lgblkb_tools.folder_utils.Folder().path)
			logsup.logger.info('repo: %s',repo)
			assert not repo.bare
			repo.index.commit(f"""Updated lgblkb_tools to version='{lgblkb_tools_version}'""")
	
	logsup.logger.info('lgblkb_tools_version: %s',lgblkb_tools_version)
	return lgblkb_tools_version

def get_current_branch_name(repo):
	branches=list(map(lambda x:x.strip(),repo.git.branch().split('\n')))
	logsup.logger.debug('branches: %s',branches)
	
	for branch in branches:
		if '* ' in branch:
			the_branch=branch[2:]
			logsup.logger.info('Current branch: %s',the_branch)
			return the_branch

def get_corresponding_path(base_dir,path):
	path_parts=gsup.get_splitted(path)[1:]
	for i,path_part in enumerate(path_parts):
		if os.path.exists(os.path.join(base_dir,path_part)):
			return os.path.join(base_dir,*path_parts[i:])

class RemoteProjectFolder(SshFolder):
	
	def __init__(self,remote_path,local_project_folder,**conn_kwargs):
		super(RemoteProjectFolder,self).__init__(remote_path=remote_path,**conn_kwargs)
		self.local_project_folder=local_project_folder
		pass
	
	def _download_remote_item(self,remote_itempath,local_itempath=''):
		remote_log_path=get_corresponding_path(self.path,remote_itempath)
		local_itempath=local_itempath or get_corresponding_path(self.local_project_folder.path,remote_itempath)
		os.makedirs(gsup.get_parent_dir(local_itempath),exist_ok=True)
		self.get(remote_log_path,local_itempath)
		return local_itempath
	
	def run_in_docker(self,cmd):
		output=self.run_with_cd(rf'docker run -i --rm --name lgblkb_test_2 '
		                        rf'--network=redis '
		                        rf'--network=postgis '
		                        rf'-v "$(pwd)":/app '
		                        rf'-v /home/egistic_db/egistic/image_backend:/image_backend '
		                        rf'-v /nfs/storage/sat_images:/app/nfs_storage_images '
		                        rf'hub.egistic.kz/imgback:latest {cmd}',
		                        warn=True)
		return output
	
	def upload_and_run_in_docker(self,module,args_cmd: str):
		module_path=module.__name__.replace('.','/')+'.py'
		self.put(module.__file__,module_path)
		self.put('configs.yaml','configs.yaml')
		return self.run_in_docker(rf"""python3 -m {module.__name__} {args_cmd}""")
	
	def _upload_and_run(self,python_module,cmd):
		helper_script=python_module.__name__.replace('.','/')+'.py'
		self.put(python_module.__file__,helper_script)
		output=self.run_with_cd(f"""
		docker run -i --rm --name lgblkb_test -v "$(pwd)":/app hub.egistic.kz/imgback:latest {cmd}
		""")
		self.run_with_cd(f'rm {helper_script}',warn=True)
		return output
	
	def commit_and_deploy(self,image_tag,update_lgblkb_tools=False,downup=True,detached=True,):
		MESSAGE=input('Commit message: ')
		lgblkb_tools_version=get_updated_lgblkb_tools(dry=not update_lgblkb_tools)
		# deploy(self.sshman,lgblkb_tools_version,MESSAGE,detached=detached,downup=downup)
		run_command(f'git commit -a -m "{MESSAGE}"')
		run_command('git push')
		# time.sleep(5)
		self.put('configs.yaml','configs.yaml')
		self.put('.env','.env')
		with self.sshman.cd_to_working_dir():
			self.sshman.run(f"""
				git stash
				git fetch
				git pull
				sed -i "s/ENV LGBLKB_TOOLS_VERSION=''/ENV LGBLKB_TOOLS_VERSION='{lgblkb_tools_version}'/g" Dockerfile
				docker build -t {image_tag} .
				""")  #--build-arg UID=$(id -u) --build-arg GID=$(id -g)
			
			if downup:
				self.sshman.run(f"""
				docker-compose down
				docker-compose up {'-d' if detached else ''}""")
	
	def find_log_with_content(self,content):
		self.run_with_cd(r"""

		""")

def open_in_pycharm(filepath):
	run_command(f'/snap/bin/pycharm-professional "{filepath}"')

def main():
	
	pass

if __name__=='__main__':
	main()
