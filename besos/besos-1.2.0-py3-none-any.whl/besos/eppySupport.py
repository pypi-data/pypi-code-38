import os
from eppy import modeleditor
from eppy.modeleditor import IDF
from eppy.results import readhtml
import inspect
import subprocess

def listify_idf_objects(idf: IDF, objects: list):
	"""	listify_idf_objects(IDF, list)

		Takes the passed idf, and grabs the objects out of it
		that are specified in objects

		idf(IDF): The idf to grab the objects from
		objects(list): A list generated from a yaml file
			       that specifies how and what to read
			       from the idf file
	"""
	objects_list = []

	#: For every set of object information in objects, and for
	#: every attribute in that object, check if it's in the variables
	#: dictionary, and if it is, and its a float, then append it to
	#: objects_list
	for objectset in objects:

		#: If the name of the object is "Run_Parameters", then its
		#: not an object, its actually something in the config file
		#: used to setup some run inputs.
		if objectset[0] == "Run_Parameters":
			continue

		#: Get the idf object from the idf based off its name (objectset[0])
		current_object = get_idfobject_from_name(idf, objectset[0])

		#: Loop through the attributes and check if both the attribute
		#: is in the Variables dictionary, and that it's float
		for attribute in current_object.fieldnames:
			#: Catch value errors to check if attributes are floats.
			try:
				#: Check that the attribute is in the Variables dictionary,
				#: if its not, raise a ValueError to move on.
				if attribute not in objectset[1]["Variables"]:
					raise ValueError

				#: Store a float of the attribute (if it cannot
				#: be converted to a float, then it will raise a
				#: ValueError, and move on.
				val = float(getattr(current_object, attribute))

				#: Append the value to the objects_list
				objects_list.append(val)

			#: Except the ValueError, and pass
			except ValueError as e:
				pass

	#: Return the list of objects
	return objects_list

def rebuild_idf(idd_path: str, idf_path: str, epw_path: str, w_objects: list, build_list: list):
	"""	rebuild_idf(IDF, list, list)

		Builds an idf based off of a passed config file, and
		a list of values that was passed.

		Args:
			idd_path(str):	The absolute path to the idd file to be run.

			idf_path(str):	The absolute path to the idf file to be run.

			epw_path(str):	The absolute path to the epw file to be run.

			w_objects(list):	A list generated from a yaml file
						that specifies how and what to read
						from the idf file

			build_list(list):	A list of values which will be assigned to
						values in objects in the idf.
	"""

	#: Get an idf object from the passed idd, idf, and epw
	idf = create_idf_object(idd_path, idf_path, epw_path)
	i = 0

	#: For every set of object information in w_objects,
	#: and for every attribute in the object described if that attribute
	#: is in the Variables dictionary, and the attribute is a float, AND the
	#: value for this entry in build_list is between the max and min values
	#: described in the object's information then set the attribute to the
	#: value in build_list. (Note, the first object's first valid field is
	#: equivellant to the first item in build_list, the second field to the
	#: second item in build_list, etc)
	for object in w_objects:

		#: If the name of the object is "Run_Parameters", then
		#: this is not an idf object, it's an informatic field
		#: from the config, so ignore it.
		if object[0] == "Run_Parameters":
			continue

		#: Get the object from the idf based off its name (object[0] holds
		#: the name of the object)
		current_object = get_idfobject_from_name(idf, object[0])

		#: For each attribute in the object, check if the attribute is a
		#: float, and check that the value that the attribute that is to be
		#: set to is within the range given, and if both are true, then set
		#: the attribute to that value
		for attribute in current_object.fieldnames:

			#: Try catch block to catch ValueErrors that float(getattr) raises
			#: if the attribute is not a float (to check if the attribute is float)
			try:
				#: Check if the attribute is in the Variables dictionary
				#: and if its not, raise a ValueError to skip this attribute.
				if attribute not in object[1]["Variables"]:
					raise ValueError

				#: Attempt to get the attribute to check if its a float or not.
				val = float(getattr(current_object, attribute))

				#: If we should check max/mins
				if dict(w_objects)["Run_Parameters"][1]:

					#: If the attribute has specific max/mins,
					#: then check if its within those limits
					if attribute in object[1].keys():

						#: If the value is less than the min
						if build_list[i] < float(object[1][attribute][1]):

							#: return None as this idf is invalid
							return None

						#: If the value is more than the max
						elif build_list[i] > float(object[1][attribute][0]):

							#: return None as this idf is invalid
							return None

					#: Otherwise check it against the defaults
					else:

						#: If the value is less than the default min
						if build_list[i] < float(object[1]["Default"][1]):

							#: return None as this idf is invalid
							return None

						#: If the value is more than the default max
						elif build_list[i] > float(object[1]["Default"][0]):

							#: return None as this idf is invalid
							return None

				#: If we get to this point, then the attribute is valid, and the
				#: value is valid, so set the attribute to that value
				setattr(current_object, attribute, round(build_list[i], 2))

				#: Add 1 to i, so that we can assign the next value to the next
				#: attribute
				i += 1

			#: Except ValueErrors incase the attribute is not a float, or it is not in Variables
			except ValueError as e:
				for key, value in object[1]["Abstracts"].items():
					if attribute == key:
						print(attribute, " ==> ", value)
						setattr(current_object, attribute, round(value, 2))

	#: Return the idf with all the new attributes.
	return idf

def get_idfobject_from_name(idf: IDF, name: str):
	"""	get_idfobject_from_name(IDF, str)

		Gets an object from the passed idf where it's name
		value is equal to the passed string, if none are found
		then this method returns None

		Args:
			idf(IDF): The idf to find the object from.
			name(str): The string to find that is equal to the
				   name field of the object.
	"""

	#: For every object in the idf.
	for idfobject in idf.idfobjects:

		#: For field in this object
		for object in idf.idfobjects[idfobject]:

			#: Try except block incase object does not
			#: have a .Name attribute
			try:
				#: If object.Name == name, then return
				#: the object, as that is the object
				#: we're looking at.
				if object.Name == name:
					return object

			#: Move on to the next object if an exception is
			#: raised.
			except:
				pass

	#: If this is enocuntered then no match was found, so we return None.
	return None

def create_idf_object(idd: str, idf: str, epw: str):
	"""	create_idf_object(str, str, str)

		Returns an idf object generated from the passed
		idd, idf, and epw

		Args:
			idd(str): The directory to the idd
			idf(str): The directory to the idf
			epw(str): The directory to the epw
	"""

	#: Try to set the idd attribute for the IDF class.
	try:
		IDF.setiddname(idd)
	except:
		pass

	#: Create an idf object based off the passed idf and epw.
	idf = IDF(idf, epw)

	#: return the created idf object
	return idf

def printErr(msg: str):
	""" 	printErr(str)

		Prints the message in an error red on unicode supported
		consoles.

		Args:
			msg(str): The string to print
	"""
	#: print(red_colour + msg + end_colour)
	print('\033[91m' + msg + '\033[0m')

def printSuccess(msg: str):
	""" 	printSuccess(str)

		Prints the message in a success green on unicode supported
		consoles.

		Args:
			msg(str): The string to print
	"""
	#: print(green_colour + msg + end_colour)
	print('\033[92m'  + msg + '\033[0m')

def get_energy_usage(idf: IDF, obj_list= None) -> float:
	"""	get_energy_usage(IDF, list)

		Runs an idf, and extracts the building's energy usage
		from that run.

		Args:
			idf(IDF): The idf to be run.
			obj_list(list): ONLY USED IF VERBOSE IS TRUE FOR
					DEBUGGING PURPOSES. This variable
					prints the final state of each of
					the idf's objects that are being
					changed.
	"""

	#: Verbose is used to help debug, when true it prints
	#: additional information about each run.
	verbose = False

	#: Try to run the idf. If an error is caught during this execution
	#: then the idf is unrunable, and we will return an energy usage of inf
	try:

		#: Run the idf. if Verbose is False, then we log that we're running
		#: the idf, and when it's finished, but we suppress the output from
		#: the idf's actual run. If verbose is True, we instead run the idf
		#: without suppressing its objectives
		if not verbose:
			print("Running idf...")
			idf.run(verbose='q') #: verbose='q' suppresses objectives
			printSuccess("Done.")
		else:
			idf.run()
	except:
		#: If an exception is raised, then print that we failed to run
		#: the idf, and return inf. NOTE, if verbose is true, we will also
		#: print all of the objects being looked at, so that we can analize
		#: why the idf is unrunable
		printErr("Failed to run idf. Is it valid?")
		if verbose == True and obj_list is not None:
			for object in obj_list:
				print(get_idfobject_from_name(idf, object[0]))

		#: return inf
		return float("inf")

	#: Create a variable to hold the sum of the energy used.
	energy_used = 0.0

	#: Open the meter file to read what the energy usages were.
	with open("eplusout.mtr", 'r') as filestring:

		#: Read all the lines in the file, and split them into seperate string
		#: in a list. This way we can analize each line seperately.
		strings = filestring.read().split('\n')
		for line in strings[35:]:

			#: If the line has the id 13 (ie the first entry is 13) then
			#: this is one of the objectives we want to look at, so grab the
			#: float value from the line (which will be in the second
			#: position of the csv) and read it as a float. Add that float
			#: to the total energy used.
			if line[:3] == "13,":
				energy_used += float(line[3:line[3:].find(',')])

			#: If the line has the id 274 (ie the first entry is 274) then
			#: this is one of the objectives we want to look at, so grab the
			#: float value from the line (which will be in the second
			#: position of the csv) and read it as a float. Add that float
			#: to the total energy used.
			elif line[:4] == "274,":
				energy_used += float(line[4:line[4:].find(',')])

	#: Return the total amount of energy used.
	return energy_used



def main():
	""" 	main()

		This method will not be documented as it is not meant to be run. This method is used
		for debugging and testing only, and thus it may change from commit to commit without
		any mention.
	"""
	IDF.setiddname("EP.idd")
	idf = IDF("input.idf", "t.epw")
	myWindow = idf.idfobjects['FENESTRATIONSURFACE:DETAILED']
	for window in myWindow:
		print(window)
	exit()

	print(get_idfobject_from_name(idf, "Perimeter_ZN_3_wall_north_Window_6"))

	energies_used = []
	min_height = 0.91
	denom = 100

	for i in range(200, -1, -1):
		idf.idfobjects['FENESTRATIONSURFACE:DETAILED'][0].Vertex_1_Zcoordinate = round(min_height + (i / denom), 2)
		idf.idfobjects['FENESTRATIONSURFACE:DETAILED'][0].Vertex_4_Zcoordinate = round(min_height + (i / denom), 2)

		print("Running with window height {}".format(round(min_height + (i/denom), 2)))
		energies_used.append((round(min_height + (i / denom), 2), get_energy_usage(idf)))

	energies_used = sorted(energies_used, key= lambda x: x[1])

	for index, use in enumerate(energies_used):
		print("{}th  best solution has window height {}".format(index + 1, use[0]), end='\n\t')
		print(use[1])

	print("Best window size is: ", end='\n\t')
	print(min(energies_used, key=lambda x: x[1]))


if __name__ == "__main__":
	main()
