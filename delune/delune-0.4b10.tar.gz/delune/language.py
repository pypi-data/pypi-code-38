try:
	import pycld2 as cld2
	
except ImportError:
	def detect (text):
		raise SystemError ("pycld2 is not installed, use pip install pycld2")
		
else:	
	def detect (text):
		detected = cld2.detect (text)	
		if detected [0] is False:
			return None
		else:
			return detected [2][0][1]

