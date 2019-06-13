import argparse
from VmorpheusVoice.tools.Profile import Profile
#from VmorpheusVoice.tools import Menu
from VmorpheusVoice.core.audio.Microphone import Microphone
from ctypes import *
from contextlib import contextmanager
import threading
class Console(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--cli', default=False, action="store_true", help='si esta activado se iniciara en modo consola usando los parametros')
        self.parser.add_argument('--source','-S',nargs='?',required=True,type=str,help='Archivo de audio de entrada')
        self.parser.add_argument('--profile','-P',nargs='?',type=str,default='test',help='Crear o usar perfil existente')
        self.parser.add_argument('--mic','-m',default=False, action="store_true" ,help='Usar microfono para generar entrada de audio')
        self.parser.add_argument('--show','-s',default=False, action="store_true", help='Mostrar perfiles creados')
        self.args = self.parser.parse_args()
    
    def iniciar_consola(self):
        profile = Profile(self.args.profile)
        mic = Microphone(profile)
        #menu = Menu()
        with noalsaerr():
            mic.set_input_device()
            sem = threading.Semaphore(0)
            threading.Thread(target=mic.record,args=sem)
            

    

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    
@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)