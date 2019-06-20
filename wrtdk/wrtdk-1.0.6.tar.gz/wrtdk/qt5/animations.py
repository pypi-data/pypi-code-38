'''
Created on Nov 20, 2018

@author: reynolds
'''

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QStatusBar, QSizePolicy, QVBoxLayout, QWidget, QApplication, QPushButton
from PyQt5.QtOpenGL import QGLWidget
import sys

class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.widget = CubeWidget(self,0,0,0,pz=.6)
        self.button = QPushButton('Change')
        self.button.clicked.connect(self.onClick)
        self.statusbar = QStatusBar()
        self.statusbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        layout.addWidget(self.button)
        layout.addWidget(self.statusbar)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
    def onClick(self):
        self.widget.update(0, 0, 180)

class OpenGLWidget(QGLWidget):

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(100, 100)
        #LMB = left mouse button
        #True: fires mouseMoveEvents even when not holding down LMB
        #False: only fire mouseMoveEvents when holding down LMB
        self.setMouseTracking(False)
        self.screen = Screen()

    def initializeGL(self):
        glClearColor(0, 0, 0, 1)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        #glViewport is needed for proper resizing of QGLWidget
        aspect = float(width)/float(height)
        self.screen.update(2*aspect,2,2)
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.screen.getX0(),self.screen.getX(),
                self.screen.getY0(),self.screen.getY(),
                self.screen.getZ0(),self.screen.getZ())
        #glOrtho(0, width, 0, height, -1, 1)
        #gluPerspective(45, 1.0 * width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        #Renders a triangle... obvious (and deprecated!) stuff
        #w, h = self.width(), self.height()# not needed anymore
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # draw the graphic
        self.graphic()

    def graphic(self):
        pass
    
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass
    
class CubeWidget(OpenGLWidget):
    
    def __init__(self,parent=None,roll=0,pitch=0,yaw=0,px=.2,py=.2,pz=.2):
        self._px = px
        self._py = py
        self._pz = pz
        OpenGLWidget.__init__(self,parent)
        self.update(roll,pitch,yaw)
        
    def update(self,roll=0,pitch=0,yaw=0):
        self._roll = roll
        self._pitch = pitch
        self._yaw = yaw
        self.glDraw()
        
    def graphic(self):
        glTranslatef(0,0,0)
        
        #string = 'Roll: %.2f, Pitch: %.2f, Yaw: %.2f' % (self._roll,self._pitch,self._yaw)
        #drawtext((-.75,-.75,-.75),string)
        
        glRotatef(self._pitch,1.0,0.0,0.0)
        glRotatef(self._yaw,0.0,-1.0,0.0)
        glRotatef(self._roll,0.0,0.0,1.0)
        
        r = ScreenCube(self.screen.getW(),self.screen.getH(),self.screen.getT(),
                       self._px,self._py,self._pz)
        
        glBegin(GL_QUADS)
        
        glColor3f(0.0,1.0,0.0)
        glVertex3f( r.getX(), r.getY(),r.getZ0())# 1.0, 0.2,-1.0)
        glVertex3f(r.getX0(), r.getY(),r.getZ0())#-1.0, 0.2,-1.0) 
        glVertex3f(r.getX0(), r.getY(), r.getZ())#-1.0, 0.2, 1.0) 
        glVertex3f( r.getX(), r.getY(), r.getZ())# 1.0, 0.2, 1.0)
        
        glColor3f(1.0,0.5,0.0)
        glVertex3f( r.getX(),r.getY0(), r.getZ())#1.0,-0.2, 1.0)
        glVertex3f(r.getX0(),r.getY0(), r.getZ())#-1.0,-0.2, 1.0)        
        glVertex3f(r.getX0(),r.getY0(),r.getZ0())#-1.0,-0.2,-1.0)        
        glVertex3f( r.getX(),r.getY0(),r.getZ0())# 1.0,-0.2,-1.0)
         
        glColor3f(1.0,0.0,0.0)        
        glVertex3f( r.getX(), r.getY(), r.getZ())# 1.0, 0.2, 1.0)
        glVertex3f(r.getX0(), r.getY(), r.getZ())#-1.0, 0.2, 1.0)        
        glVertex3f(r.getX0(),r.getY0(), r.getZ())#-1.0,-0.2, 1.0)        
        glVertex3f( r.getX(),r.getY0(), r.getZ())# 1.0,-0.2, 1.0)
        
        glColor3f(1.0,1.0,0.0)    
        glVertex3f( r.getX(),r.getY0(),r.getZ0())# 1.0,-0.2,-1.0)
        glVertex3f(r.getX0(),r.getY0(),r.getZ0())#-1.0,-0.2,-1.0)
        glVertex3f(r.getX0(), r.getY(),r.getZ0())#-1.0, 0.2,-1.0)        
        glVertex3f( r.getX(), r.getY(),r.getZ0())# 1.0, 0.2,-1.0)
        
        glColor3f(0.0,0.0,1.0)    
        glVertex3f(r.getX0(), r.getY(), r.getZ())#-1.0, 0.2, 1.0)
        glVertex3f(r.getX0(), r.getY(),r.getZ0())#-1.0, 0.2,-1.0)        
        glVertex3f(r.getX0(),r.getY0(),r.getZ0())#-1.0,-0.2,-1.0)        
        glVertex3f(r.getX0(),r.getY0(), r.getZ())#-1.0,-0.2, 1.0)
        
        glColor3f(1.0,0.0,1.0)    
        glVertex3f( r.getX(), r.getY(),r.getZ0())# 1.0, 0.2,-1.0)
        glVertex3f( r.getX(), r.getY(), r.getZ())# 1.0, 0.2, 1.0)
        glVertex3f( r.getX(),r.getY0(), r.getZ())# 1.0,-0.2, 1.0)        
        glVertex3f( r.getX(),r.getY0(),r.getZ0())# 1.0,-0.2,-1.0)
        
        glEnd()
     
class TriangeWidget(OpenGLWidget):
    
    def __init__(self,parent=None):
        OpenGLWidget.__init__(self,parent)
        
    def graphics(self):
        glBegin(GL_TRIANGLES)
        glColor3f(1, 0, 0)
        glVertex3f(self.screen.getX0(),self.screen.getY0(), 0)
        glColor3f(0, 1, 0)
        glVertex3f(0,self.screen.getY(), 0)
        glColor3f(0, 0, 1)
        glVertex3f(self.screen.getX(), 0, 0)
        glEnd()
        
    def mouseReleaseEvent(self, event):
        OpenGLWidget.mouseReleaseEvent(self, event)
        
        x, y = event.x(), event.y()
        #w, h = self.width(), self.height()
        #required to call this to force PyQt to read from the correct, updated buffer 
        #see issue noted by @BjkOcean in comments!!!
        glReadBuffer(GL_FRONT)
        data = self.grabFrameBuffer()#builtin function that calls glReadPixels internally
        data.save("test.png")
        rgba = QColor(data.pixel(x, y)).getRgb()#gets the appropriate pixel data as an RGBA tuple
        message = "You selected pixel ({0}, {1}) with an RGBA value of {2}.".format(x, y, rgba)
        statusbar = self.parent().statusbar#goes to the parent widget (main window QWidget) and gets its statusbar widget
        statusbar.showMessage(message)

class Screen(object):
    
    def __init__(self,x=1,y=1,z=1):
        self.update(x,y,z)
        
    def update(self,x=1,y=1,z=1):
        self._w, self._h, self._t = x,y,z
        self._x0,self._x = -x/2.0, x/2.0
        self._y0,self._y = -y/2.0, y/2.0
        self._z0,self._z = -z/2.0, z/2.0
        
    def getX0(self):
        return self._x0
    
    def getX(self):
        return self._x
    
    def getY0(self):
        return self._y0
    
    def getY(self):
        return self._y
    
    def getZ0(self):
        return self._z0
    
    def getZ(self):
        return self._z
    
    def getW(self):
        return self._w
    
    def getH(self):
        return self._h
    
    def getT(self):
        return self._t
    
class ScreenCube(object):
    
    def __init__(self,w=1,h=1,t=1,pw=0.1,ph=0.1,pt=0.2):
        if pw > 1: pw = 1
        if ph > 1: ph = 1
        if pt > 1: pt = 1
        self._w, self._h, self._t = w * pw, h * ph, t * pt
        self._x0, self._y0, self._z0 = -self._w/2.0, -self._h/2.0, -self._t/2.0
        self._x, self._y, self._z = -self._x0, -self._y0, -self._z0
        
    def getW(self):
        return self._w
    
    def getH(self):
        return self._h
        
    def getX0(self):
        return self._x0
    
    def getY0(self):
        return self._y0
    
    def getZ0(self):
        return self._z0
    
    def getX(self):
        return self._x
    
    def getY(self):
        return self._y
    
    def getZ(self):
        return self._z

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(10,10)
    window.setWindowTitle("Color Picker Demo")
    window.show()
    app.exec_()

