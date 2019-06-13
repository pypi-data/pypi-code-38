"""
    Modulo para la implementacion de los decoradores,
    necesarios para el uso de reflec data, al momento
    de registrar las acciones de los microservicios.
"""

import inspect
import sys
from .options import Options
from .types import TypesActions, Types
from .loggs import Loggs

def validParam(fn):
    """
        Metodo para validar que se proporcionaran
        los parametros minimos para la funciones
        que interactuan con un registro expecifico.
    """
    logs = Loggs('Core')
    if len(inspect.getargspec(fn)[0]) < 4:
        logs.error('Lo metodos GET, DELETE, UPDATE requieren 3 parametros (data, auth, id) ')
        sys.exit(-1)

def asignDec(fn, typeDec):
    """
        Metodo para agregar el decorador y los atributos
        necesarios para el reflect data
    """
    # Decorador de la funcion
    def decorated(*args,**kwargs):
        return fn(*args,**kwargs)
    # Asignar los atributos
    if typeDec == TypesActions.ERRORS or inspect.isfunction(fn):
        setattr(decorated, '__MICROSERVICE_ACTION__', True)
        setattr(decorated, '__TYPE__', typeDec)
    return decorated

def Define(opt):
    """
        Metodo que agrega la informacion
        necesaria para iniciar la clase del
        microservicio.
    """
    def dec(cls):
        try:
            cls(opt)
        except KeyboardInterrupt:
            cls.logs.info('Keyboard Interrupt')
        return cls
    return dec

def List(fn):
    """
        Decorador para las acciones de tipo
        LIST (GET a la raiz del servicio)
    """
    return asignDec(fn, TypesActions.LIST)

def Get(fn):
    """
        Decorador de la accion cuando se solicitan
        los datos de un elemento especifico
    """
    # Validar la cantidad de parametros
    validParam(fn)
    # Retornar el decorador
    return asignDec(fn, TypesActions.GET)

def Create(fn):
    """
        Decorador de accion de creacion de un
        elemento en el servicio
    """
    return asignDec(fn, TypesActions.CREATE)

def Update(fn):
    """
        Decorador de actualizacion de un
        servicio en especfico
    """
    # Validar la cantidad de parametros
    validParam(fn)
    # Retornar el decorador
    return asignDec(fn, TypesActions.UPDATE)

def Delete(fn):
    """
        Decorador de accion de eliminacion
        de un elemento especfico
    """
    # Validar la cantidad de parametros
    validParam(fn)
    # Retornar el decorador
    return asignDec(fn, TypesActions.DELETE)

def Listener(fn):
    """
        Decorador Generico
    """
    return asignDec(fn, TypesActions.LISTENER)

def Errors(fn):
    """
        Decorador para asignacion de los errores
    """
    return asignDec(fn, TypesActions.ERRORS)