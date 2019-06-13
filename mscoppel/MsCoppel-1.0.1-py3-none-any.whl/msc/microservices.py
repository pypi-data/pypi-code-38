import sys
import inspect
import json
import socket
import datetime
from abc import abstractmethod, ABC
from .ms_base import KafkaBase
from .options import Options
from .types import TypesActions, Types
from .Worker import Worker
from .ErrorMs import ErrorMs

class Microservices(KafkaBase, ABC):
    """
        Clase con la logica necesaria para utilizar sobre los
        microservicios, se debe implementar los metodos segun
        como se requiera.
    """
    # Datos de configuracion
    __OPT = {}
    # Acciones del microservicio
    __ACTIONS = {}
    # Lista de errores definidos por el usuario
    __ERRORS = {
        '-97': 'No existe la accion que esta tratando de llamar',
        '-98': 'Ocurrio una error, favor de intentar de nuevo.',
        '-99': 'Ocurrio una excepcion, favor de intentar de nuevo.',
        '0': 'Smoke Test',
        '-1': 'Este servicio no puede ser consumido de forma externa'
    }
    # Logica de la aplicacion
    __APP = None

    # Topico
    __TOPIC__ = ''

    # Hostname
    __HOSTNAME = ''

    """
        Clase que contiene la logica del microservicio.
    """
    def __init__(self, opt):
        # Validar que se pase un objeto de configuracion correcto
        if not isinstance(opt, Options):
            self.logs.error('No se proporciono una configuracion correcta')
            sys.exit(-1)
        
        # Asignar los datos de la configuracion para su acceso
        self.__OPT = opt
        
        # Construccion del topico
        if opt.Legacy:
            topico = opt.Name
        else:
            topico = "{}_{}_{}".format(opt.App, opt.Version, opt.Name)
        
        # Asignar el topico
        self.__TOPIC__ = topico

        # Recuperar el hostname del servidor
        self.__HOSTNAME = socket.gethostname()

        # Crear el administrador de la logica de la aplicacion.
        if opt.Type == Types.WORKER:
            # Es un worker
            self.__APP = Worker()
        elif opt.Type == Types.FORK:
            # Es un Fork ( Bifurcacion )
            pass
        else:
            self.logs.error('No se reconoce el tipo asignado al microservicio')
            sys.exit(-1) # Forzar el cierre

        # Buscar las acciones
        self.__initActions()

        # llamar el constructor padre
        KafkaBase.__init__(self, topico, opt.Kafka)


    def _message(self, msg):
        """
            Metodo que se encagra de procesar todos los
            mensajes que llegas desde Kafka.
        """
        # metodo que se ejecutara
        mth = None
        # Recuperar los datos de otro modo regresar
        data = msg.get('data', {})
        # Recuperar la metadata
        meta = msg.get('metadata', {})
        # Validar si es un smoktest
        if 'smoketest' in list(data):
            # Ejecutar la funcion del smoketest
            if self.smoketest():
                # Todo esta bien
                self.__response(data, 0, True)
            else:
                # Algo salio bien
                self.__response(data, -1, True)

        # Validar si se encuentra en modo Debug
        if self.__OPT.Debug:
            self.logs.info("\n ENTRADA: {} \n HEADERS: {} \n DATA: {}".format(
                self.__TOPIC__,
                json.dumps(msg.get('headers', {})),
                msg.get('data', {})
            ))

        # Validar si es callback y no publico
        if meta.get('callback', '') == self.__TOPIC__ and not self.__OPT.Public:
            self.logs.warn('No se permite el acceso, no es publico.')
            # Regresar los datos originales
            self.__response(msg, -1)
        
        # ----------------------------------------------------------------->
        #   LOGICA PARA VALIDAR QUE NO A EXPIRADO [NO IMPLEMENTADA]
        # ----------------------------------------------------------------->

        # Procesar el mensaje
        try:
            mth = self.__getMethod(msg.get('metadata'))
        except Exception as identifier:
            # No fue posible recuperar una accion para el evento
            self.logs.error(identifier)

        # Enviar el mensaje al que procesa [Worker, Fork]
        try:
            RESP = self.__APP.process(msg, mth)
            # Enviar la respuesta
            self.__response(RESP.get('response', {}), RESP.get('errorCode'))
        except ErrorMs as error:
            self.logs.error(self.___getErrorId(error.errorCode))
            self.__response(msg, error.errorCode) # Enviar el error
        except Exception as e:
            self.logs.error(e)
            self.__response(msg, -99) # Enviar el error

    def __response(self, data, errorCode, isSmokeTest = False):
        """
            Metodo para enviar la respuesta a kafka
        """

        # Diccionario de la respuesta
        Resp = {}

        # Crear una copia de la respuesta
        dataResponse = data

        # Validar si ocurrio un error
        if errorCode < 0:
            # Estructura del mensaje de error
            dataResponse['response'] = {
                "data": {
                    "response": {
                        "hostname": self.__HOSTNAME,
                        "code": errorCode,
                        "userMessage": self.___getErrorId(errorCode)
                    }
                },
                "meta": {
                    "id_transaction": dataResponse['metadata']['id_transaction'],
                    "status": 'ERROR' if errorCode < 0 else 'SUCCESS'
                }
            }

        # Asignar el tiempo
        dataResponse['metadata']['time'] = datetime.datetime.now().isoformat()

        # Indicar el worker
        dataResponse['metadata']['worker'] = data['metadata']['owner']

        # Topico
        dataResponse['metadata']['owner'] = self.__TOPIC__

        # Tipo de salida
        dataResponse['metadata']['mtype'] = 'output'

        # Validar que tenga un uowner
        if dataResponse['metadata'].get("uowner", None):
            dataResponse['metadata']['uworker'] = data['metadata']['uowner']
        
        # Validar si tiene asignado un uworker
        if dataResponse['metadata'].get("uworker", None):
            dataResponse['metadata']['uowner'] = data['metadata']['uworker']
        
        # Topico de respuesta
        TOPIC_RESP = "respuesta_{}".format(dataResponse['metadata']['owner'])

        # Validar si es una bifurcacion
        if dataResponse['metadata'].get("bifurcacion", False):
            # Asignar el topico
            TOPIC_RESP = dataResponse['metadata'].get("callback")
            # Pasar a falso
            dataResponse['metadata']['bifurcacion'] = False
            # Indicar la salida de respuesta
            Resp = dataResponse
        else:
            # Asignar la respuesta
            Resp = {
                "_id": dataResponse['metadata']['id_transaction'],
                "metadata": dataResponse.get('metadata', {}),
                "response": dataResponse.get('response', {})
            }
        
        # Revisar si es un smoketest
        if isSmokeTest:
            # respuesta generica
            Resp.set('response', {
                "data": {
                    "response": {
                        "code": errorCode,
                        "hostname": self.__HOSTNAME,
                        "userMessage": "Smoke test"
                    }
                },
                "meta": {
                    "id_transaction": dataResponse['metadata']['id_transaction'],
                    "status": 'ERROR' if errorCode < 0 else 'SUCCESS'
                }
            })
        
        # Validar si es modeo DEBUG
        if self.__OPT.Debug:
            self.logs.info("SALIDA [{}]: {}".format(TOPIC_RESP, json.dumps(Resp)))

        # Publicar la respuesta
        self._send(TOPIC_RESP, Resp, dataResponse['metadata']['id_transaction'])

    def ___getErrorId(self, id_error):
        """
            Metodo apra recuperar los datos de un error registrado
        """
        try:
            if self.__ERRORS.get(str(id_error), None):
                return self.__ERRORS.get(str(id_error))
            else:
                return self.__ERRORS.get('-99')
        except:
            self.logs.error('Ocurrio un excepcion al recuperar los datos del error')
            return 'Ocurrio un error generico'

    def __getListener(self):
        """
            Metodo para recuperar la accion registrada
            en el Listener, de no contar con dicha accion
            se lanza una excepcion.
        """
        if self.__ACTIONS.get(TypesActions.LISTENER, None):
            return self.__caller(self.__ACTIONS.get(TypesActions.LISTENER))
        else:
            raise Exception('No existe un metodo para el evento solicitado')
    
    def __getMethod(self, meta):
        """
            Metodo para recuperar el metodo que se
            ejecutara, segun los datos pasados en 
            el metada.
        """
        if meta.get('method', None) and meta.get('uuid', None):
            if meta.get('method', None) == 'GET': # Consultar un elemento
                return self.__caller(self.__ACTIONS.get(TypesActions.GET))
            elif meta.get('method', None) == 'DELETE': # Eliminar el elemento 
                return self.__caller(self.__ACTIONS.get(TypesActions.DELETE))
            elif meta.get('method', None) == 'PUT': # Actualizar el elemento
                return self.__caller(self.__ACTIONS.get(TypesActions.UPDATE))
        elif meta.get('method', None) == 'GET': # Lista de servicios
            if self.__ACTIONS.get(TypesActions.LIST, None):
                return self.__caller(self.__ACTIONS.get(TypesActions.LIST))

        elif meta.get('method') == 'POST': # Creacion de un nuevo elemento
            if self.__ACTIONS.get(TypesActions.CREATE, None):
                return self.__caller(self.__ACTIONS.get(TypesActions.CREATE))

        # Regresar el Listener por default
        return self.__getListener()

    def __initActions(self):
        """
            Metodo que se encarga de recuperar todas las
            acciones registradas, para su implementacion
            durante su llamado.
        """
        for f in inspect.getmembers(self):
            # Validar que tenga el atributo minimo
            if hasattr(f[1], '__MICROSERVICE_ACTION__'):
                # Recuperar el tipo de accion
                typeAction = getattr(f[1], '__TYPE__')
                # Validar si es el de errores
                if typeAction == TypesActions.ERRORS:
                    # Recuperar la funcion para ejecutarla
                    errorFNC = self.__caller(f[0])
                    # Ejecutar la funcion para recuperar los errores definidos
                    errores_definidos = errorFNC()
                    # Validar que sea el tipo correcto
                    if not isinstance(errores_definidos, dict):
                        self.logs.error('No se proporciono un formato correcto para los errores definidos')
                        sys.exit(-1)
                    # Ejecutar y asignar los errores
                    self.__ERRORS = self.__merge_dicts(self.__ERRORS, errores_definidos)
                else:
                    # Almacenar la accion
                    self.__ACTIONS.update({typeAction: f[0]})

    def __caller(self, name):
        """
            Metodo para recuperar una propiedad que sera utilizada
            como metodo
        """
        if hasattr(self, name):
            return getattr(self, name)

    @abstractmethod
    def smoketest(self):
        """
            Metodo que es llamado para validar los
            servicios desde su consumo por REST/Kafka
        """
        pass

    def __merge_dicts(self, *dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
    
