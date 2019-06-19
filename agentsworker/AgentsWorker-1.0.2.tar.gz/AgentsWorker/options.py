import os
import sys
from .loggs import Loggs

class Options:
    Debug = False
    Kafka = []
    Name = None
    Logger = Loggs('Options')
    def __init__(self, name, kafka):
        """
            Clase para la construccion de las opciones del microservicio.

            @params name Nombre del agente
            @params kafka Lista de direcciones de kafka.

            @returns void 
        """
        # Validar que se pase la direccion de kafka de forma correcta
        if not isinstance(kafka, list):
            self.Logger.error('No se proporciono una lista de direcciones de kafka correcta')
            sys.exit(-1)
        elif len(kafka) < 1:
            self.Logger.error('Se proporciono una lista vacia de Kafka Hosts')

        
        # Asignar la variable debug a verdadero si no es productivo.
        self.Debug = False if os.environ.get('PRODUCTION', None) else True

        # Asignar el nombre del microservicio
        self.Name = name

        # Asignar el cluster de kafka
        self.Kafka = kafka
