from .codigos_sensores import CODES_SENSORES

#######################################################
# 						SENSORES 					  #
#######################################################
def get_modulos(code_sensor):
    """
		Devuelve el valor del campo modulos de CODES_SENSORES de acuerdo al 
		codigo numerico de un sensor que se recibe como parametro.
        Parametros:
            _code_sensor: codigo numerico del sensor.
	"""
    for key in CODES_SENSORES.keys():
        if CODES_SENSORES[key]["clase"] == code_sensor: return CODES_SENSORES[key]["modulos"]
    return []


def get_code_alfabetico(code_sensor):
    """
		Devuelve el codigo alfabetico de un sensor de acuerdo al 
		codigo numerico que se recibe como parametro.
	"""
    for key in CODES_SENSORES.keys():
        if CODES_SENSORES[key]["clase"] == code_sensor:
            return key
    return None


def get_code_numerico(code_sensor):
    """
		Devuelve el codigo numerico de un sensor de acuerdo al
		codigo alfabetico que se recibe como parametro.
	"""
    try:
        code = CODES_SENSORES[code_sensor]["clase"]
    except Exception as e:
        print("ERROR 11 - ", str(e))
        code = "Sensor No valido"

    return code

def get_unidad(code_sensor, nro_modulo):
    """
		Retorna la unidad de un sensor de especificaciones
		Recibe como parametro: 
			_code_sensor: codigo alfabetico del sensor.
			_nro_modulo: nro de modulo del sensor
	"""
    de_unidad = ""
    try:
        de_unidad = CODES_SENSORES[code_sensor]["de_unidad"][nro_modulo]
    except Exception as e:
        print("ERROR 12 -Error al obtener Unidad - " + str(e))
    return de_unidad

def get_module_name(code_sensor, nro_modulo):
    """
        Retorna la unidad de un sensor de especificaciones
        Recibe como parametro: 
            _code_sensor: codigo alfabetico del sensor.
            _nro_modulo: nro de modulo del sensor
    """
    de_modulo = ""
    try:
        de_modulo = CODES_SENSORES[code_sensor]["modulos"][nro_modulo]
    except Exception as e:
        print("ERROR 12 -Error al obtener nombre de modulo - " + str(e))
    return de_modulo

