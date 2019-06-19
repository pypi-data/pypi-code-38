# -*- coding: utf-8 -*-


import os
import Tkinter as tk
import ttk
import shutil
import filecmp
from songfinder import messages as tkMessageBox
from songfinder import messages as tkFileDialog

from songfinder import globalvar
from songfinder import classPaths
from songfinder import classSettings as settings
from songfinder import guiHelper
from songfinder import background

class ParamGen(object):
	def __init__(self, papa, **kwargs):
		fenetre = tk.Toplevel()
		fenetre.withdraw()
		fenetre.title('Paramètres généraux')
		fenetre.resizable(width=True, height=True)

		fenetre.grid()
		self.fenetre = fenetre
		self.papa = papa
		self.paths = classPaths.PATHS
		self.settingName = 'SettingsGen'

		self.screen_w = fenetre.winfo_screenwidth()
		self.screen_h = fenetre.winfo_screenheight()

		self.reset_button = tk.Button(fenetre, text='Reset', command=self.reset)
		self.ext_image = settings.GENSETTINGS.get('Extentions', 'image')
		self.FILETYPES_image = [(ext[1:].upper(), ext) for ext in self.ext_image] + [("All files", "*.*")]

		self.mot_data = tk.Label(fenetre, text = 'Base de données local: ')
		self.data_button = tk.Button(fenetre, text='Sauver/parcourir', command=self.change_rep)
		self.data_str = tk.Entry(fenetre, width=50)

		self.autoload = tk.IntVar()
		self.autoload_button = tk.Checkbutton(fenetre, text="Charger la dernière liste au démarrage de SongFinder.", \
											variable=self.autoload, \
									command = lambda intVar=self.autoload, parameter='autoload': \
												self.save_setting(intVar, parameter))
		self.sync = tk.IntVar()
		self.sync_button = tk.Checkbutton(fenetre, text="Synchroniser la base de données avec un dépôt en ligne.", \
											variable=self.sync, \
									command = lambda intVar=self.sync, parameter='sync': \
												self.save_setting(intVar, parameter))
		self.autoReceive = tk.IntVar()
		self.autoReceive_button = tk.Checkbutton(fenetre, text='Recevoir automatiquement les changements '
														'au démarrage de SongFinder.', \
											variable=self.autoReceive, \
									command = lambda intVar=self.autoReceive, parameter='autoreceive': \
												self.save_setting(intVar, parameter))
		self.highMem = tk.IntVar()
		self.highMem_button = tk.Checkbutton(fenetre, text='Autoriser SongFinder à utiliser beaucoup de mémoire.\n'
															'Cette option peut résoudre certains problèmes de performances.', \
											variable=self.highMem, \
									command = lambda intVar=self.highMem, parameter='highmemusage': \
												self.save_setting(intVar, parameter))

		self.autoload_button.grid(row=0, column=0, columnspan=5, sticky='w' )
		self.sync_button.grid(row=1, column=0, columnspan=5, sticky='w' )
		self.autoReceive_button.grid(row=2, column=0, columnspan=5, sticky='w' )
		self.highMem_button.grid(row=3, column=0, columnspan=5, sticky='w' )

		self.mot_data.grid(row=4, column=0, columnspan=2, sticky='w' )
		self.data_str.grid(row=4, column=2, columnspan=7, sticky='w' )
		self.data_button.grid(row=4, column=9, columnspan=1, sticky='w' )
		self.reset_button.grid(row=5, column=0, columnspan=2)

		self.maj()

		fenetre.update()
		fenetre.geometry("%dx%d"%(fenetre.winfo_reqwidth(), fenetre.winfo_reqheight()))
		fenetre.deiconify()
		guiHelper.upFront(fenetre)

	def maj(self):
		if settings.GENSETTINGS.get('Parameters', 'autoload') == 'oui':
			self.autoload_button.select()
		if settings.GENSETTINGS.get('Parameters', 'sync') == 'oui':
			self.sync_button.select()
		if settings.GENSETTINGS.get('Parameters', 'autoreceive') == 'oui':
			self.autoReceive_button.select()
		if settings.GENSETTINGS.get('Parameters', 'highmemusage') == 'oui':
			self.highMem_button.select()
		self.data_str.delete(0, tk.END)
		self.data_str.insert(0, self.paths.root)

	def change_rep(self):
		chemin = self.data_str.get()
		if chemin == self.paths.root:
			self.paths.save( tkFileDialog.askdirectory(parent = self.fenetre) )
		else:
			self.paths.save(chemin)
		self.maj()
		self.papa.updateData()

	def save_setting(self, settingIntVar, parameter):
		if settingIntVar.get():
			value = 'oui'
		else:
			value = 'non'
		settings.GENSETTINGS.set('Parameters', parameter, value)
		if parameter == 'highmemusage':
			if value == 'oui':
				background.BACKGROUNDS.resizeCache('high')
			elif value == 'non':
				background.BACKGROUNDS.resizeCache('low')
		if parameter == 'sync' and value =='oui':
			classPaths.PATHS.sync()
		self.maj()

	def reset(self):
		if tkMessageBox.askyesno(u'Defaut', 'Etes vous sur de remettre les paramètres par defaut ?'):
			globalvar.sett.create()
			self.maj()

	def close(self):
		self.fenetre.destroy()


class ParamPres(object):
	def __init__(self, papa, **kwargs):
		fenetre = tk.Toplevel()
		fenetre.withdraw()
		fenetre.title('Paramètres de présentation')
		fenetre.resizable(width=True, height=True)
		fenetre.grid()
		self.fenetre = fenetre
		self.papa = papa
		self.paths = classPaths.PATHS
		self.petit_mot_profil = tk.Label(fenetre, text = 'Profil: ')
		self.petit_mot_profil.grid(row=0, column=0, columnspan=3, sticky='w')

		self.settingName = 'SettingsPres'

		self.screen_w = fenetre.winfo_screenwidth()
		self.screen_h = fenetre.winfo_screenheight()

		self.fenetre_profil = None
		self.profil = ''
		self.liste_profil = []

		self.profil_selection = tk.StringVar()
		self.combobox_profil = ttk.Combobox(fenetre, textvariable = self.profil_selection, \
												values = self.liste_profil, state = 'readonly')
		self.combobox_profil.grid(row=0, column=3, columnspan=5)
		self.get_profil_liste()
		self.start_profil()

		self.etype = 'song'

		self.petit_mot_type = tk.Label(fenetre, text = 'Paramètres pour le type: ')
		self.petit_mot_type.grid(row=1, column=0, columnspan=3, sticky='w')

		self.liste_etype = settings.GENSETTINGS.get('Syntax', 'element_type')

		self.etype_selection	= tk.StringVar()
		self.combobox_etype	= ttk.Combobox(fenetre, textvariable = self.etype_selection, \
						values = self.liste_etype, state = 'readonly')
		self.combobox_etype.grid(row=1, column=3, columnspan=5)
		self.combobox_etype.set('song')

		self.ext_image = settings.GENSETTINGS.get('Extentions', 'image')
		self.FILETYPES_image = [(ext[1:].upper(), ext) for ext in self.ext_image] + [("All files", "*.*")]

		self.mot_background = tk.Label(fenetre, text = 'Arrière plan: ')
		self.background_button = tk.Button(fenetre, text='Sauver/parcourir', command=self.change_background)
		self.background_str = tk.Entry(fenetre, width=60)

		self.add_profil_button = tk.Button(fenetre, text='Sauvegarder le profil', command=self.fenetre_creation_profil)

		self.dictParam = {"Numéroter les diapositives.":"Numerote_diapo",\
							"Afficher le titre/commentaire.":"Print_title",\
							"Enlever les majuscules aux pronoms.":"Clean_majuscule",\
							"Mettre des majuscules en début de lignes.":"Majuscule",\
							'Verifier les "bis".':"Check_bis",\
							"Passer à la ligne en fonction de la ponctuation.":"Saut_ligne",\
							"Passer à la lignes même sans ponctuation.":"Saut_ligne_force",\
							"Vérifier les espaces autour des ponctuations.":"Ponctuation",\
							"Numeroter les éléments ne contenant qu'une seul diapo.":"oneslide",\
							}

		self.var_justification = tk.IntVar()
		self.justification_gauche = tk.Radiobutton(fenetre, text="Justifier à gauche.", \
												variable=self.var_justification, value=0, command=self.save)
		self.justification_centre = tk.Radiobutton(fenetre, text="Justifier au centre.", \
												variable=self.var_justification, value=1, command=self.save)
		self.justification_droite = tk.Radiobutton(fenetre, text="Justifier à droite.", \
												variable=self.var_justification, value=2, command=self.save)
		self.liste_justification = [self.justification_gauche, self.justification_centre, self.justification_droite]

		self.liste_mep = ['left', 'center', 'right']

		self.var_size = tk.StringVar()
		self.mot_size = tk.Label(fenetre, text = 'Taille police: ')
		self.size_entry = tk.Entry(fenetre, textvariable=self.var_size, width=5)
		self.var_max_car = tk.StringVar()
		self.mot_max_car = tk.Label(fenetre, text = 'Taille des lignes: ')
		self.max_car_entry = tk.Entry(fenetre, textvariable=self.var_max_car, width=5)
		self.save_sizes_button = tk.Button(fenetre, text='Sauver', command=self.save_sizes)

		self.combobox_etype.bind("<<ComboboxSelected>>", self.select_etype)
		self.combobox_profil.bind("<<ComboboxSelected>>", self.select_profil)

		for i, just in enumerate(self.liste_justification):
			just.bind("<ButtonRelease-1>", self.save)

		nb_boutton = len(self.dictParam)
		nb_justification = len(self.liste_justification)

		self.mot_background.grid(row=nb_boutton+5+nb_justification, column=0, columnspan=2, sticky='w' )
		self.background_str.grid(row=nb_boutton+5+nb_justification, column=2, columnspan=7, sticky='w' )
		self.background_button.grid(row=nb_boutton+5+nb_justification, column=9, columnspan=1, sticky='w' )

		self.add_profil_button.grid(row=nb_boutton+12+nb_justification, column=0, columnspan=10, sticky='ew' )

		column_width = 5
		nb_row = (nb_boutton+1)//2
		self.dictValeurs = dict()
		self.dictButton = dict()
		for i, (param, item) in enumerate(self.dictParam.items()):
			var = tk.IntVar()
			button = tk.Checkbutton(fenetre, text=param, variable=var, command=self.save)
			self.dictValeurs[param] = var
			self.dictButton[item] = button
			column_num = i//nb_row * (column_width + 1)
			button.grid(row=i%nb_row+3, column=column_num, columnspan=column_width, sticky='w' )

		for i, just in enumerate(self.liste_justification):
			just.grid(row=nb_row+3+i, column=0, columnspan=5, sticky='w' )

		self.mot_size.grid(row=nb_boutton+8+nb_justification, column=0, columnspan=2, sticky='w' )
		self.size_entry.grid(row=nb_boutton+8+nb_justification, column=2, columnspan=1, sticky='w' )
		self.mot_max_car.grid(row=nb_boutton+8+nb_justification+1, column=0, columnspan=2, sticky='w' )
		self.max_car_entry.grid(row=nb_boutton+8+nb_justification+1, column=2, columnspan=1, sticky='w' )
		self.save_sizes_button.grid(row=nb_boutton+8+nb_justification, column=3, columnspan=1, rowspan=2, sticky='w' )

		self.separator0 = ttk.Separator(fenetre, orient="horizontal")
		self.separator1 = ttk.Separator(fenetre, orient="horizontal")
		self.separator2 = ttk.Separator(fenetre, orient="horizontal")
		self.separator3 = ttk.Separator(fenetre, orient="vertical")
		self.separator5 = ttk.Separator(fenetre, orient="horizontal")

		self.separator0.grid(row=2, column=0, columnspan=10, sticky='ew' )
		self.separator1.grid(row=nb_boutton+4+nb_justification, column=0, columnspan=10, sticky='ew' )
		self.separator2.grid(row=nb_boutton+7+nb_justification, column=0, columnspan=10, sticky='ew' )
		self.separator3.grid(row=2, column=5, rowspan=nb_boutton+4+nb_justification-2, sticky='ns' )
		self.separator5.grid(row=nb_boutton+10+nb_justification, column=0, columnspan=10, sticky='ew' )

		self.maj()

		fenetre.update()
		fenetre.geometry("%dx%d"%(fenetre.winfo_reqwidth(), fenetre.winfo_reqheight()))
		fenetre.deiconify()
		guiHelper.upFront(fenetre)

	def maj(self):
		for param in self.dictParam.values():
			if settings.PRESSETTINGS.get(self.etype, param) == 'oui':
				self.dictButton[param].select()
			else:
				self.dictButton[param].deselect()
		if self.etype == 'song':
			for button in self.dictButton.values():
				button.config(state=tk.NORMAL)
			for i, just in enumerate(self.liste_justification):
				just.config(state=tk.NORMAL)

		elif self.etype == 'verse':
			for button in self.dictButton.values():
				button.config(state=tk.NORMAL)
			for i, just in enumerate(self.liste_justification):
				just.config(state=tk.NORMAL)
			for param in ["Check_bis", "Clean_majuscule"]:
				self.dictButton[param].deselect()
				self.dictButton[param].config(state=tk.DISABLED)

		elif self.etype == 'media':
			for button in self.dictButton.values():
				button.deselect()
				button.config(state=tk.DISABLED)
			for param in ["Print_title", "Ponctuation"]:
				self.dictButton[param].config(state=tk.NORMAL)
			for i, just in enumerate(self.liste_justification):
				just.config(state=tk.NORMAL)

		elif self.etype == 'image':
			for button in self.dictButton.values():
				button.deselect()
				button.config(state=tk.DISABLED)
			for param in ["Print_title", "Ponctuation"]:
				self.dictButton[param].config(state=tk.NORMAL)
			for i, just in enumerate(self.liste_justification):
				just.config(state=tk.NORMAL)

		elif self.etype == 'empty':
			for button in self.dictButton.values():
				button.deselect()
				button.config(state=tk.DISABLED)
			for i, just in enumerate(self.liste_justification):
				just.config(state=tk.DISABLED)

		elif self.etype == 'preach':
			for button in self.dictButton.values():
				button.config(state=tk.NORMAL)
			for param in ["Check_bis", "Clean_majuscule", "oneslide"]:
				self.dictButton[param].deselect()
				self.dictButton[param].config(state=tk.DISABLED)

		param = settings.PRESSETTINGS.get(self.etype, 'Justification')
		self.var_justification.set(self.liste_mep.index(param))

		self.background = settings.PRESSETTINGS.get(self.etype, 'Background')
		self.background_str.delete(0, tk.END)
		self.background_str.insert(0, self.background)

		self.var_size.set(settings.PRESSETTINGS.get('Presentation_Parameters', 'size'))
		self.var_max_car.set(settings.PRESSETTINGS.get('Presentation_Parameters', 'size_line'))

	def save(self, event=0, *args):
		for param, valeur in self.dictValeurs.items():
			if valeur.get():
				str_valeur = 'oui'
			else:
				str_valeur = 'non'
			settings.PRESSETTINGS.set(self.etype, self.dictParam[param], str_valeur)

		num = self.liste_mep[self.var_justification.get()]
		settings.PRESSETTINGS.set(self.etype, 'Justification', str(num))

	def save_sizes(self):
		size = self.var_size.get()
		max_car = self.var_max_car.get()
		if settings.is_number(size):
			settings.PRESSETTINGS.set('Presentation_Parameters', 'size', str(int(round(float(size)))))
		if settings.is_number(max_car):
			settings.PRESSETTINGS.set('Presentation_Parameters', 'size_line', str(int(round(float(max_car)))))

		self.var_size.set(settings.PRESSETTINGS.get('Presentation_Parameters', 'size'))
		self.var_max_car.set(settings.PRESSETTINGS.get('Presentation_Parameters', 'size_line'))

	def change_background(self):
		chemin = self.background_str.get()
		if chemin == self.background:
			chemin = tkFileDialog.askopenfilename(filetypes=self.FILETYPES_image, parent = self.fenetre)
			if chemin and os.path.isfile(chemin):
				self.background = chemin
			elif chemin:
				tkMessageBox.showerror(u'Erreur', u'Le fichier est introuvable', parent = self.fenetre)
		else:
			if chemin and os.path.isfile(chemin):
				self.background = chemin
			elif chemin:
				tkMessageBox.showerror(u'Erreur', u'Le fichier est introuvable', parent = self.fenetre)
		settings.PRESSETTINGS.set(self.etype, 'Background', self.background)
		self.maj()

	def select_etype(self, event):
		if self.combobox_etype.get():
			self.etype = self.combobox_etype.get()
			self.maj()

	def select_profil(self, event):
		if self.combobox_profil.get():
			self.profil = self.combobox_profil.get()
			shutil.copy( os.path.join(globalvar.settingsPath, self.settingName + '_' + self.profil) , os.path.join(globalvar.settingsPath, self.settingName) )
			globalvar.sett.read()
			self.maj()

	def start_profil(self):
		for filename in os.listdir(globalvar.settingsPath):
			if filename.find(self.settingName + '_') != -1 and \
				filecmp.cmp( os.path.join(globalvar.settingsPath, filename) , os.path.join(globalvar.settingsPath, self.settingName) ):
				self.profil = filename[filename.find('_')+1:]
				self.combobox_profil.set(self.profil)

	def fenetre_creation_profil(self):
		if not self.fenetre_profil	:
			self.fenetre_profil = tk.Toplevel()
			self.fenetre_profil.wm_attributes("-topmost", 1)
			self.fenetre_profil.title("Nouveau profil")
			self.fenetre_profil.geometry("%dx%d+%d+%d"%(170, 80, self.screen_w//2-100, self.screen_h//4-25))

			self.text_set=tk.Label(fenetre.fenetre_profil, text="Nom du nouveau profil")
			self.nom_profil = tk.Entry(fenetre.fenetre_profil, width=20)
			self.bouton_set = tk.Button(fenetre.fenetre_profil, text='Créer', command=self.cree_profil)

			self.text_set.grid(row=0, column=0)
			self.nom_profil.grid(row=1, column=0)
			self.bouton_set.grid(row=2, column=0)

			self.fenetre_profil.update()
			self.nom_profil.focus_set()

	def cree_profil(self):
		if self.nom_profil.get():
			self.profil = self.nom_profil.get()
			profil = os.path.join(globalvar.settingsPath, self.settingName + '_' + self.profil)
			if not os.path.isfile(profil) or \
								tkMessageBox.askyesno(u'Conflit', 'Le fichier %s existe déjà, voulez-vous le remplacer ?'%profil, \
								parent = self.fenetre_profil):
				globalvar.sett.write()
				shutil.copy( os.path.join(globalvar.settingsPath, self.settingName), profil)
				self.fenetre_profil.destroy()
				self.fenetre_profil = None
				if os.path.isfile(profil):
					tkMessageBox.showinfo(u'Confirmation', u'Le fichier %s a été écrit'%profil, parent = self.fenetre)
					self.combobox_profil.set(self.profil)
			else:
				tkMessageBox.showerror(u'Erreur', u'Le fichier %s n\'a pas été crée'%profil, parent = self.fenetre)
		self.get_profil_liste()

	def get_profil_liste(self):
		# Creation de la liste de profil
		self.liste_profil = []
		for root, dirs, files in os.walk(globalvar.settingsPath):
			for fichier in files:
				if fichier.find('Settings_') != -1:
					self.liste_profil.append(fichier[9:])
			break
		self.combobox_profil['values'] = self.liste_profil

	def close(self):
		self.fenetre.destroy()
