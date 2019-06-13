"""
    Clase encargada de manejar la definicion de los
    decoradores para su implementacion sobre los 
    agentes.
"""

import inspect
import sys
from .loggs import Loggs
from .options import Options

def validParam(fn):
    """
        Metodo para validar que se proporcionaran
        los parametros minimos para la funciones
        que interactuan con un registro expecifico.
    """
    logs = Loggs('Agents')
    if len(inspect.getargspec(fn)[0]) < 2:
        logs.error('Toda accion de un agente requiere esperar dos parametros (data)')
        sys.exit(-1)

def Define(opt):
    """
        Metodo que agrega la informacion
        necesaria para iniciar la clase del
        agente.
    """
    def dec(cls):
        try:
            cls(opt)
        except KeyboardInterrupt:
            cls.logs.info('Keyboard Interrupt')
        return cls
    return dec

def asignDec(fn, actionName):
    """
        Metodo para agregar el decorador y los atributos
        necesarios para el reflect data
    """
    # Decorador de la funcion
    def decorated(*args,**kwargs):
        return fn(*args,**kwargs)
    # Asignar los atributos
    if inspect.isfunction(fn):
        setattr(decorated, '__AGENTS_ACTION__', True)
        setattr(decorated, '__ACTION__', actionName)
    return decorated

def Actions(name):
    """
        Decorador para la definicion de las acciones
        para su implementacion en los agentes
    """
    def dec(fn):
        # Validar la cantidad de parametros
        validParam(fn)
        # Retornar el decorador
        return asignDec(fn, name)
    # Retornar la funcion original
    return dec