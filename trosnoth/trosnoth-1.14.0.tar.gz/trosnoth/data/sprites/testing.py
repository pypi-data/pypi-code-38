import time

import PIL.Image
import PIL.ImageTk
import pygame.image


FILENAME = 'bigCoin0.png'



pgimg = pygame.image.load(FILENAME)



#######################
from tkinter import Tk, Label, Button


root = Tk()
root.title("A simple GUI")

t0 = time.time()
data = pygame.image.tostring(pgimg, 'RGBA')
pilimg = PIL.Image.frombytes('RGBA', pgimg.get_size(), data)
tkimg = PIL.ImageTk.PhotoImage(pilimg)
t1 = time.time()
print(t1 - t0)

label = Label(root, image=tkimg)
label.pack()

close_button = Button(root, text="Close", command=root.quit)
close_button.pack()
root.mainloop()
