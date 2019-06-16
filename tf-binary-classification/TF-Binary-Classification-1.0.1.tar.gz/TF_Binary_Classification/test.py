import cv2
import tensorflow as tf
import argparse
import time
import cv2
import argparse
def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-c1", "--cat1", help="catagory1 same as test", type=str, default="FALSE", nargs=1)
	parser.add_argument("-c2", "--cat2", help="catagory2 same as test", type=str, default="TRUE",nargs=1)
	parser.add_argument("-p", "--path", help="add test data path", type=str, nargs=1)
	args = parser.parse_args()
	DATADIR1 = args.path
	DATADIR=DATADIR1[0]
	DATADIR=DATADIR + "/*jpg"
	CATEGORIES= []
	x=args.cat1
	CATEGORIES.append(x[0])
	x=args.cat2
	CATEGORIES.append(x[0])
	print(DATADIR)
	model = tf.keras.models.load_model("64x3-CNN.model")

	def final_test():
		def prepare(test_dir):
			IMG_SIZE = 64  # 50 in txt-based
			img_array = cv2.imread(test_dir, cv2.IMREAD_GRAYSCALE)  # read in the image, convert to grayscale
			new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))  # resize image to match model's expected sizing
			return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)  # return the image with shaping that TF wants.

		
		import glob

		images = glob.glob(DATADIR)

		for i in images:
			prediction = model.predict([prepare(i)]) # will be a list in a list.
			print(CATEGORIES[int(prediction[0][0])])

	final_test()
if __name__=="__main__":
	main()