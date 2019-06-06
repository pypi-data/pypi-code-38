# -*- coding: utf-8 -*-
#cython: language_level=2

import os
import importlib
import traceback

from songfinder import globalvar

try:
	fileName = os.path.splitext( os.path.split(__file__)[1] )[0]
	module = importlib.import_module('lib.%s_%s'%(fileName, globalvar.arch))
	print("Using compiled version %s module"%fileName)
	globals().update(
		{n: getattr(module, n) for n in module.__all__} if hasattr(module, '__all__')
		else
		{k: v for (k, v) in module.__dict__.items() if not k.startswith('_')
	})
except (ImportError, NameError):
	# print(traceback.format_exc())

	from songfinder import fonctions as fonc
	from songfinder import classPaths
	from songfinder import globalvar
	from songfinder import creplace
	from songfinder import classSettings as settings

	def clean_line(text):
		for i in range(5):
			text = text.replace('\n\n','\n')
			text = text.replace('\n \n','\n')
		newline = settings.GENSETTINGS.get('Syntax', 'newline')
		text = text.replace(newline,'')
		return text

	def numerote(text, numero, nombre, etype)	:
		if nombre > 1 or settings.PRESSETTINGS.get(etype, 'oneslide') == 'oui':
			if settings.PRESSETTINGS.get(etype, 'Numerote_diapo') == 'oui':
				if numero:
					text = '(%s/%s)%s'%(str(numero), str(nombre), text)
		return text

	def print_title(text, title, numero, etype):
		if settings.PRESSETTINGS.get(etype, 'Print_title') == 'oui':
			if numero == 1:
				text = '%s\n%s'%(title.upper(), text)
		return text

	def check_bis(text, etype):
		if settings.PRESSETTINGS.get(etype, 'Check_bis') == 'oui':
			text = text.replace('(x2)', '(bis)')\
					.replace('(X2)', '(bis)')\
					.replace(u'(× 2)', '(bis)')\
					.replace('(* 2)', '(bis)')\
					.replace('(BIS)', '(bis)')\
					.replace(' (Bis)', ' (bis)')\
					.replace('\n (bis)', '\n (Bis)')\
					.replace('\n(bis)', '\n(Bis)')\
					.replace('\n(ter)', '\n(Ter)')
		return text

	def clean_maj(text, etype):
		# Must be before maj at starting lines
		# Must be after check of ponctuation but maybe not
		if settings.PRESSETTINGS.get(etype, 'Clean_majuscule') == 'oui':
			text = text + ' '
			prePonct = ["'", " ", "\n"]
			postPonct = [",", ".", " ", "\n"]
			list_pronoms = ['Oint','Sa', 'Ta', 'Il', 'Tu', 'Te', 'Toi', \
							'Son', 'Ses', 'Tes', 'Ton', 'Nom', 'Lui', \
							'Roi', 'Celui', 'Agneau', 'Fils']
			for pronom in list_pronoms:
				for ponct1 in prePonct:
					for ponct2 in postPonct:
						text = text.replace(ponct1 + pronom + ponct2, ponct1 + pronom.lower() + ponct2)
			text = text.strip(' ')
		return text

	def majuscule(text, etype):
		if settings.PRESSETTINGS.get(etype, 'Majuscule') == 'oui':
			lignes = text.splitlines()
			lignes = [ligne.strip(' ') for ligne in lignes if ligne.strip(' ') != '']
			new_lignes = []
			for ligne in lignes:
				ligne = fonc.upper_first(ligne)
				if ligne[0] == '"' or ligne[0] == "'":
					ligne = ligne[0] + fonc.upper_first(ligne[1:])
				new_lignes.append(ligne)

			text = "\n".join(new_lignes)
		return text

	def enleve_ponctuation(text):
		return text.replace('.',' ').replace(',',' ').replace(';',' ').replace(':',' ')\
				.replace('!',' ').replace("'",' ').replace('?',' ').replace('  ',' ')\
				.replace('_',' ').replace('-',' ')

	def verifie_ponctuation(text, etype):
		#verification ponctuation
		if settings.PRESSETTINGS.get(etype, 'Ponctuation') == 'oui':
			ponctuations0 = [":"]
			for car in ponctuations0:
				text = text.replace(car, " %s "%car).replace("  ", " ")
			ponctuations1 = [";", "!", "?"]
			for car in ponctuations1:
				text = text.replace(car, " %s "%car).replace("  ", " ").replace('%s "'%car, '%s"'%car)
			ponctuations2 = [".", ","]
			for car in ponctuations2:
				text = text.replace(car, "%s "%car).replace("  ", " ").replace('%s "'%car, '%s"'%car)
			text = text.replace(' \n', '\n')
			for i in range(5):
				text = text.replace('. .', '..')
			for ponct in ponctuations0 + ponctuations1 + ponctuations2:
				text = text.replace('%s )'%ponct, '%s)'%ponct)
		return text

	def verifie_ponctuation_maj(text, etype):
		# Majuscule après les points ? et !
		if settings.PRESSETTINGS.get(etype, 'Ponctuation') == 'oui':
			ponctuations_maj = ["!", "?", "."]
			for ponct in ponctuations_maj:
				deb = 0
				while text.find(ponct, deb) != -1:
					index = text.find(ponct, deb)
					if len(text) > index+3:
						text = text[:index+2] + text[index+2].upper() + text[index+3:]
					deb = index+1
		return text

	def genere_chant(title, nom_set_chants_dispo):
		if not ((title[:3] == 'JEM' or title[:3] == 'SUP' )and title[3:6].isdigit()):
			max_sup = 0
			for chant in nom_set_chants_dispo:
				if chant[0:3] == 'SUP':
					if max_sup < int(chant[3:6]):
						max_sup = int(chant[3:6])
			title = 'SUP' + str(max_sup+1) + ' ' + title

		chemin_chants = classPaths.Paths().songs
		chemin = os.path.join(chemin_chants, fonc.enleve_accents(title)\
								+ settings.GENSETTINGS.get('Extentions', 'chant')[0])
		return chemin, title

	def saut_ligne(text, max_car, etype, force=None):
		liste_sep = ['\\newline', '.', '!', '?', ' et ', ' Et ', ';',  ':', ',']
		do_not = ['(bis)', '(Bis)']
		new_text = text
		if settings.PRESSETTINGS.get(etype, 'Saut_ligne') == 'oui' or force == 'force':
			for i in range(5):
				lignes = new_text.splitlines()
				new_text = ''
				for ligne in lignes:
					trouve = -1

					if len(ligne) > max_car and ligne.find('\\ac') == -1:
						ind = len(ligne)*2/5
						for sep in liste_sep:
							trouve = ligne.find(sep, ind, -1)
							if trouve > -1:
								if sep in [' et ', ' Et ']:
									plus = 0
								else:
									plus = len(sep)
								if ligne[trouve+len(sep)+1: trouve+len(sep)+6] not in do_not:
									new_text = new_text + ligne[:trouve+plus] + '\n'
									new_text = new_text + ligne[trouve+plus:] + '\n'
									break
					if trouve == -1:
						new_text = new_text + ligne + '\n'
			if settings.PRESSETTINGS.get(etype, 'Saut_ligne_force') == 'oui' or force == 'force':
				lignes = new_text.splitlines()
				new_text = ''
				for ligne in lignes:
					trouve = -1
					longueur = len(ligne)
					if longueur > max_car:
						div = (longueur + max_car - 1)/max_car
						new_longueur = longueur/div
						trouve = ligne.find(' ', new_longueur, -1)
						new_text = new_text + ' ' + ligne[:trouve+1] + '\n'
						if div > 2:
							for i in range(div-2):
								trouve1 = ligne.find(' ', (i+1)*new_longueur, -1)
								trouve = ligne.find(' ', (i+2)*new_longueur, -1)
								new_text = new_text + ' ' + ligne[trouve1+1:trouve+1] + '\n'
						new_text = new_text + ' ' + ligne[trouve+1:] + '\n'

					if trouve == -1:
						new_text = new_text + ligne + '\n'
			for sep in set(liste_sep) - set([' et ', ' Et ']):
				new_text = new_text.replace('\n%s'%sep, '%s\n'%sep)
				new_text = new_text.replace('\n %s'%sep, '%s\n '%sep)
				new_text = new_text.replace('%s\n"'%sep, '%s"\n'%sep)
				new_text = new_text.replace('%s\n)'%sep, '%s)\n'%sep)
				new_text = new_text.replace('%s\n'''%sep, '%s''\n'%sep)

		return new_text

	def nettoyage(text):
		newslide = settings.GENSETTINGS.get('Syntax', 'newslide')
		newline = settings.GENSETTINGS.get('Syntax', 'newline')

		text = text.replace(". .", "..")\
					.replace(". .", "..")\
					.replace(u"\u2018", "'")\
					.replace(u"\u2019", "'")\
					.replace(u"\u0020"," ")\
					.replace(u"\u00A0"," ")

		text = creplace.cleanupChar(text.encode('utf-8'))
		text = creplace.cleanupSpace(text)

		for i in range(2):
			text = text.strip(" _\n")
			text = fonc.strip_perso(text, newline)
		for newslideSyntax in newslide:
			text = text.replace("\n" + newslideSyntax, "\n\n" + newslideSyntax)

		return text.decode('utf-8')

	def getListStypePlus(listStype):
		# Trouve les suite de type de diapo
		i = 0
		previous = ''
		listStypePlus = [] # (type, list des numero)
		tmp = []
		ignore = settings.LATEXSETTINGS.get('Latex_Parameters', 'ignore')
		for k,stype in enumerate(listStype):
			tmp.append(k-1)
			if stype == previous:
				i = i + 1
			else:
				if previous != '\si' or ignore == 'non':
					listStypePlus.append((previous, tmp))
				i = 0
				tmp = []
			previous = stype

		tmp.append(len(listStype)-1)
		if previous != '\si' or ignore == 'non':
			listStypePlus.append((previous, tmp))
		del listStypePlus[0]
		return listStypePlus

	# ~ def getPlusIndex(listStypePlus, index):
		# ~ for plusIndex, (Stype, numList) in enumerate(listStypePlus):
			# ~ if index in numList:
				# ~ return plusIndex

	def getPlusNum(listStypePlus, index):
		for plusIndex, (Stype, numList) in enumerate(listStypePlus):
			if index in numList:
				return len(numList)

	def getIndexes(liste, elem):
		return [i for i, j in enumerate(liste) if j == elem]
