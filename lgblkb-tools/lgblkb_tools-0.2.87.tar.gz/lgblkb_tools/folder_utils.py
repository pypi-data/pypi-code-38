import glob
import logging
import os
import shutil
import time
import zipfile
from datetime import datetime
from typing import Callable,List

import numpy as np
import pandas as pd
import itertools
import collections

from box import Box
from checksumdir import dirhash

from lgblkb_tools import log_support as logsup
from lgblkb_tools.locations import get_parent_dir,get_splitted,InfoDict,create_path,_make_zipfile,ZipError,get_existing_path,get_name,CopyError

class Folder(object):
	
	def __init__(self,path='',pseudo=False,parent=None,propagate_type=False,assert_exists=False):
		if isinstance(path,Folder): path=path.path
		assert isinstance(pseudo,bool)
		if not pseudo:
			if not path: path=os.getcwd()
			elif not os.path.exists(path):
				if assert_exists: raise AssertionError(f'The path {path} should exist.',dict(path=path))
				assert os.path.splitext(os.path.split(path)[-1])[-1]=='',f"Please, use folder path as input. Provided path is: \n{path}"
				os.makedirs(path)
			elif not os.path.isdir(path):
				path=get_parent_dir(path,1)
		self.path=path
		self.pseudo=pseudo
		self.__parent=parent
		self.__propagate_type=propagate_type
	
	@classmethod
	def create_for_filepath(cls,filepath):
		os.makedirs(get_parent_dir(filepath),exist_ok=True)
		return cls(filepath)
	
	@property
	def name(self):
		return os.path.split(self.path)[-1]
	
	def get_filepath(self,*name_portions,ext='',delim='_',include_depth=None,datetime_loc_index=None,iterated=False,**name_kwargs):
		parts=list()
		if include_depth not in [0,None]:
			if type(include_depth) is Callable:
				parent_parts=include_depth(get_splitted(self.path))
			elif type(include_depth) is int:
				parent_parts=get_splitted(self.path)[-include_depth:]
			elif type(include_depth) in [tuple,list]:
				parent_parts=[get_splitted(self.path)[-x] for x in include_depth]
			else:
				raise NotImplementedError(f'include_depth={include_depth}')
			parts.extend(parent_parts)
		part_portions=delim.join([str(x) for x in name_portions])
		if part_portions: parts.append(part_portions)
		part_kwargs=InfoDict(name_kwargs).get_portions()
		if part_kwargs: parts.extend(part_kwargs)
		if datetime_loc_index is not None: parts.insert(datetime_loc_index,datetime.now().strftime("%Y%m%d-%H:%M:%S"))
		assert parts,'Nothing is provided to create filepath.'
		output_path=os.path.join(self.path,delim.join(parts).replace(' ',delim)+ext)
		if iterated:
			return create_iterated_path(output_path)
		else:
			return output_path
	
	def _mkdir(self,child_dirpath):
		return create_path(self.path,child_dirpath)
	
	def create(self,*child_folders,**info_kwargs):
		parts=list()
		if child_folders: parts.extend(child_folders)
		if info_kwargs: parts.extend(InfoDict(info_kwargs).get_portions())
		assert parts,'Nothing is provided to create directory'
		child_dirpath='__'.join(map(str,parts))
		
		if self.pseudo: path=os.path.join(self.path,child_dirpath)
		else: path=self._mkdir(child_dirpath)
		if self.__propagate_type:
			return self.__class__(path,pseudo=self.pseudo,parent=self)
		else:
			return Folder(path,pseudo=self.pseudo,parent=self,propagate_type=True)
	
	def delete(self):
		if self.pseudo: raise OSError('Cannot delete when in "pseudo" mode.')
		shutil.rmtree(self.path)
	
	def clear(self):
		if self.pseudo: raise OSError('Cannot delete when in "pseudo" mode.')
		self.delete()
		create_path(self.path)
	
	def children(self,*paths):
		return glob.glob(os.path.join(self.path,*(paths or '*')))
	
	@logsup.with_logging(log_level=logging.DEBUG)
	def zip(self,zip_filepath='',save_path_formatter=None,forced=False):
		max_attempts=5
		if not zip_filepath: zipfile_basepath=self.parent().get_filepath(self.name)
		elif zip_filepath[-4:]=='.zip': zipfile_basepath=zip_filepath[:-4]
		else: zipfile_basepath=zip_filepath
		if save_path_formatter is not None: zipfile_basepath=save_path_formatter(zipfile_basepath)
		if not forced:
			fullpath=zipfile_basepath+'.zip'
			if os.path.exists(fullpath) and not zipfile.ZipFile(fullpath).testzip():
				return fullpath
		
		for i in range(max_attempts):
			fullpath=_make_zipfile(base_name=zipfile_basepath,root_dir=get_parent_dir(self.path),base_dir=self.name)
			#shutil.make_archive(base_name=zipfile_basepath,format='zip',root_dir=get_parent_dir(self.path),base_dir=self.name)
			zip_obj=zipfile.ZipFile(fullpath)
			if not zip_obj.testzip():
				return fullpath
			else:
				os.remove(fullpath)
		raise ZipError(f'Could not zip {self.path} to {zipfile_basepath}.zip.')
	
	@logsup.with_logging(log_level=logging.DEBUG)
	def zip_to(self,dest_folder,zipname='',save_path_formatter=None,forced=False):
		return self.zip(Folder(dest_folder).get_filepath(zipname or self.name),save_path_formatter=save_path_formatter,forced=forced)
	
	@logsup.with_logging(log_level=logging.DEBUG)
	def unzip(self,zip_filepath,create_subdir=True):
		# if save_path_formatter is None: save_path_formatter=lambda x:x
		zip_path=[zip_filepath,
		          zip_filepath+'.zip',
		          self.get_filepath(zip_filepath),
		          self.get_filepath(zip_filepath,ext='.zip')]
		zip_path=get_existing_path(zip_path)
		assert not os.path.isdir(zip_path),f'The folder "{zip_filepath}" cannot be unzipped.'
		if create_subdir:
			zipfilename=get_name(zip_path)
			# self.get_filepath(zipfilename)
			shutil.unpack_archive(zip_path,self.create(zipfilename).path,'zip')
		
		else:
			shutil.unpack_archive(zip_path,self.path,'zip')
		return self
	
	def glob_search(self,*patterns,recursive=True):
		return glob.glob(self.get_filepath(*patterns),recursive=recursive)
	
	def find_item(self,partial_name,ending='*'):
		filepath=self.glob_search(f'**/*{partial_name}{ending}')
		if filepath: return filepath[0]
		else: return ''
	
	def rename(self,new_name):
		new_path=os.path.join(get_parent_dir(self.path),new_name)
		os.rename(self.path,new_path)
		self.path=new_path
		return self
	
	def move(self,dst_path,create_subdir=True):
		if self.__propagate_type: classtype=self.__class__
		else: classtype=Folder
		if create_subdir: destination_folder=classtype(dst_path).create(self.name)
		else: destination_folder=classtype(dst_path)
		shutil.move(self.path,destination_folder.path)
		return destination_folder
	
	def parent(self,depth=1):
		if self.__propagate_type: classtype=self.__class__
		else: classtype=Folder
		return classtype(get_parent_dir(self.path,depth=depth),pseudo=self.pseudo)
	
	@logsup.with_logging(log_level=logging.DEBUG)
	def copy_to(self,dst_path,create_subdir=True,forced=False):
		# if self.__propagate_type: classtype=self.__class__
		# else: classtype=partial(Folder,pseudo=True)
		if create_subdir: destination_folder=self.__class__(self.__class__(dst_path).create(self.name),
		                                                    pseudo=self.pseudo,propagate_type=self.__propagate_type)
		else: destination_folder=self.__class__(dst_path,pseudo=self.pseudo,propagate_type=self.__propagate_type)
		
		logsup.logger.debug(f'Copying {self.path} to {destination_folder.path}...')
		source_hashsum=dirhash(self.path)
		if not forced and os.path.exists(destination_folder.path):
			destination_hashsum=dirhash(destination_folder.path)
			if source_hashsum==destination_hashsum: return destination_folder
		max_tries=3
		for i in range(3):
			#if os.path.exists(destination_folder.path):
			shutil.rmtree(destination_folder.path,ignore_errors=True)
			shutil.copytree(self.path,destination_folder.path)
			destination_hashsum=dirhash(destination_folder.path)
			if source_hashsum==destination_hashsum: return destination_folder
			else:
				logsup.logger.warning('source_hashsum',source_hashsum)
				logsup.logger.warning('destination_hashsum',destination_hashsum)
				logsup.logger.warning(
					f'Warning!!!!!!!!!. Copied folder has different hashsum than its source. Try {i}/{max_tries}. Waiting for 10 sec.')
				time.sleep(10)
		raise CopyError(f'{self} could not be copied to {destination_folder}.',dict(source_folder=self.path,
		                                                                            destination_folder=destination_folder.path))
	
	def get_size_in_gb(self):
		total_size=0
		for dirpath,dirnames,filenames in os.walk(self.path):
			for f in filenames:
				fp=os.path.join(dirpath,f)
				total_size+=os.path.getsize(fp)
		return total_size*1e-9
	
	@property
	def exists(self):
		return os.path.exists(self.path)
	
	def create_iterated(self,start=None,delim='_',empty_ok=False):
		if empty_ok: validator_func=lambda existing_path:not self.__class__(existing_path).children()
		else: validator_func=lambda existing_path:existing_path==self.path
		
		new_iter_folder_path=create_iterated_path(self.path,start,delim,validator_func=validator_func)
		last_part=new_iter_folder_path.split(delim)[-1]
		if last_part.isnumeric() and int(last_part)==(start or 0):
			new_folder=self.rename(new_iter_folder_path)
		else:
			new_folder=self.__class__(new_iter_folder_path)
			if not new_folder==self and not self.children(): self.delete()
		
		# base_folder=self.rename(delim.join([self.name,f'{start}']))
		# new_path=create_iterated_path(base_folder.path,delim)
		# while base_folder.children():
		#
		# 	existing_path=base_folder.path
		# 	old_counter=base_folder.path.split('_')[-1]
		# 	new_counter=int(old_counter)+1
		# 	new_path=existing_path[:-len(old_counter)]+str(new_counter)
		# 	base_folder=self.__class__(new_path)
		return new_folder
	
	def __getitem__(self,item):
		if os.path.splitext(item)[-1]:
			return self.get_filepath(item)
		else:
			return self.create(item)
	
	def __eq__(self,other):
		if isinstance(other,str):
			return self.path==other
		else:
			return self.path==self.__class__(other).path
	
	def __setitem__(self,key,value):
		filename,ext=os.path.splitext(key)
		if isinstance(value,str): string_obj=value
		elif type(value) in [list,tuple]:
			string_obj='\n'.join(map(str,value))
		elif isinstance(value,dict):
			ext=ext or '.yaml'
			if ext in ['.yaml','.yml']:
				Box(value).to_yaml(filename=self.get_filepath(filename,ext=ext))
				return
			elif ext=='.json':
				Box(value).to_json(filename=self.get_filepath(filename,ext=ext))
				return
			else:
				string_obj='\n'.join(map(lambda kv:f"{kv[0]}: {kv[1]}",value.items()))
		
		else: string_obj=str(value)
		# def writer(filehandler):
		# 	for k,v in value.items():
		# 		filehandler.writelines([f"{k}: {v}"])
		
		with open(self.get_filepath(filename,ext=ext or '.txt'),'w') as fh:
			fh.write(str(string_obj))
	
	def __repr__(self):
		return f"{self.__class__.__name__}(r'{self.path}')"

def create_iterated_path(iterated_path: str,start=None,delim='_',validator_func=None) -> str:
	if validator_func is None: validator_func=lambda x:False
	base_path,item_name_with_ext=os.path.split(iterated_path)
	item_name,ext=os.path.splitext(item_name_with_ext)
	# parts: List[str]=item_name.split(delim)
	# the_parts: list=parts[:]
	# for i_part,part in enumerate(parts[::-1]):
	# 	if part.isnumeric():
	# 		curr_iter=int(part) if start is None else start#max(start,int(part))
	# 		while True:
	# 			the_parts[len(parts)-i_part-1]=curr_iter
	# 			new_item_name=delim.join(map(str,the_parts))
	# 			new_itempath=os.path.join(base_path,new_item_name+ext)
	# 			if not os.path.exists(new_itempath) or validator_func(new_itempath): return new_itempath
	# 			curr_iter+=1
	
	curr_iter=0 if start is None else start
	while True:
		new_item_name=delim.join([item_name,f'{curr_iter}'])
		new_itempath=os.path.join(base_path,new_item_name+ext)
		if not os.path.exists(new_itempath) or validator_func(new_itempath): return new_itempath
		curr_iter+=1
