#!/usr/bin/env python3
# -*-coding:utf-8 -*


def mean(float_list):
	"""Calcul and return the mean for the given list of numbers (float and int).

	If the list is emmpty or None, return None.
	Else, the value returned is a float."""
	if float_list is None or not float_list:
		return None

	sum = 0
	for number in float_list:
		sum += float(number)
	return sum/len(float_list)


class IRSensor:
	"""This class represent each IR sensors of the sensor set.

	Attributes:
		_ID is the sensor's id. This attribute must not be modified. We can get it as an item with the key value "ID".
		_history is a list of float number which contains the last values given by the sensor. At the index 0, there is the newest value. At the end of the list there is the oldest value. This attribute must no be modified by the outside nor be readable.
		_distance is the mean value from the _history list. This attribute must not be modified by the outside but can be read as an item with the key value "distance".

		main method :
			write(self, id, distance, error) : This method should only be called by a IRSensorSet object. The IRSensorSet object read datas from an serial connection and give them to an IRSensor object through this method.

		other methods :
			__len__(self): Give the number of values in the history list attribute.
			__repr__(self): Return a str which indicates the class of the object and the value of his attributes.
			__str__(self): Return a str which indicates the value of the _distance attribute only.

	"""
	def __init__(self, id, nb_values=10):
		"""Constructor of the IRSensor class.

		Set the id given in parameter.
		Create the hystory list full of 0.
		Set the distance at 0.

		"""
		object.__setattr__(self, "_ID", int(id))
		object.__setattr__(self, "_history", [0] * int(nb_values))
		object.__setattr__(self, "_distance", 0)


	def __getattr__(self, attribute_name):
		"""Raise an AttributeError when the user tries to access an attribute that does not exist."""
		raise AttributeError("'IRSensor' object has no attribute " + attribute_name)

	def __setattr__(self, attribute_name, attribute_value):
		"""Raise an TypeError when the user tries to modifie an attribute's value."""
		raise TypeError("'IRSensor' object does not support attribute assignment " + \
		"(attributeName -> " + attribute_name + ", attributeValue -> " + str(attribute_value)+")")

	def __delattr__(self, attribute_name):
		"""Raise an TypeError when the user tries to delete an attribute."""
		raise TypeError("'IRSensor' object does not support attribute deletion " + \
		"(attributeName -> " + attribute_name + ")")


	def __getitem__(self, item_name):
		"""Give acces to all attributes as items except _history attribute.

		Raise an KeyError when the user tries to access _history attribute or an attribute that does not exist.

		"""
		if item_name == "ID":
			return self._ID
		if item_name == "distance":
			return self._distance
		if item_name == "history":
			raise KeyError("'IRSensor' object does not support history attribute reading")
		raise KeyError("'IRSensor' has no item " + item_name)

	def __setitem__(self, item_name, item_value):
		"""Raise an TypeError when the user tries to modifie the value of an attribute as item."""
		raise TypeError("'IRSensor' object does not support item assignment " + \
		"(attributeName -> " + item_name + ", attributeValue -> " + str(item_value) + ")")

	def __delitem__(self, item_name):
		"""Raise an TypeError when the user tries to delete an attribute as items."""
		raise TypeError("'IRSensor' object does not support item deletion " + \
		"(attributeName -> " + item_name + ")")


	def __len__(self):
		"""Return the lenght of the _history list."""
		return len(getattr(self, "_history"))


	def write(self, id, distance, error):
		"""Get, save the last sensor's data and update the distance.

		id: sender sensor's id.
		distance: sender sensor's distance data.
		error: sender sensor's error data.

		Check if the id is the good one and act differently according to the error code (if the id is not the good one, do nothing).
			If the error = 0, it means that there is not any error.
				Erase the last value of the _history attribute (it's the oldest value), put the new value (distance parameter) at the index 0 of the _history list and update the distance value with the mean of the _history list.
			If the error = 1
				Do nothing.
			If the error = 2
				Do nothing.
			If the error = 3, it means that the target is to close.
				Do the same thing as if the error code is 0, but replace the distance parameter by 0.
			If the error = 4
				Do nothing.
			If the error = 5
				Do nothing.
			If the error = 6
				Do nothing.
			If the error = 7
				Do nothing.
			If the error = 8
				Do nothing.
			If the error = 9
				Do nothing.
			If the error = 10
				Do nothing.
			If the error = 11
				Do nothing.
			If the error = 12
				Do nothing.
			If the error = 13
				Do nothing.
			If the error = 14
				Do nothing.
			If the error = 255, it means that the value from the physical sensor has not been update.
				Do not need to do anything.
			If the error code is not implement, raise an ValueError.
		If one of the parameters is None, return None.
		Whatever happens, either the method returns None or it raise an ValueError.

		"""
		if None in (self, id, distance, error):
			return

		if int(id) == self["ID"]:
			if int(error) == 0: # No error. -> update the _history list (remove the oldest value and put the new one at the index 0. Finally, update the _distance attribute with the _history's mean.
				getattr(self, "_history").pop()
				object.__setattr__(self, "_history", [float(distance)] + getattr(self, "_history"))
				object.__setattr__(self, "_distance", mean(getattr(self, "_history")))
				return
			if int(error) == 1:	# Sigma fail.
				return
			if int(error) == 2:	# Signal fail.
				return
			if int(error) == 3:	# Target to close -> update the _history list (remove the oldest value and put a 0 value at the index 0. Finally, update the _distance attribute with the _history's mean.
				getattr(self, "_history").pop()
				object.__setattr__(self, "_history", [0] + getattr(self, "_history"))
				object.__setattr__(self, "_distance", mean(getattr(self, "_history")))
				return
			if int(error) == 4:	# Phase out of valid limits -  different to a wrap exit.
				return
			if int(error) == 5:	# Hardware fail.
				return
			if int(error) == 6:	# The Range is valid but the wraparound check has not been done.
				return
			if int(error) == 7:	# Wrapped target - no matching phase in other VCSEL period timing.
				return
			if int(error) == 8:	# Internal algo underflow or overflow in lite ranging.
				return
			if int(error) == 9:	# Specific to lite ranging.
				return
			if int(error) == 10:	# 1st interrupt when starting ranging in back to back mode. Ignore data.
				return
			if int(error) == 11:	# All Range ok but object is result of multiple pulses merging together.
				return				# Used by RQL for merged pulse detection
			if int(error) == 12:	# Used  by RQL  as different to phase fail.
				return
			if int(error) == 13:	# User ROI input is not valid e.g. beyond SPAD Array.
				return
			if int(error) == 14:	# lld returned valid range but negative value !
				return
			if int(error) == 255:	# No Update. -> Do nothing.
				return
			raise ValueError("'write' method in 'IRSensor' class does not implement error = " + str(error))


	def __repr__(self):
		"""Return a str which indicates the class of the object and the value of his attributes."""
		return "<Class = IRSensor, ID = " + str(self["ID"]) + \
		", History = " + str(getattr(self, "_history")) + \
		", Distance = " + str(self["distance"]) + ">"

	def __str__(self):
		"""Return a str which indicates the value of the _distance attribute only."""
		return str(self["distance"])


__all__ = ["IRSensor"]


if __name__ == "__main__":
	try:
		test = IRSensor(id = 0)
		print(
			repr(test), "\n",
			str(test), "\n"
		)

		while True:
			input_distance = float(input(">> "))
			test.write(
				id=test["ID"],
				distance=input_distance,
				error=0
			)
			print(
				repr(test), "\n",
				str(test), "\n"
			)

	except KeyboardInterrupt:
		pass

	finally:
		pass
