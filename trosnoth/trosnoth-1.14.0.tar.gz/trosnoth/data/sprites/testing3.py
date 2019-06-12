import pygame
from pygame.locals import *
import Tkinter
import sys   # for exit and arg

def Draw(surf):
  #Clear view
  surf.fill((80,80,80))
  pygame.display.flip()


def GetInput():

  for event in pygame.event.get():
    if event.type == QUIT:
      return True
    if event.type == KEYDOWN:
      print event
    elif event.type == MOUSEBUTTONDOWN:
      print event
    elif event.type == ACTIVEEVENT and event.state == 2:
      print 'ACTIVE:', event.gain
      if event.gain:
        # Simulate model dialog
        raise_tk_window()
    sys.stdout.flush()  # get stuff to the console
  return False


tk_window_closed = False

def quit_callback():
  global tk_window_closed
  tk_window_closed = True


def raise_tk_window():
  root.focus_force()
  root.lift()
  root.attributes('-topmost', 1)
  root.attributes('-topmost', 0)


def main():
  global root

  # initialise pygame
  pygame.init()
  ScreenSize = (200,100)
  Surface = pygame.display.set_mode(ScreenSize)

  # initialise tkinter
  root = Tkinter.Tk()
  root.protocol('WM_DELETE_WINDOW', quit_callback)
  main_dialog =  Tkinter.Frame(root)
  root.title("Test dialog")
  status_line = Tkinter.Label(main_dialog, text='Hello', bd=1, relief=Tkinter.SUNKEN, anchor=Tkinter.W)
  status_line.pack(fill=Tkinter.BOTH)
  main_dialog.pack()

  # start pygame clock
  clock = pygame.time.Clock()
  gameframe = 0

  # main loop
  while not tk_window_closed:
    try:
      main_dialog.update()
    except:
      print "dialog error"

    if GetInput():  # input event can also comes from diaglog
      break
    Draw(Surface)
    clock.tick(100) # slow it to something slightly realistic
    gameframe += 1

  main_dialog.destroy()


if __name__ == '__main__':
    main()
