import os, base64, numpy as np
from pythonvideoannotator_models.models.video.objects.object2d.datasets.contours.contours_base import ContoursBase

class ContoursIO(ContoursBase):

	FACTORY_FUNCTION = 'create_contours'

	def save(self, data, dataset_path=None):
		data = super(ContoursIO, self).save(data, dataset_path)

		contours_file = os.path.join(dataset_path, 'contours.csv')
		with open(contours_file, 'wb') as outfile:
			outfile.write((';'.join(['frame','contour','shape'])+'\n').encode( ))
			for index in range(len(self)):
				contour = self.get_contour(index)
				angle   = self.get_angle(index)
				row = [index] + ([None, None] if contour is None else [base64.b64encode(contour), contour.shape, angle])
				outfile.write((';'.join( map(str,row) )).encode( ))
				outfile.write(b'\n')

		data['color'] = self.color

		return data

	def load(self, data, dataset_path=None):
		data = super(ContoursIO, self).load(data, dataset_path)

		contours_file = os.path.join(dataset_path, 'contours.csv')
		
		if os.path.exists(contours_file):
			with open(contours_file, 'rb') as infile:
				infile.readline()
				for i, line in enumerate(infile):
					csvrow = line[:-1].split(b';')
					
					if csvrow[1] is None or csvrow[2] is None: 		continue
					if len(csvrow[1])==0 or len(csvrow[2])==0: 		continue
					if csvrow[1] == b'None' or csvrow[2] == b'None': continue
					
					frame = int(csvrow[0])
					shape = eval(csvrow[2])
					angle = eval(csvrow[3]) if len(csvrow)>3 else None
					
					contourbytes = eval(csvrow[1])
					if contourbytes is not None:
						buf = base64.b64decode(contourbytes)
						contour = np.frombuffer(buf, np.int32)
						contour = contour.reshape(shape)
						self.set_contour(frame, contour, angle)
					else:
						self.set_contour(frame, None, None)

		self.color = data.get('color', self.color)

		return data