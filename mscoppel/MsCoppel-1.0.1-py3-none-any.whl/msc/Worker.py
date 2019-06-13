from .Base import Base
from .ErrorMs import ErrorMs

class Worker(Base):
    """
        Clase que contiene la logica para el manejo de los
        worker.
    """

    def process(self, request, fnc):
        """
            Metodo que se encarga de procesar, la accion
            que se asign al evento del microservicio.

            @params resquest peticion de datos
            @params fnc Funcion a ejecutar
        """
        try:
            if request['metadata'].get('uuid', None):
                # Ejecutar la funcion
                RESP = fnc(
                    request.get('data'),
                    request["headers"]["Authorizacion"],
                    request["metadata"]["uuid"]
                )
            else:
                # Ejecutar la funcion con 3 parametros
                RESP = fnc(
                    request.get('data'),
                    request["headers"]["Authorizacion"]
                )
            # Regresar la respuesta con el formato correcto
            return self.__format(request, RESP)
        except ErrorMs as err:
            # Retornar el error
            return self.__format(request, None, err.errorCode)

    
    def __format(self, original, resp, errorCode = 0):
        """
            Metodo que se encarga de darle formato a la
            salida del procesamiento de la accion.
        """
        # Regresar la respuesta con el formato correcto 
        return {
            "errorCode": errorCode,
            "response": {
                "data": original.get("data", None),
                "headers": original.get("headers", {}),
                "metadata": original.get("metadata", {}),
                "response": {
                    "data": {
                        "response": resp
                    },
                    "meta": {
                        "id_transaction": original["metadata"]["id_transaction"],
                        "status": 'ERROR' if errorCode < 0 else 'SUCCESS'
                    }
                }
            }
        }