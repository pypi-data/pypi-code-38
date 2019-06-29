try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk
import time
import os
from PIL import Image, ImageTk

################################################################################

class Splash:

	def __init__(self, root, fileIn, wait, screen=None):
		self.__root = root
		self.__file = fileIn
		self.__wait = wait + time.clock()
		self.__screen = screen

	def __enter__(self):
		# Hide the root while it is built.
		self.__root.withdraw()
		if os.path.isfile(self.__file):
			# Create components of splash screen.
			self.__window = tk.Toplevel(self.__root)
			self.__canvas = tk.Canvas(self.__window)
			self._transparent()
			self.__splash = ImageTk.PhotoImage(Image.open(self.__file))
			# Get the screen's width and height.
			if self.__screen:
				scrW = self.__screen.w
				scrH = self.__screen.h
			else:
				scrW = self.__window.winfo_screenwidth()
				scrH = self.__window.winfo_screenheight()
			# Get the images's width and height.
			imgW = self.__splash.width()
			imgH = self.__splash.height()
			# Compute positioning for splash screen.
			Xpos = (scrW - imgW) // 2
			Ypos = (scrH - imgH) // 2
			# Configure the window showing the logo.
			self.__window.overrideredirect(True)
			self.__window.geometry('+{}+{}'.format(Xpos, Ypos))
			# Setup canvas on which image is drawn.
			self.__canvas.configure(width=imgW, height=imgH, highlightthickness=0)
			self.__canvas.grid()
			# Show the splash screen on the monitor.
			self.__canvas.create_image(imgW // 2, imgH // 2, image=self.__splash)
			self.__window.update()
			# Save the variables for later cleanup.

	def _transparent(self):
		self.__canvas.config(bg='black')
		try:
			self.__window.wm_attributes("-disabled", True)
		except tk.TclError:
			pass
		try:
			self.__window.wm_attributes("-transparent", True)
		except tk.TclError:
			pass
		try:
			self.__window.wm_attributes("-transparentcolor", "green")
			self.__canvas.config(bg='green')
		except tk.TclError:
			pass
		try:
			self.__window.config(bg='systemTransparent')
		except tk.TclError:
			pass

	def __exit__(self, exception_type, exception_value, traceback):
		# Ensure that required time has passed.
		now = time.clock()
		if now < self.__wait:
			time.sleep(self.__wait - now)
		if os.path.isfile(self.__file):
			# Free used resources in reverse order.
			del self.__splash
			self.__canvas.destroy()
			self.__window.destroy()
			# Give control back to the root program.
			self.__root.update_idletasks()
		self.__root.deiconify()
