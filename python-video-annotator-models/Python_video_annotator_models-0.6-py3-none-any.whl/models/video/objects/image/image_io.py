import os, cv2
from send2trash import send2trash
from pythonvideoannotator_models.models.video.objects.image.image_base import ImageBase

class ImageIO(ImageBase):

	FACTORY_FUNCTION = 'create_image'

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	def save(self, data, image_path):
		data = super(ImageIO, self).save(data, image_path)

		filepath = os.path.join(image_path, self.name+'.png')
		cv2.imwrite(filepath, self.image)

		return data

	def load(self, data, image_path):
		data = super(ImageIO, self).load(data, image_path)

		filepath = os.path.join(image_path, self.name+'.png')
		
		self.image = cv2.imread(filepath)
		return data