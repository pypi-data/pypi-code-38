# # -*- coding: utf-8 -*-
import logging
import json

from datetime import datetime

from apps.especificaciones import especificaciones as EspecificacionesApp
from apps.funciones import funciones as FuncionesApp
from apps.json.json import JsonManager
from configuraciones.general_texto_spa import *
from modelos.models import db, Registro, RegistroInterno

log = logging.getLogger(__name__)


class Sensor(object):
	"""
		Clase Sensor, estructura básica para todos los sensores
	"""

	@classmethod
	def get_codigo_sensor(cls):
		return "GENERICO"

	@classmethod
	def get_codigo_especificacion():
		"""Código asignado en especificaciones"""
		return -1

	@classmethod
	def get_especificacion(cls):
		"""
		Retorna el codigo especifico del Sensor definido en Especificaciones.
		"""
		
		for codigo in EspecificacionesApp.CODES_SENSORES:
			print(EspecificacionesApp.CODES_SENSORES[codigo]["clase"] , get_codigo_especificacion() )
			if EspecificacionesApp.CODES_SENSORES[codigo]["clase"] == get_codigo_especificacion():                
				return EspecificacionesApp.CODES_SENSORES[codigo]
			return None

	@classmethod
	def esActuador(cls):
		return False

	def __init__(self):
		self.id_sensor = 0
		self.guid_sensor = ""
		self.id_modulo = 0
		self.pin = 0
		self.nombre = "Nombre Sensor"
		self.estado = False  # desactivado por defecto el sensor
		self.tipo_actualizacion = ""
		self.tiempo = None
		self.variacion = None
		self.fe_registrado = None
		self.valor_max = None
		self.valor_min = None
		self.codigo = ""
		self.descripcion_serie = ""
		self.ti_conexion = 1
		self.topico_suscripto = ""

	def __str__(self):
		# s = super(Sensor, self).__str__()
		return " Sensor_" + "%%%" + "_" + str(self.id_sensor) + "_" + str(self.id_modulo) + ": " + str(self.nombre)

	def set_id_sensor(self, valor):
		self.id_sensor = valor

	def get_id_sensor(self):
		return self.id_sensor

	def set_pin(self, valor):
		self.pin = valor

	def get_pin(self):
		return self.pin

	def get_nombre(self):
		return self.nombre

	def activar(self):
		self.estado = True

	def desactivar(self):
		self.estado = False

	def get_estado(self):
		return self.estado

	def get_tipo_act(self):
		return self.tipo_actualizacion

	def get_tiempo(self):
		return self.tiempo

	def get_variacion(self):
		return self.variacion

	def get_fecha_registrado(self):
		return self.fe_registrado

	def get_valor_max(self):
		return self.valor_max

	def get_valor_min(self):
		return self.valor_min

	def set_values(self, dict):  # MEJORAR: Tratarlo con escpecificaciones
		"""
			Setea los valores para un Sensor a partir de los datos de un diccionario.
		"""
		if dict:
			self.id_sensor = dict["id_sensor"]
			self.guid_sensor = dict["guid_sensor"]
			self.id_modulo = dict["id_modulo"]
			self.nombre = dict["nombre_sensor"]
			self.pin = dict["pin_sensor"]
			self.estado = dict["estado_sensor"]
			self.tipo_actualizacion = dict["tipo_actualizacion"]
			self.tiempo = dict["tiempo"]
			self.variacion = dict["variacion"]
			self.valor_max = dict["val_max"]
			self.valor_min = dict["val_min"]
			self.descripcion_serie = dict["descripcion_serie"]
			self.ti_conexion = dict["ti_conexion"]
			self.topico_suscripto = dict["topico_suscripto"]

	def mostrar(self):
		log.info(TXT_ID_SEN + str(self.id_sensor))
		log.info(TXT_NOM + self.nombre)
		log.info(TXT_PIN_SEN + str(self.pin))
		if self.estado:
			log.info(TXT_EST + TXT_EST_VAL)
		else:
			log.info(TXT_EST + TXT_EST_INV)

	def mostrar_con_validacion(self, condicion):
		log.info(TXT_ID_SEN + str(self.id_sensor))
		log.info(TXT_NOM + self.nombre)
		log.info(TXT_PIN_SEN + str(self.pin))
		if condicion:
			log.info(TXT_EST + TXT_EST_V)
		else:
			log.info(TXT_EST + TXT_EST_I)

	def get_json(self, sensorEspecifico, get_data=True, data_mqtt=None):
		"""
			Devuelve un Json apartir de los datos de atributo de una instancia de un SensorEspecifico.
			Parametros:
				_sensorEspecifico: Instancia de un algun Sensor Especifico
				_get_data: *bool* con valor de verdad para saber si obtiene datos de un sensor especifico
			Retorna:
				_json_instance: Instancia del tipo *json* con los datos de Registro para un Sensor Especifico.
		"""
		if get_data:
			if data_mqtt:
				sensorEspecifico.valor = float(data_mqtt)
			else:
				resultado = sensorEspecifico.obtener_datos()
				if resultado is None: return None

			sensorEspecifico.fe_registrado = str(datetime.now())

		json_instance = JsonManager.generateJsonRegistro(self=None, sensorEspecifico=sensorEspecifico)

		return json_instance

	def desactivar_sensor(self):
		bool = FuncionesApp.desactivar_sensor(self.id_sensor)
		return bool

	def get_dict_values(self, sensorEspecifico):
		"""
			Retorna un diccionario con los datos de todos los campos para un Sensor Especifico.
			Ejemplo:
				 {'humedad': 10.0, 'modulo_0': None, 'modulo_1': None, 'temperatura': 23.0, 'grados': 'C',
				 'id_sensor': 3, 'pin': 0, 'nombre': 'Nombre Sensor', 'estado': False, 'tipo_actualizacion': '',
				 'tiempo': None, 'variacion': None, 'fe_registrado': '2018-02-26 11:44:02.319040', 'valor_max': None,
				 'valor_min': None, 'codigo': ''}
		"""
		return sensorEspecifico.__dict__

	def registrar(self, sensorEspecifico):
		"""
			Crea una instancia del tipo RegistroInterno (de acuerdo al Modelo) a partir de un Sensor Especifico con la ayuda
			de Especificaciones.
			Parametros:
				_sensorEspeifico: Instancia del tipo Sensor Especifico a partir del cual se generara el Registro.
		"""
		registro = Registro()
		msj_ok = "Se ha insertado correctamente un Registro para " + str(sensorEspecifico)
		msj_error = 'Ha ocurrido un problema al Insertar Registro: '
		self.generar_registro(registro=registro, sensorEspecifico=sensorEspecifico, msj_ok=msj_ok, msj_error=msj_error)

	def registrar_estado_interno(self, sensorEspecifico, registro):
		"""
			Crea una instancia del tipo RegistroInterno (de acuerdo al Modelo) a partir de un Sensor Especifico con la ayuda
			de Especificaciones.
			Parametros:
				_sensorEspeifico: Instancia del tipo Sensor Especifico a partir del cual se generara el Registro.
		"""
		msj_ok = "Se ha insertado actualizado correctamente Registro Interno de: " + str(sensorEspecifico)
		msj_error = 'Ha ocurrido un problema al Actualizar Registro Interno de : ' + str(sensorEspecifico)
		self.generar_registro(registro=registro, sensorEspecifico=sensorEspecifico, msj_ok=msj_ok, msj_error=msj_error)

	def generar_registro(self, sensorEspecifico, registro, msj_ok, msj_error):
		"""
			Genera un *Registro o RegistroInterno* a partir de un sensorEspecifico.
			Parametros:
				_sensorEspecifico:
				_registro: Instancia del registro o RegistroInterno al cual se le setearan los valores.
				_msj_ok: Mensaje de Resultado correcto de la operacion.
				_msj_error: Mensaje de Resultado de falla de la operacion.
			Retorna:
				Nada, solo muestra mensaje en log del resultado de la operacion.
		"""

		list_fields_sensor = EspecificacionesApp.CODES_SENSORES[sensorEspecifico.get_especificacion()]['fields']
		for field_sensor in list_fields_sensor:
			try:
				field_registro = EspecificacionesApp.PARSEO_REGISTRO[field_sensor]
				value = EspecificacionesApp.sensor_gestion_value(sensorEspecifico=sensorEspecifico, field=field_sensor)
			except Exception as e:
				log.critical('CODE ERROR: k123k - ' + str(e))

			if value:
				EspecificacionesApp.registro_gestion_value(field=field_registro, value=value, registro=registro,
														   modo="SET")

		db.session.add(registro)
		try:
			db.session.commit()
			log.info(msj_ok)
		except Exception as e:
			db.session.rollback()
			log.error(msj_error + str(e))
	
	def stopThread(self):
		""" Encargado de detener hilos que se creen para un sensor en aprticular. 
		Se redefine en cada sensor especifico"""
		#print("stopThread!")
		return None
