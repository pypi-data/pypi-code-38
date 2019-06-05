import math

# standard

typeinfo = {	
	"Text": {"method": "Text"},
	"Term": {"method": "Text"},
	
	"String": {"method": "Field"},
	"List": {"method": "List"},
	"Fnum": {"method": "Fnum"},
	
	"Coord4": {"len": 6, "method": "Coord"},
	"Coord6": {"len": 8, "method": "Coord"},
	"Coord8": {"len": 10, "method": "Coord"},
	
	"Bit8":  {"len": 1, "method": "Bit"},
	"Bit16": {"len": 2, "method": "Bit"},
	"Bit24": {"len": 3, "method": "Bit"},
	"Bit32": {"len": 4, "method": "Bit"},
	"Bit40": {"len": 5, "method": "Bit"},
	"Bit48": {"len": 6, "method": "Bit"},
	"Bit56": {"len": 7, "method": "Bit"},
	"Bit64": {"len": 8, "method": "Bit"},
	
	"Int8":  {"len": 1, "method": "Int"},
	"Int16": {"len": 2, "method": "Int"},
	"Int24": {"len": 3, "method": "Int"},
	"Int32": {"len": 4, "method": "Int"},
	"Int40": {"len": 5, "method": "Int"},
	"Int48": {"len": 6, "method": "Int"},
	"Int56": {"len": 7, "method": "Int"},
	"Int64": {"len": 8, "method": "Int"}
}
	
class FieldType:
	def hasnorm (self, type):
		return type in ("Term", "Text")

	def isscorable (self, type):
		return self.hasnorm (type) or self.isfield (type) or self.islist (type)

	def isfield (self, type):
		return type == "String"
		
	def islist (self, type):
		return type == "List"
		
	def isbit (self, type):
		return type [:3] == "Bit"
	
	def isint (self, type):
		return type [:3] == "Int"
	
	def isextra (self, type):
		return type [:5] == "Coord"
	
	def iscoord (self, type):
		return type [:5] == "Coord"
			
	def valid (self, type):
		return type in typeinfo
	
	def getdelim (self):
		try:
			return typeinfo [type]["delim"]
		except KeyError:
			return
		
	def getsize (self, type):
		try:
			return typeinfo [type]["len"]
		except KeyError:
			return 0
	
	def getmethod (self, type):	
		if type.startswith ("Fnum"):
				return "Fnum"
		return typeinfo [type]["method"]
		
typemap = FieldType ()

def zfill (ftype, value):
	if type (value) is str:
		if value.find (".") != -1:
			try:
				value = float (value)
			except ValueError:	
				raise TypeError ('DOUBLEF Field allows float or int')							
					
		else:
			try:
				value = int (value)
			except ValueError:			
				raise TypeError ('DOUBLEF Field allows float or int')				
	
	fmt = "%%0%sf" % ftype[4:]
	val = fmt % value
	if val [0] == "-":
		val = "-0" + val [1:]
	return val
	