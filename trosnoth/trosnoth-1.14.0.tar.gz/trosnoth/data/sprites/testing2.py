from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

# Start ShowBase, but don't open a Panda window yet
base = ShowBase(windowType='none')

# Start Tkinter integration, get the root window handle
base.startTk()

frame = base.tkRoot
import sys
sys.stderr.write('frame:\n')
sys.stderr.write('{}\n{}\n{}\n---\n'.format(type(frame), repr(frame), frame))
frame.update()
width = frame.winfo_width()
height = frame.winfo_height()

props = WindowProperties()
props.setParentWindow(frame.winfo_id())
props.setOrigin(0, 0)
props.setSize(width, height)

base.makeDefaultPipe()
base.openDefaultWindow(props=props)

scene = base.loader.loadModel("environment")
scene.reparentTo(base.render)

base.run()
