import posixpath
import stat
import os
from abc import abstractmethod

from fabric import Connection
from fabric.transfer import Transfer,Result

import lgblkb_tools.folder_utils
from . import global_support as gsup,log_support as logsup

# class FabricTransfer(Transfer):
#
# 	def get(self,remote,local=None,preserve_mode=True):
# 		"""
# 		Download a file from the current connection to the local filesystem.
#
# 		:param str remote:
# 			Remote file to download.
#
# 			May be absolute, or relative to the remote working directory.
#
# 			.. note::
# 				Most SFTP servers set the remote working directory to the
# 				connecting user's home directory, and (unlike most shells) do
# 				*not* expand tildes (``~``).
#
# 				For example, instead of saying ``get("~/tmp/archive.tgz")``,
# 				say ``get("tmp/archive.tgz")``.
#
# 		:param local:
# 			Local path to store downloaded file in, or a file-like object.
#
# 			**If None or another 'falsey'/empty value is given** (the default),
# 			the remote file is downloaded to the current working directory (as
# 			seen by `os.getcwd`) using its remote filename.
#
# 			**If a string is given**, it should be a path to a local directory
# 			or file and is subject to similar behavior as that seen by common
# 			Unix utilities or OpenSSH's ``sftp`` or ``scp`` tools.
#
# 			For example, if the local path is a directory, the remote path's
# 			base filename will be added onto it (so ``get('foo/bar/file.txt',
# 			'/tmp/')`` would result in creation or overwriting of
# 			``/tmp/file.txt``).
#
# 			.. note::
# 				When dealing with nonexistent file paths, normal Python file
# 				handling concerns come into play - for example, a ``local``
# 				path containing non-leaf directories which do not exist, will
# 				typically result in an `OSError`.
#
# 			**If a file-like object is given**, the contents of the remote file
# 			are simply written into it.
#
# 		:param bool preserve_mode:
# 			Whether to `os.chmod` the local file so it matches the remote
# 			file's mode (default: ``True``).
#
# 		:returns: A `.Result` object.
#
# 		.. versionadded:: 2.0
# 		"""
# 		# TODO: how does this API change if we want to implement
# 		# remote-to-remote file transfer? (Is that even realistic?)
# 		# TODO: handle v1's string interpolation bits, especially the default
# 		# one, or at least think about how that would work re: split between
# 		# single and multiple server targets.
# 		# TODO: callback support
# 		# TODO: how best to allow changing the behavior/semantics of
# 		# remote/local (e.g. users might want 'safer' behavior that complains
# 		# instead of overwriting existing files) - this likely ties into the
# 		# "how to handle recursive/rsync" and "how to handle scp" questions
#
# 		# Massage remote path
# 		if not remote:
# 			raise ValueError("Remote path must not be empty!")
# 		orig_remote=remote
# 		remote=posixpath.join(
# 			self.sftp.getcwd() or self.sftp.normalize("."),remote
# 			)
#
# 		# Massage local path:
# 		# - handle file-ness
# 		# - if path, fill with remote name if empty, & make absolute
# 		orig_local=local
# 		is_file_like=hasattr(local,"write") and callable(local.write)
# 		if not local:
# 			local=posixpath.basename(remote)
# 		if not is_file_like:
# 			local=os.path.abspath(local)
#
# 		# Run Paramiko-level .get() (side-effects only. womp.)
# 		# TODO: push some of the path handling into Paramiko; it should be
# 		# responsible for dealing with path cleaning etc.
# 		# TODO: probably preserve warning message from v1 when overwriting
# 		# existing files. Use logging for that obviously.
# 		#
# 		# If local appears to be a file-like object, use sftp.getfo, not get
# 		if is_file_like:
# 			self.sftp.getfo(remotepath=remote,fl=local,confirm=False)
# 		else:
# 			self.sftp.get(remotepath=remote,localpath=local)
# 			# Set mode to same as remote end
# 			# TODO: Push this down into SFTPClient sometime (requires backwards
# 			# incompat release.)
# 			if preserve_mode:
# 				remote_mode=self.sftp.stat(remote).st_mode
# 				mode=stat.S_IMODE(remote_mode)
# 				os.chmod(local,mode)
# 		# Return something useful
# 		return Result(
# 			orig_remote=orig_remote,
# 			remote=remote,
# 			orig_local=orig_local,
# 			local=local,
# 			connection=self.connection,
# 			)
#
# 	def put(self,local,remote=None,preserve_mode=True):
# 		"""
# 		Upload a file from the local filesystem to the current connection.
#
# 		:param local:
# 			Local path of file to upload, or a file-like object.
#
# 			**If a string is given**, it should be a path to a local (regular)
# 			file (not a directory).
#
# 			.. note::
# 				When dealing with nonexistent file paths, normal Python file
# 				handling concerns come into play - for example, trying to
# 				upload a nonexistent ``local`` path will typically result in an
# 				`OSError`.
#
# 			**If a file-like object is given**, its contents are written to the
# 			remote file path.
#
# 		:param str remote:
# 			Remote path to which the local file will be written.
#
# 			.. note::
# 				Most SFTP servers set the remote working directory to the
# 				connecting user's home directory, and (unlike most shells) do
# 				*not* expand tildes (``~``).
#
# 				For example, instead of saying ``put("archive.tgz",
# 				"~/tmp/")``, say ``put("archive.tgz", "tmp/")``.
#
# 				In addition, this means that 'falsey'/empty values (such as the
# 				default value, ``None``) are allowed and result in uploading to
# 				the remote home directory.
#
# 			.. note::
# 				When ``local`` is a file-like object, ``remote`` is required
# 				and must refer to a valid file path (not a directory).
#
# 		:param bool preserve_mode:
# 			Whether to ``chmod`` the remote file so it matches the local file's
# 			mode (default: ``True``).
#
# 		:returns: A `.Result` object.
#
# 		.. versionadded:: 2.0
# 		"""
# 		if not local:
# 			raise ValueError("Local path must not be empty!")
#
# 		is_file_like=hasattr(local,"write") and callable(local.write)
#
# 		# Massage remote path
# 		orig_remote=remote
# 		if is_file_like:
# 			local_base=getattr(local,"name",None)
# 		else:
# 			local_base=os.path.basename(local)
# 		if not remote:
# 			if is_file_like:
# 				raise ValueError(
# 					"Must give non-empty remote path when local is a file-like object!"  # noqa
# 					)
# 			else:
# 				remote=local_base
# 				# debug("Massaged empty remote path into {!r}".format(remote))
# 				pass
# 		elif self.is_remote_dir(remote):
# 			# non-empty local_base implies a) text file path or b) FLO which
# 			# had a non-empty .name attribute. huzzah!
# 			if local_base:
# 				remote=posixpath.join(remote,local_base)
# 			else:
# 				if is_file_like:
# 					raise ValueError(
# 						"Can't put a file-like-object into a directory unless it has a non-empty .name attribute!"  # noqa
# 						)
# 				else:
# 					# TODO: can we ever really end up here? implies we want to
# 					# reorganize all this logic so it has fewer potential holes
# 					raise ValueError(
# 						"Somehow got an empty local file basename ({!r}) when uploading to a directory ({!r})!".format(  # noqa
# 							local_base,remote
# 							)
# 						)
#
# 		prejoined_remote=remote
# 		remote=posixpath.join(
# 			self.sftp.getcwd() or self.sftp.normalize("."),remote
# 			)
# 		if remote!=prejoined_remote:
# 			# msg="Massaged relative remote path {!r} into {!r}"
# 			# debug(msg.format(prejoined_remote,remote))
# 			pass
#
# 		# Massage local path
# 		orig_local=local
# 		if not is_file_like:
# 			local=os.path.abspath(local)
# 			if local!=orig_local:
# 				# debug(
# 				# 	"Massaged relative local path {!r} into {!r}".format(
# 				# 		orig_local,local
# 				# 		)
# 				# 	)  # noqa
# 				pass
#
# 		# Run Paramiko-level .put() (side-effects only. womp.)
# 		# TODO: push some of the path handling into Paramiko; it should be
# 		# responsible for dealing with path cleaning etc.
# 		# TODO: probably preserve warning message from v1 when overwriting
# 		# existing files. Use logging for that obviously.
# 		#
# 		# If local appears to be a file-like object, use sftp.putfo, not put
# 		if is_file_like:
# 			# msg="Uploading file-like object {!r} to {!r}"
# 			# debug(msg.format(local,remote))
#
# 			pointer=local.tell()
# 			try:
# 				local.seek(0)
# 				self.sftp.putfo(fl=local,remotepath=remote,confirm=False)
# 			finally:
# 				local.seek(pointer)
# 		else:
# 			# debug("Uploading {!r} to {!r}".format(local,remote))
# 			self.sftp.put(localpath=local,remotepath=remote,confirm=False)
# 			# Set mode to same as local end
# 			# TODO: Push this down into SFTPClient sometime (requires backwards
# 			# incompat release.)
# 			if preserve_mode:
# 				local_mode=os.stat(local).st_mode
# 				mode=stat.S_IMODE(local_mode)
# 				self.sftp.chmod(remote,mode)
# 		# Return something useful
# 		return Result(
# 			orig_remote=orig_remote,
# 			remote=remote,
# 			orig_local=orig_local,
# 			local=local,
# 			connection=self.connection,
# 			)
#
# class FabricConnection(Connection):
#
# 	def get(self,*args,**kwargs):
# 		return FabricTransfer(self).get(*args,**kwargs)
#
# 	def put(self,*args,**kwargs):
# 		"""
# 		Put a remote file (or file-like object) to the remote filesystem.
#
# 		Simply a wrapper for `.Transfer.put`. Please see its documentation for
# 		all details.
#
# 		.. versionadded:: 2.0
# 		"""
# 		return FabricTransfer(self).put(*args,**kwargs)

class SshMan(object):
	
	def __init__(self,fabric_connection: Connection,remote_workdir: lgblkb_tools.folder_utils.Folder):
		self.conn: Connection=fabric_connection
		# if isinstance(remote_workdir,str): remote_workdir=remote_projects_dir.create(
		# 	remote_workdir)
		assert isinstance(remote_workdir,lgblkb_tools.folder_utils.Folder),f"'remote_workdir' is neither a Folder nor a string."
		self.work_folder: lgblkb_tools.folder_utils.Folder=remote_workdir
		# if self.conn.run(f'[ -d "{remote_workdir.path}" ] && echo "exist" || echo "not exist"',warn=True).stdout.strip()=='not exist':
		# 	logsup.logger.info('Creating folder %s on remote host.',remote_workdir.path)
		# 	self.conn.run(f'mkdir -p {remote_workdir.path}')
		pass
	
	def check_exists(self,program_name):
		which_result=self.conn.run(f'which {program_name}',warn=True)
		if which_result.failed: return False
		else:
			logsup.logger.info(f'"{program_name}" already exists.')
			return True
	
	def apt_install(self,*package_names,forced=False):
		names=list()
		for package_name in package_names:
			pack_names=[x for x in package_name.split(" ") if x]
			names.extend(pack_names)
		
		if not forced:
			for package_name in names.copy():
				if self.check_exists(package_name):
					names.remove(package_name)
					logsup.logger.info('Skipping installation of "%s".',package_name)
		
		for package_name in names:
			self.run(f'sudo apt-get install {package_name} -y')
			package_path=self.conn.run(f'which {package_name}',warn=True).stdout.strip()
			logsup.logger.debug('"%s" path: %s',package_name,package_path)
	
	@abstractmethod
	def initial_setup(self,*args,**kwargs):
		pass
	
	@abstractmethod
	def execute(self,*args,**kwargs):
		pass
	
	def run(self,command,**kwargs):
		logsup.logger.info('Running !!!%s!!!',command)
		return self.conn.run(command,**kwargs)
	
	def put(self,local,remote,preserve_mode=True,absolute_remote=False):
		if not absolute_remote: remote=self.work_folder.get_filepath(remote)
		logsup.logger.info('Putting from !!!%s!!! to !!!%s!!!',local,remote)
		out=self.conn.put(local,remote=remote,preserve_mode=preserve_mode)
		return out
	
	def get(self,remote,local=None,preserve_mode=True):
		logsup.logger.info('Getting from !!!%s!!! to !!!%s!!!',remote,local)
		out=self.conn.get(remote,local=local,preserve_mode=preserve_mode)
		return out
	
	def cd(self,path):
		return self.conn.cd(path=path)
	
	def cd_to_working_dir(self):
		return self.cd(self.work_folder.path)
	
	def prefix(self,command):
		return self.conn.prefix(command=command)
	
	def sudo(self,command,**kwargs):
		return self.conn.sudo(command=command,**kwargs)

class SshFolder(lgblkb_tools.folder_utils.Folder):
	
	def __init__(self,remote_path,pseudo=False,parent=None,**conn_kwargs):
		super(SshFolder,self).__init__(remote_path,pseudo=True,parent=parent,propagate_type=True)
		self.pseudo=pseudo
		if parent is None:
			self.fabric_conn=Connection(**conn_kwargs)
		else:
			# self.sshman: SshMan=parent.sshman
			# self.sshman.work_folder=self
			self.fabric_conn=parent.fabric_conn
		self.sshman=SshMan(self.fabric_conn,self)
	
	def _mkdir(self,child_dirpath):
		with self.sshman.cd_to_working_dir():
			self.sshman.conn.run(f'mkdir -p {child_dirpath}')
		return os.path.join(self.path,child_dirpath)
	
	def children(self):
		with self.sshman.cd_to_working_dir():
			item_names=self.sshman.run('ls').stdout.strip().split('\n')
		return list(map(lambda x:os.path.join(self.path,x),item_names))
	
	def delete(self):
		with self.sshman.cd_to_working_dir():
			self.sshman.run(f"""
cd ..
rm -r {self.path}
""")
	
	def clear(self):
		with self.sshman.cd_to_working_dir():
			self.sshman.run(f'rm -rf *')
	
	def md5(self,remote_filepath):
		return self.sshman.conn.run(f'md5sum {remote_filepath}',warn=True).stdout.strip().split(' ')[0]
	
	def upload_item(self,local_itempath,only_children=True):
		item_base_name=os.path.split(local_itempath)[-1]
		if os.path.isdir(local_itempath):
			if only_children:
				for item_to_upload in lgblkb_tools.folder_utils.Folder(local_itempath).children():
					self.upload_item(item_to_upload,only_children=False)
				pass
			else:
				remote_folder=self.create(item_base_name)
				for local_sub_item_path in lgblkb_tools.folder_utils.Folder(local_itempath).children():
					remote_folder.upload_item(local_sub_item_path)
		else:
			local_checksum=gsup.md5(local_itempath)
			remote_filepath=self.get_filepath(item_base_name)
			while local_checksum!=self.md5(remote_filepath):
				self.sshman.run(f"""rm {remote_filepath}""",warn=True)
				self.sshman.put(local_itempath,remote_filepath,absolute_remote=True)
		return remote_filepath
	
	def run(self,command,**kwargs):
		return self.sshman.run(command=command,**kwargs).stdout.strip()
	
	def run_with_cd(self,command,**kwargs):
		with self.sshman.cd_to_working_dir():
			return self.run(command,**kwargs)
	
	def get(self,remote,local=None,preserve_mode=True):
		return self.sshman.get(remote,local=local,preserve_mode=preserve_mode)
	
	def put(self,local,remote,preserve_mode=True,absolute_remote=False):
		return self.sshman.put(local,remote,preserve_mode=preserve_mode,absolute_remote=absolute_remote)

def main():
	pass

if __name__=='__main__':
	main()
