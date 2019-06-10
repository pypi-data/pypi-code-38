# -*- coding: utf-8 -*-
import Tkinter as tk
from songfinder import fonctions as fonc

def change_text(widget, text):
	widget.delete(1.0, tk.END)
	widget.insert(1.0, text) # TclError if text is None

def get_max_width(text, police):
	lignes = text.splitlines()
	lenghs = [police.measure(ligne) for ligne in lignes]
	return max(lenghs+[0])

def get_height(text, police):
	h_line = police.metrics("linespace")
	lignes = text.splitlines()
	return len(lignes)*h_line

def index_plus(index, plus):
	unpack = index.split('.')
	if len(unpack) == 2:
		[a, b] = unpack
		a, b = int(a), int(b)
		b = b+plus
		a, b = str(a), str(b)
		return '.'.join([a, b])
	else:
		return index

def update_fen(fen, message):
	fen.prog["text"] = fonc.safeUnicode(fen.prog["text"].replace('...', '')) \
						+ fonc.safeUnicode(message)
	fen.update()
	fen.geometry("%dx%d"%(fen.winfo_reqwidth(), fen.winfo_reqheight()))

def coloration(widget, couleur, chaine='', fin=''):
	# Bold make the tag_config method very slow
	# ~ relou = tkFont.nametofont("TkDefaultFont")
	# ~ police = tkFont.Font(family=relou["family"],size=relou["size"],weight="bold")
	# ~ police["weight"] = "bold"
	#coloration

	if not chaine:
		for tag in widget.tag_names():
			widget.tag_delete(tag)
		return 0

	pos = "1.0"
	pos = widget.search(chaine, pos, stopindex=tk.END, nocase=1)
	while pos: # Lets Some None pass
		if fin:
			pos_sui = index_plus( widget.search(fin, pos, stopindex=tk.END, nocase=1), 1 )
		else:
			pos_sui = index_plus(pos, len(chaine))
		widget.tag_add(chaine, pos, pos_sui) # TclError None
		pos = widget.search(chaine, pos_sui, stopindex=tk.END, nocase=1) # TclError ??
	# ~ widget.tag_config(chaine, foreground=couleur, font=police)
	widget.tag_config(chaine, foreground=couleur)
