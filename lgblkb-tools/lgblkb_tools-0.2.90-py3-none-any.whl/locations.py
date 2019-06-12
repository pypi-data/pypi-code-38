import collections
import fnmatch
import os
import shutil
import zipfile

get_name=lambda some_path:os.path.splitext(os.path.basename(some_path))[0]

def get_parent_dir(some_path,depth=1):
	for i in range(depth):
		some_path=os.path.dirname(os.path.abspath(some_path))
	return some_path

def create_path(*paths,stop_depth=0):
	path=os.path.join(*paths)
	os.makedirs(get_parent_dir(path,stop_depth),exist_ok=True)
	return path

def get_existing_path(paths,silent=False):
	for p in paths:
		if os.path.exists(p): return p
	if not silent:
		raise NotImplementedError('Could not find any existing path.')

def clear_folder(folder,remove_subdirs=True):
	for the_file in os.listdir(folder):
		file_path=os.path.join(folder,the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif remove_subdirs and os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			print(e)

def get_full_paths_from(parent_dir: str):
	for file in os.listdir(parent_dir):
		yield os.path.join(parent_dir,file)

def get_splitted(path):
	folders=[]
	while 1:
		path,folder=os.path.split(path)
		
		if folder!="":
			folders.append(folder)
		else:
			if path!="":
				folders.append(path)
			break
	folders.reverse()
	return folders

class InfoDict(collections.OrderedDict):
	
	def get_dir_path(self,*paths):
		return os.path.join(*self.get_portions(),*paths)
	
	# def create_file_path(self,ext,dir_depth=1):
	# 	return create_info_path(self,ext=ext,*self.get_portions(),dir_depth=dir_depth)
	
	def get_portions(self):
		portions=list()
		for k,v in self.items():
			if not v is None: portions.append(f"{k}_{v}")
			else: portions.append(k)
		return portions
	
	def get_text(self,delim="__"):
		return delim.join(self.get_portions())
	
	def __str__(self):
		return self.get_text()

class ZipError(Exception):
	pass

class CopyError(Exception):
	pass

def _make_zipfile(base_name,base_dir,root_dir=None,dry_run=0,logger=None):
	"""Create a zip file from all the files under 'base_dir'.

	The output zip file will be named 'base_name' + ".zip".  Returns the
	name of the output zip file.
	"""
	save_cwd=os.getcwd()
	if root_dir: os.chdir(root_dir)
	zip_filename=base_name+".zip"
	archive_dir=os.path.dirname(base_name)
	
	if archive_dir and not os.path.exists(archive_dir):
		if logger is not None:
			logger.debug("creating %s",archive_dir)
		if not dry_run:
			os.makedirs(archive_dir)
	
	if logger is not None:
		logger.debug("creating '%s' and adding '%s' to it",
		             zip_filename,base_dir)
	
	if not dry_run:
		with zipfile.ZipFile(zip_filename,"w",
		                     compression=zipfile.ZIP_DEFLATED) as zf:
			path=os.path.normpath(base_dir)
			if path!=os.curdir:
				zf.write(path,path)
				if logger is not None:
					logger.debug("adding '%s'",path)
			for dirpath,dirnames,filenames in os.walk(base_dir):
				for name in sorted(dirnames):
					path=os.path.normpath(os.path.join(dirpath,name))
					zf.write(path,path)
					if logger is not None:
						logger.debug("adding '%s'",path)
				for name in filenames:
					path=os.path.normpath(os.path.join(dirpath,name))
					if os.path.isfile(path):
						zf.write(path,path)
						if logger is not None:
							logger.debug("adding '%s'",path)
	os.chdir(save_cwd)
	return zip_filename

# class RemoteFolder(Folder):
#
# 	def __init__(self,path=''):
# 		super().__init__(path='')
# 		self.path=path
#
# 	def create(self,*child_folders,**info_kwargs):
# 		return super().create(*child_folders,is_remote=True,**info_kwargs)
#
# 	def delete(self):
# 		raise NotImplementedError
#
# 	def children(self,*paths):
# 		raise NotImplementedError

get_neighbor_path=lambda curr_path,filename:os.path.join(get_parent_dir(curr_path),filename)

def get_paths_matching(target_dir,match: str):
	items=os.listdir(target_dir)
	outs=list()
	for item in items:
		if match in item: outs.append(os.path.join(target_dir,item))
	return outs

def replace_ext(fpath,out_extension):
	base_path,ext=os.path.splitext(fpath)
	return base_path+out_extension

def find_file(directory,pattern):
	for root,dirs,files in os.walk(directory):
		for basename in files:
			if fnmatch.fnmatch(basename,pattern):
				filename=os.path.join(root,basename)
				return filename

def main():
	# project_folder=Folder(__file__)
	# logs_folder=project_folder.create('log_files')
	# results_folder=project_folder.create('Results')
	# test_folder=Folder(r'/home/lgblkb/PycharmProjects/Egistic/Scripts/lgblkb_local_folder_2')
	# dst_folder=Folder(r'/home/lgblkb/PycharmProjects/Egistic/lgblkb_scripts')
	# test_folder.copy_to(dst_folder)
	
	pass

if __name__=='__main__':
	main()
