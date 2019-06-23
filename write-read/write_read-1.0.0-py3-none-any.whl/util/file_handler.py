class FileHandler:
	def __init__(self,filename):
		self.filename = filename

	def read(self):
		fread = open(self.filename, 'r')
		return fread.read()

	def write(self, filedata):
		fwrite = open(self.filename, 'w')
		fwrite.write(' '.join(filedata))

