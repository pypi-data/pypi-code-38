# -*- coding: utf-8 -*-

import Tkinter as tk
import os
from songfinder import messages as tkMessageBox
import subprocess
import getpass
import tkSimpleDialog
import shutil
import warnings
import traceback
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
from songfinder import __version__

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

class AddRepo(object): # TODO integrate to repo class
	def __init__(self, paths, exe, interface, **kwargs):
		fenetre = tk.Toplevel()
		fenetre.withdraw()
		fenetre.title("Clonage d'un dépôt")
		fenetre.update()
		fenetre.grid()
		self.paths = paths
		self.fenetre = fenetre
		self.interface = interface
		self.__exe = exe
		self.__scm = commandLine.MyCommand(self.__exe)
		self.__scm.checkCommand()

		self.prog = tk.Label(fenetre, text="", justify='left')
		self.ok_button = tk.Button(fenetre, text='Cloner', command=self._cloneRepo)
		self.cancel_button = tk.Button(fenetre, text='Annuler', command=self._closeAddRepo)
		self.remote = tk.Entry(fenetre, width=60)
		self.user = tk.Entry(fenetre, width=30)
		self.password = tk.Entry(fenetre, width=30)
		self.param = [self.remote, self.user, self.password]
		labelsStr = ["Chemin", "Utilisateur", "Mot de passe"]
		self.labels = []
		for i, param in enumerate(self.param):
			label = tk.Label(fenetre, text=labelsStr[i], justify='left')
			label.grid(row=i, column=0, columnspan=5, sticky='w' )
			self.labels.append(label)
			param.grid(row=i, column=5, columnspan=20, sticky='w' )
		self.ok_button.grid(row=len(self.param), column=0, columnspan=1, sticky='w' )
		self.cancel_button.grid(row=len(self.param), column=1, columnspan=1, sticky='w' )

		fenetre.bind_all("<KeyRelease-Return>", self._cloneRepo)

		fenetre.update()
		fenetre.geometry("%dx%d"%(fenetre.winfo_reqwidth(), fenetre.winfo_reqheight()))
		fenetre.deiconify()
		fenetre.focus_set()
		guiHelper.upFront(fenetre)

	def _closeAddRepo(self):
		if self.fenetre:
			self.fenetre.destroy()
			self.fenetre = None

	def _cloneRepo(self, event=0):
		guiHelper.update_fen(self.fenetre, 'Récupération des informations ...')
		repo = self.remote.get()
		name = self.user.get()
		mdp = self.password.get()
		if not (repo and name and mdp):
			guiHelper.update_fen(self.fenetre, "    échec\n")
			tkMessageBox.showerror('Erreur', 'Erreur: les informations sont incomplètes')
		else:
			self.prog.grid(sticky='w')
			guiHelper.update_fen(self.fenetre, "    ok\nVerification de la connexion ...")
			if commandLine.ping('google.fr') == 0:
				guiHelper.update_fen(self.fenetre, "    ok\n")
			else:
				guiHelper.update_fen(self.fenetre, "    échec\n")
				#https://epef@bitbucket.org/epef/data

			if repo:
				guiHelper.update_fen(self.fenetre, "Clonage du dépôt (ceci peut prendre quelques minutes) ...")
				shutil.rmtree(self.paths.root)
				os.makedirs(self.paths.root)
				os.chdir(self.paths.root)
				arrobase = repo.find('@')
				user = repo[repo.find('://')+3:arrobase]
				prefix = repo[arrobase+1:]
				fullrepo = repo[:arrobase] + ':' + mdp + repo[arrobase:]
				code, out, err = self.__scm.run( options=['clone%s'%COMMANDS['insecure'][self.__exe], fullrepo, '.'] )
				try:
					self._makeHidden(os.path.join(self.paths.root, '.hg'))
					self._makeHidden(os.path.join(self.paths.root, '.hgignore'))
					self._makeHidden(os.path.join(self.paths.root, 'bitbucket-pipelines.yml'))
				except Exception:
					warnings.warn('Failed to make file hidden\n:%s'%traceback.format_exc())
			if code != 0:
				guiHelper.update_fen(self.fenetre, "    échec\n")
				tkMessageBox.showerror('Erreur', 'Erreur: le clonage du dépôt à échoué\nErreur %d:\n%s'%(code, err))
				self._closeAddRepo()
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
				guiHelper.update_fen(self.fenetre, "    ok\n")
				tkMessageBox.showinfo('Confirmation', 'Le dépôt à été cloné.')
				if hasattr(self.interface, 'updateData'):
					self.interface.updateData()
				self._closeAddRepo()

			os.chdir(globalvar.chemin_root)

	def _makeHidden(self, path):
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
		self.__commitName = 'Song Finder v%s'%__version__
		self.__showGui = showGui

	def __gui(self):
		if self.__showGui:
			self.__fen_recv = tk.Toplevel(self.__papa)
			self.__fen_recv.withdraw()
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
			self.__fen_recv.deiconify()
			guiHelper.upFront(self.__fen_recv)
		else:
			self.__fen_recv = None

	def __update_fen(self, message):
		if self.__showGui:
			message = fonc.safeUnicode(message)
			newText = fonc.safeUnicode(self.__fen_recv.prog["text"].replace('...', ''))
			exceList = set(self.__usbFound) | {u'ok', 'échec', 'aucune'}
			if not set(message.split(' ')) & exceList:
				newText += '\n'
			newText += message
			newText = fonc.strip_perso(newText.replace('\n\n','\n'), '\n')
			self.__fen_recv.prog["text"] = newText
			self.__fen_recv.update()
			self.__fen_recv.geometry("%dx%d"%(self.__fen_recv.winfo_reqwidth(), \
											self.__fen_recv.winfo_reqheight()))

	def __showError(self, message):
		self.__update_fen('    échec')
		tkMessageBox.showerror('Erreur', message)
		self.__closeAddRepo()
		return 1

	def __showInfo(self, message):
		self.__update_fen('    ok')
		if self.__showGui:
			tkMessageBox.showinfo('Confirmation', message)
		self.__closeAddRepo()
		return 0

	def __closeAddRepo(self):
		os.chdir(globalvar.chemin_root)
		if self.__showGui:
			self.__fen_recv.destroy()
			self.__fen_recv = None

	def __checkConnection(self):
		self.__update_fen('Vérification de la connexion ...')
		if commandLine.ping('google.fr') == 0:
			self.__update_fen('    ok')
			self.__remotes.append(COMMANDS['remote'][self.__exe])
		else:
			self.__update_fen('    échec\n')

	def __getUSB(self):
		self.__update_fen('Recherche des clé usb ...')
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
			if path:
				path = os.path.join(path, 'songfinder')
			if os.path.isdir(path):
				self.__remotes.append(path)
				self.__usbFound.append(key)

		if self.__usbFound:
			self.__update_fen(': ' + ' '.join(self.__usbFound))
		else:
			self.__update_fen('    aucune')

	def __getRemotes(self):
		self.__remotes = []
		self.__usbFound = []
		self.__checkConnection()
		self.__getUSB()
		if self.__remotes == []:
			return self.__showError('La connection a échoué. Verifiez votre connexion à internet.\n'
								'Aucune clé USB n\'as été trouvé')
		return 0

	def receive(self, send=0):
		self.__gui()
		if self.__getRemotes() == 1:
			return 1
		os.chdir(self.__path)
		self.__update_fen('Réception des modifications ...')
		# ~ code, out, err = self.__scm.run(options=['pull', self.__remotes[0], '&&', 'update'])
		code, out, err = self.__scm.run(options=[COMMANDS['pullUpdate'][self.__exe], self.__remotes[0]])

		if out.find('no changes found') != -1 or out.find('aucun changement trouv') != -1:
			if send == 1:
				self.__update_fen("    ok")
			else:
				return self.__showInfo('Rien à recevoir')
		elif code == 0:
			if send == 1:
				self.__update_fen("    ok")
			else:
				return self.__showInfo('Les modifications ont bien été recus.')
		elif code == 255:
			return self.__showError('Erreur: Impossible de recupérer les modifications.\nErreur %d:\n%s'%(code, '\n'.join([out,err])))
		elif tkMessageBox.askyesno('Erreur', 'Erreur: Impossible de recupérer les modifications.\n'
									'Ceci peut être du au fait que vos modifications sont incompatibles '
									'avec les modifications faites par un autre utilisateur.'
									'Pour résoudre ce conflit vous devez annuler vos modifications '
									'et receptionner les modifications faites par l''autre utilisateurs.'
									'Voulez vous annuler vos modifications (ceci effacera tout vos changements.) ?'\
									%(code, '\n'.join([out,err]))):
			code, out, err = self.__scm.run(options=[COMMANDS['reset'][self.__exe]])
			if code != 0:
				return self.__showError('Erreur: la reception forcé à échoué\nErreur %d:\n%s'%(code, '\n'.join([out,err])))

	def send(self, what='all'):
		if self.receive(1) == 1:
			return 1
		returns = []
		outs = []
		errs = []
		self.__update_fen('Validation des modifications ...')
		if what == 'all':
			code, out, err = self.__scm.run(options=[COMMANDS['addAll'][self.__exe], '&&', 'commit -m "%s"'%self.__commitName])
		elif what:
			if self.__exe =='hg':
				code, out, err = self.__scm.run(options=['commit -I %s -m "%s"'%(what, self.__commitName)])
			if self.__exe =='git':
				code, out, err = self.__scm.run(options=['add', what, '&&', 'commit -m "%s"'%self.__commitName])

		if out.find('nothing changed') != -1 or out.find('aucun changement') != -1 or out.find('nothing to commit') != -1:
			return self.__showInfo('Rien à envoyer')
		elif code != 0:
			self.__update_fen("    échec\n")
			return self.__showError('Erreur: la validation a échoué.\nErreur %d:\n%s'%(code, '\n'.join([out,err])))
		else:
			self.__update_fen('Envoi des modifications ...')
			for remote in self.__remotes:
				code, out, err = self.__scm.run(options=['push', remote])
				errs.append(err)
				returns.append(str(code))
			if returns == ['0']*len(self.__remotes):
				return self.__showInfo('Les modifications ont été envoyées sur:%s'%', '.join(self.__remotes))
			else:
				return self.__showError('Erreur %s:\n%s'%(' '.join(returns), '\n'.join(errs)))
