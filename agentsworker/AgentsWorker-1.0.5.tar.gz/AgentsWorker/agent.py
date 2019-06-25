"""
    Clase que contiene la logica de un agente
    para poder responder a las diferentes acciones
    que se le aplican.
"""
import sys
import inspect
import json
import socket
import uuid
import datetime
from .kafkaBase import KafkaBase
from .options import Options

class Agent(KafkaBase):

    # Acciones del microservicio
    __ACTIONS = {}

    def __init__(self, opt):
        # Validar que se pase un objeto de configuracion correcto
        if not isinstance(opt, Options):
            self.logs.error('No se proporciono una configuracion correcta')
            sys.exit(-1)
        
        # Cargar las acciones
        self.__initActions()

        # llamar el constructor padre
        KafkaBase.__init__(self, opt.Name, opt.Kafka)
    
    def _message(self, msg):
        """
            Metodo para el procesamiento de mensajes de
            kafka.

            {
                uuid: '',
                method: '',
                data: {},
                status: ''
            }
        """
        # Validar que cumpla con los campos minimo
        # if msg.get('uuid', None) or msg.get('method', None) or msg.get('data', None):
            # self.logs.warn('La peticion no cumple con la estructura necesaria')
            # return 0
        # Id de la operacion
        id = msg['uuid'].replace('-', '_')

        # Nombre del metodo a ejecutar
        methodName = msg['method']
        # Datos que son pasados al metodo
        data = msg['data']
        # Metodo que se ejecutara
        mth = None
        # Recuperar el metodo que se ejecutara
        try:
            mth = self.__getMethod(methodName)
        except Exception as e:
            self.logs.error(e)
            self._send(id, {
                "uuid": str(uuid.uuid4()),
                "status": 'ERROR',
                "data": {
                    "error": e
                }
            }, str(uuid.uuid4()))

        # Ejecutar el metodo
        try:
           resp =  mth(data)
           # Regresar la respuesta
           self._send(id, {
                "uuid": str(uuid.uuid4()),
                "status": 'SUCCESS',
                "data": resp
            }, str(uuid.uuid4()))
        except:
            self.logs.error(sys.exc_info()[1])
            self._send(id, {
                "uuid": str(uuid.uuid4()),
                "status": 'ERROR',
                "data": {
                    "error": str(sys.exc_info()[1])
                }
            }, str(uuid.uuid4()))

    def __initActions(self):
        """
            Metodo que se encarga de recuperar todas las
            acciones registradas, para su implementacion
            durante su llamado.
        """
        for f in inspect.getmembers(self):
            # Validar que tenga el atributo minimo
            if hasattr(f[1], '__AGENTS_ACTION__'):
                # Recuperar el tipo de accion
                action = getattr(f[1], '__ACTION__')
                # Almacenar la accion
                self.__ACTIONS.update({action: f[0]})

    def __getMethod(self, name):
        """
            Metodo para recuperar el metodo que se
            ejecutara.
        """
        if self.__ACTIONS.get(name, None):
            return self.__caller(self.__ACTIONS.get(name))
        else:
            print(self.__ACTIONS)
            self.logs.error('No se tiene registro del metodo {}'.format(name))
            raise Exception('No existe el metodo que se trata de llamar')
    
    def __caller(self, name):
        """
            Metodo para recuperar una propiedad que sera utilizada
            como metodo.
        """
        if hasattr(self, name):
            return getattr(self, name)