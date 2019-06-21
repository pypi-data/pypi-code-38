#!/usr/bin/env python3
# -*-coding:utf-8 -*


import time
from threading import Thread

import serial

from irsensors.irsensor import IRSensor


class IRSensorSet(Thread):
	"""This class represent the IR sensor set.

	This class is a thread, it means that the run method will be executed in parallel to the main program as soon as the start method is call in the main program.

	Attributes:
		THREAD_ATTRIBUTES is a tuple of attribute's name that need to be modifie for the thread to run well.
		_sensor is the serial connection USB with the physical sensor.
		_sensors is the list of IR sensor contents in the physical sensor.
		_listening is the control variable for knowing if the thread is launched or not.

		main method :
			listen(self) :
				This method is call by the run method, itself called by the start method as explain before. The user needs to launche the start method to access sensor's data.
				This method read data from the physical sensor throught the _sensor attribute. After a little process on the data, give it to the right IRSensor in the attribute _sensors list.

		other methods :
			__len__(self): Give the number of sensor in the sensor set.
			run(self):
				This method is executed in parallel to the main programm as soon as the main program call the start method.
				Firstly, check if the thread is not already launched, then update the _listening attribute, open the serial connection, write '1' for the physical sensor to start sending datas and launche the listen method in a while loop as long as the _listening attribute is True.
				Finally, when the _listening attribute changes from True to False, stop to launche the listen method, write '0' for the physical sensor to stop sending datas and close the serial connection USB.
			stop(self): Change the _listening attribute's value from True to False to stop the loop in the run method.
			__repr__(self): Return a str which indicates the class of the object and the value of his attributes.
			__str__(self): Return a str which indicates the distance of each IRSensor in the _sensor list, in the same order as their ID was given in the constructor.

	"""
	THREAD_ATTRIBUTES = (  # this class attribute tuple lists the attributes that need to be modifie for the thread to run well.
        "_target", "_name",	"_args", "_kwargs",	"_daemonic", "_ident",
		"_tstate_lock", "_started", "_is_stopped", "_initialized", "_stderr",
		"_verbose", "_stopped", "_block"
	)

	def __init__(self, port='COM22', baud=9600, time_out=1,
		id_sensors=[3, 1, 2, 0], nb_values_history=10):
		"""Constructor of the IRSensorSet class.

		Create the serial connection USB.
		Create the list of IRSensor.
		Set the _listening attribute to False.

		"""
		Thread.__init__(self)
		object.__setattr__(self, "_sensor", serial.Serial(port, # Represent the USB connection with the physical sensor set.
			baud, timeout = time_out))
		getattr(self, "_sensor").close()

		sensors = []    # List of sensor which represent each real IR sensor. Each has an ID, and make a mean on nb_values for the distance.
		for i in range(len(id_sensors)):
			sensors.append(IRSensor(
				id=id_sensors[i],
				nb_values=nb_values_history
		))
		object.__setattr__(self, "_sensors", sensors)
		object.__setattr__(self, "_listening", False)   # thread not launched.


	def __getattr__(self, attribute_name):
		"""Raise an AttributeError when the user tries to access an attribute that does not exist."""
		raise AttributeError("'IRSensorSet' object has no attribute " + attribute_name)

	def __setattr__(self, attribute_name, attribute_value):
		"""Apart from some attributes for the thread to run well, raise an TypeError when the user tries to modifie an attribute's value.

		The varaiables which names are in the THREAD_ATTRIBUTE tuple should not be modified by the outside.

		"""
		if attribute_name in IRSensorSet.THREAD_ATTRIBUTES:    # The mother class need to modifie these attributes.
			object.__setattr__(self, attribute_name, attribute_value)
			return
		raise TypeError("'IRSensorSet' object does not support attribute assignment " + \
		"(attributeName -> " + attribute_name + ", attributeValue -> " + str(attribute_value) + ")")

	def __delattr__(self, attribute_name):
		"""Raise an TypeError when the user tries to delete an attribute."""
		raise TypeError("'IRSensorSet' object does not support attribute deletion " + \
		"(attributeName -> " + attribute_name + ")")


	def __getitem__(self, item_name):
		"""aise an AttributeError when the user tries to access an attribute as item."""
		if item_name in ("sensor", "sensors", "listening"):
			raise TypeError("'IRSensorSet' object does not support item reading " + \
			"(attributeName -> " + item_name + ")")
		raise KeyError("'IRSensorSet' has no item " + item_name)

	def __setitem__(self, item_name, item_value):
		"""Raise an TypeError when the user tries to modifie the value of an attribute as item."""
		raise TypeError("'IRSensorSet' object does not support item assignment " + \
		"(attributeName -> " + item_name + ", attributeValue -> " + str(item_value) + ")")

	def __delitem__(self, item_name):
		"""Raise an TypeError when the user tries to delete an attribute as items."""
		raise TypeError("'IRSensorSet' object does not support item deletion " + \
		"(attributeName -> " + item_name + ")")


	def __len__(self):
		"""Return the lenght of the _sensors list.

		Give the number of sensors.

		"""
		return len(getattr(self, "_sensors"))


	def run(self):
		"""Launche the thread.

		If the thread is already running, do not do anything.
		If the thread is not already running, open the serial connection USB, write '1' for the physical sensor to start sending datas and launche the listen method in a while loop as long as the _listening attribute is True.
		Finally, when the _listening attribute changes from True to False, stop to launche the listen method and stop the while loop, write '0' for the physical sensor to stop sending datas and close the serial connection USB.

		"""
		if not getattr(self, "_listening"):
			object.__setattr__(self, "_listening", True)
			serial_usb = getattr(self, "_sensor")
			serial_usb.open()
			serial_usb.write(b'1')
			while getattr(self, "_listening"):
				self.listen()
			serial_usb.write(b'0')
			serial_usb.close()

	def listen(self):
		"""Main part of the thread : Read the datas from USB connection and give it to the right sensor.

		Read one line of data from the physical sensor.
		Decode, split and remove the \r\n at the end of the datas.
		Simplify the ID. /!\ As the simplification take on count only one digit, it will make some problems if the id is greater or equal to 10.
		Convert the error code from string to int.
		Convert the distance from string to float.
		Search the good IRSensor in the _sensor attribute list and give it datas throught the write method.

		"""
		datas_tmp = getattr(self, "_sensor").readline()
		datas_tmp = datas_tmp.decode().split(",")[:-1]	# [:-1] because the last element is the string "\r\n".
		datas_tmp[0] = int(datas_tmp[0][-1])	# Simplify the ID

		datas_tmp[1] = int(datas_tmp[1])  # Convert the error code from string to int.

		datas_tmp[2] = float(datas_tmp[2])    # Convert the distance from string to float.

		for sensor in getattr(self, "_sensors"):    # Look for the good sensor ID and give it the data.
			if sensor["ID"] == datas_tmp[0]:
				sensor.write(
					id=datas_tmp[0],
					error=datas_tmp[1],
					distance=datas_tmp[2]
				)

	def stop(self):
		"""Stop the thread."""
		if getattr(self, "_listening"): # If the thread is not already launched.
			object.__setattr__(self, "_listening", False)


	def __repr__(self):
		"""Return a str which indicates the class of the object and the value of his attributes."""
		serial_usb = getattr(self, "_sensor")
		return "<Class = IRSensorSet, port = "+serial_usb.port + \
			", Baudrate = "+str(serial_usb.baudrate) + \
			", TimeOut = "+str(serial_usb.timeout) + \
			", NbSensors = "+str(len(self)) + \
			", listening = "+str(getattr(self, "_listening")) + ">"

	def __str__(self):
		"""Return a str which contains the distance from each sensor.

		1 column = 1 sensor. Distance is in cm and the value can be up to 10m excluded.

		"""
		str_datas = ""
		for i in range(len(self)):
			distance = getattr(self, "_sensors")[i]["distance"]/10
			str_datas += ("%5.1f"%distance) + "\t"
		return str_datas


	def __del__(self):
		"""Destructor of the IRSensorSet class."""
		self.stop()


__all__ = ["IRSensorSet"]


if __name__ == "__main__":
	test = IRSensorSet()
	try:
		test.start()
		print(
			repr(test), "\n",
			str(test), "\n"
		)

		while True:
			print(test)
			time.sleep(0.1)

	except KeyboardInterrupt:
		pass

	finally:
		test.stop()
		del test
