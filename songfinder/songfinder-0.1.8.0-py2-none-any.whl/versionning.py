# -*- coding: utf-8 -*-


import Tkinter as tk
import os
from songfinder import messages as tkMessageBox
import subprocess
import getpass
import tkSimpleDialog
import shutil
import warnings
#~ from mercurial import commands, ui, hg
#~ import hglib
#~ import mercurial
#~ repo = hg.repository('C:\\Users\\beidan\\Documents\\songFinderData', ui.ui())

try: # Windows only imports
	import win32con, win32api
except ImportError:
	pass

from songfinder import fonctions as fonc
from songfinder import commandLine
from songfinder import globalvar
from songfinder import guiHelper
from songfinder import classSettings as settings

#~ client = hglib.open( os.path.join(os.path.expanduser("~"), "Documents", "songFinderData") )
#~ print(client.status())

COMMANDS = {'addAll':{'hg':'addr', 'git': 'add -A'},\
			'pullUpdate':{'hg':'pull -u', 'git': 'pull'},\
			'resetHead':{'hg':'update -C', 'git': 'reset --hard'},\
			'configFile':{'hg':'hgrc', 'git': 'config'},\
			'insecure':{'hg':' --insecure', 'git': ''},\
			'remote':{'hg':'default', 'git': 'origin'},\
			}

CLEUSB = {'USBEI', 'USBETIENNE'}

class AddRepo(object, tk.Frame): # TODO integrate to repo class
	def __init__(self, fenetre, paths, exe, interface, **kwargs):
		tk.Frame.__init__(self, fenetre, **kwargs)
		self.grid()
		self.paths = paths
		self.fen_clone = fenetre
		self.interface = interface

		self.__exe = exe
		self.__scm = commandLine.MyCommand(self.__exe)
		self.__scm.checkCommand()

		self.ok_button = tk.Button(self, text='Cloner', command=self.cloneRepo)
		self.remote = tk.Entry(self, width=60)
		self.user = tk.Entry(self, width=30)
		self.password = tk.Entry(self, width=30)
		self.param = [self.remote, self.user, self.password]
		labelsStr = ["Chemin", "Utilisateur", "Mot de passe"]
		self.labels = []
		for i, param in enumerate(self.param):
			label = tk.Label(self, text=labelsStr[i], justify='left')
			label.grid(row=i, column=0, columnspan=5, sticky='w' )
			self.labels.append(label)
			param.grid(row=i, column=5, columnspan=20, sticky='w' )
		self.ok_button.grid(row=len(self.param), column=0, columnspan=1, sticky='w' )

		self.bind_all("<KeyRelease-Return>", self.cloneRepo)

	def close(self):
		self.fen_clone.destroy()
		self.fen_clone = None

	def cloneRepo(self, event=0):
		guiHelper.update_fen(self.fen_clone, u'Récupération des informations ...')
		repo = self.remote.get()
		name = self.user.get()
		mdp = self.password.get()
		if not (repo and name and mdp):
			guiHelper.update_fen(self.fen_clone, u"    échec\n")
			tkMessageBox.showerror(u'Erreur', u'Erreur: les informations sont incomplètes', parent = self.fen_clone)
		else:
			self.fen_clone.prog.grid(sticky='w')
			guiHelper.update_fen(self.fen_clone, u"    ok\nVerification de la connexion ...")
			if commandLine.ping('google.fr') == 0:
				guiHelper.update_fen(self.fen_clone, u"    ok\n")
			else:
				guiHelper.update_fen(self.fen_clone, u"    échec\n")
				#https://epef@bitbucket.org/epef/data

			if repo:
				guiHelper.update_fen(self.fen_clone, u"Clonage du dépôt (ceci peut prendre quelques minutes) ...")
				shutil.rmtree(self.paths.root)
				os.makedirs(self.paths.root)
				os.chdir(self.paths.root)
				arrobase = repo.find('@')
				user = repo[repo.find('://')+3:arrobase]
				prefix = repo[arrobase+1:]
				fullrepo = repo[:arrobase] + ':' + mdp + repo[arrobase:]
				code, out, err = self.__scm.run( options=['clone%s'%COMMANDS['insecure'][self.__exe], fullrepo, '.'] )
				try:
					self.makeHidden(os.path.join(self.paths.root, '.hg'))
					self.makeHidden(os.path.join(self.paths.root, '.hgignore'))
					self.makeHidden(os.path.join(self.paths.root, 'bitbucket-pipelines.yml'))
				except Exception as e:
					warnings.warn('Failed to make file hidden\n:%s'%str(e))
			if code != 0:
				guiHelper.update_fen(self.fen_clone, u"    échec\n")
				tkMessageBox.showerror(u'Erreur', u'Erreur: le clonage du dépôt à échoué\nErreur %s:\n%s'%(str(code), err), parent = self.fen_clone)
				self.close()
				settings.GENSETTINGS.set('Parameters', 'sync', 'non')
			else:
				configContent = """# example repository config (see 'hg help config' for more info)
[paths]
default = %s

# path aliases to other clones of this repo in URLs or filesystem paths
# (see 'hg help config.paths' for more info)
#
# default:pushurl = ssh://jdoe@example.net/hg/jdoes-fork
# my-fork         = ssh://jdoe@example.net/hg/jdoes-fork
# my-clone        = /home/jdoe/jdoes-clone

[auth]
sfData.prefix = %s
sfData.username = %s
sfData.password = %s

[ui]
# name and email (local to this repository, optional), e.g.
username = %s
"""%(repo, prefix, user, mdp, name)
				configFile = open(os.path.join('.%s'%self.__exe, COMMANDS['configFile'][self.__exe]), "w")
				configFile.write(configContent)
				guiHelper.update_fen(self.fen_clone, u"    ok\n")
				tkMessageBox.showinfo(u'Confirmation', u'Le dépôt à été cloné.', parent = self.fen_clone)
				if hasattr(self.interface, 'updateData'):
					self.interface.updateData()
				self.close()

			os.chdir(globalvar.chemin_root)
	def makeHidden(self, path):
		try:
			win32api.SetFileAttributes(path,win32con.FILE_ATTRIBUTE_HIDDEN)
		except NameError: # For Ubuntu
			pass

class Repo(object):
	def __init__(self, path, exe, showGui, papa=None, screen=None, **kwargs):
		self.__myOs = globalvar.myOs
		self.__papa = papa
		self.__path = path
		self.__screen = screen

		self.__exe = exe
		self.__scm = commandLine.MyCommand(self.__exe)
		self.__scm.checkCommand()
		self.__commitName = 'Song Finder v%s'%globalvar.version
		self.__showGui = showGui

	def __gui(self):
		if self.__showGui:
			self.__fen_recv = tk.Toplevel(self.__papa)
			self.__fen_recv.wm_attributes("-topmost", 1)
			self.__fen_recv.title("Reception/Envoi")
			self.__fen_recv.grab_set()
			self.__fen_recv.focus_set()
			self.__fen_recv.resizable(False,False)
			self.__fen_recv.prog = tk.Label(self.__fen_recv, text="", justify='left')
			self.__fen_recv.prog.grid(sticky='w')
			self.__fen_recv.update()
			if self.__screen:
				width = self.__fen_recv.winfo_width()
				height = self.__fen_recv.winfo_height()
				Xpos = (self.__screen.w - width) // 2
				Ypos = (self.__screen.h - height) // 2
				self.__fen_recv.geometry('+{}+{}'.format(Xpos, Ypos))
		else:
			self.__fen_recv = None

	def __update_fen(self, message):
		if self.__showGui:
			newText = self.__fen_recv.prog["text"].replace('...', '')
			exceList = set(self.__usbFound) | {u'ok', u'échec', u'aucune'}
			if not set(message.split(' ')) & exceList:
				newText += '\n'
			newText += message
			newText = fonc.strip_perso(newText.replace('\n\n','\n'), '\n')
			self.__fen_recv.prog["text"] = newText
			self.__fen_recv.update()

	def __showError(self, message):
		self.__update_fen(u'    échec')
		tkMessageBox.showerror(u'Erreur', message, parent = self.__fen_recv)
		self.__close()
		return 1

	def __showInfo(self, message):
		self.__update_fen(u'    ok')
		if self.__showGui:
			tkMessageBox.showinfo(u'Confirmation', message, parent = self.__fen_recv)
		self.__close()
		return 0

	def __close(self):
		os.chdir(globalvar.chemin_root)
		if self.__showGui:
			self.__fen_recv.destroy()
			self.__fen_recv = None

	def __checkConnection(self):
		self.__update_fen(u'Verification de la connexion ...')
		if commandLine.ping('google.fr') == 0:
			self.__update_fen(u'    ok')
			self.__remotes.append(COMMANDS['remote'][self.__exe])
		else:
			self.__update_fen(u'    échec\n')

	def __getUSB(self):
		self.__update_fen(u'Recherche des clé usb ...')
		for key in CLEUSB:
			if self.__myOs == 'windows':
				getLetterCommand = commandLine.MyCommand('')
				getLetter = 'for /f %D in (\'wmic LogicalDisk get Caption^, VolumeName ^| find "{}"\') do %D'.format(key)
				driveLetter = getLetterCommand.run(options=getLetter)[1].strip('\r\n')[-2:]
				if driveLetter:
					path = driveLetter
				else:
					path = ''
			elif self.__myOs == 'ubuntu':
				path = os.path.join(os.sep, 'media', getpass.getuser(), key)
			path = os.path.join(path, 'songfinder')
			if os.path.isdir(path):
				self.__remotes.append(path)
				self.__usbFound.append(key)

		if self.__usbFound:
			self.__update_fen(u': ' + ' '.join(self.__usbFound))
		else:
			self.__update_fen('    aucune')

	def __getRemotes(self):
		self.__remotes = []
		self.__usbFound = []
		self.__checkConnection()
		self.__getUSB()
		if self.__remotes == []:
			return self.__showError(u'La connection a échoué. Verifiez votre connexion à internet.\n'
								u'"Aucune cle USB n\'as été trouvé"')
		return 0

	def receive(self, send=0):
		self.__gui()
		if self.__getRemotes() == 1:
			return 1
		os.chdir(self.__path)
		self.__update_fen(u'Réception des modifications ...')
		# ~ code, out, err = self.__scm.run(options=['pull', self.__remotes[0], '&&', 'update'])
		code, out, err = self.__scm.run(options=[COMMANDS['pullUpdate'][self.__exe], self.__remotes[0]])

		if out.find('no changes found') != -1 or out.find('aucun changement trouv') != -1:
			if send == 1:
				self.__update_fen(u"    ok")
			else:
				return self.__showInfo(u'Rien à recevoir')
		elif code == 0:
			if send == 1:
				self.__update_fen(u"    ok")
			else:
				return self.__showInfo(u'Les modifications ont bien été recus.')
		elif code == 255:
			return self.__showError(u'Erreur: Impossible de recupérer les modifications.\nErreur %s:\n%s'(str(code), '\n'.join([out,err])))
		elif tkMessageBox.askyesno(u'Erreur', u'Erreur: Impossible de recupérer les modifications.\n'
									u'Erreur %s:\n%s\nVoulez vous forcer la réception ? '
									u'Ceci effacera tout vos changements.'\
									%(str(code), '\n'.join([out,err])), parent = self.__fen_recv):
			code, out, err = self.__scm.run(options=[COMMANDS['reset'][self.__exe]])
			if code != 0:
				return self.__showError(u'Erreur: la reception forcé à échoué\nErreur %s:\n%s'%(str(code), '\n'.join([out,err])))

	def send(self, what='all'):
		if self.receive(1) == 1:
			return 1
		returns = []
		outs = []
		errs = []
		self.__update_fen(u'Validation des modifications ...')
		if what == 'all':
			code, out, err = self.__scm.run(options=[COMMANDS['addAll'][self.__exe], '&&', 'commit -m "%s"'%self.__commitName])
		elif what:
			if self.__exe =='hg':
				code, out, err = self.__scm.run(options=['commit -I %s -m "%s"'%(what, self.__commitName)])
			if self.__exe =='git':
				code, out, err = self.__scm.run(options=['add', what, '&&', 'commit -m "%s"'%self.__commitName])

		if out.find('nothing changed') != -1 or out.find('aucun changement') != -1 or out.find('nothing to commit') != -1:
			return self.__showInfo(u'Rien à envoyer')
		elif code != 0:
			self.__update_fen(u"    échec\n")
			return self.__showError(u'Erreur: la validation a échoué.\nErreur %s:\n%s'%(str(code), '\n'.join([out,err])))
		else:
			self.__update_fen(u'Envoi des modifications ...')
			for remote in self.__remotes:
				code, out, err = self.__scm.run(options=['push', remote])
				errs.append(err)
				returns.append(str(code))
			if returns == ['0']*len(self.__remotes):
				return self.__showInfo(u'Les modifications ont été envoyées sur:%s'%', '.join(self.__remotes))
			else:
				return self.__showError(u'Erreur %s:\n%s'%(' '.join(returns), '\n'.join(errs)))
