import os
import sys
import glob
from os.path import dirname, abspath
import platform
from skimage.io import MultiImage
from PIL import Image
from pdf2image import convert_from_path


class ImgExtractor:

    def __pdfutil(self, file, output_path):
        """ this will extract text from  pdf file """

        if platform.system() == 'Windows':
            images = convert_from_path(file,
                                       poppler_path=dirname(abspath(__file__)) + os.sep + 'poppler' + os.sep + 'bin')
        else:
            images = convert_from_path(file)

        file_name = os.path.basename(file)

        for i, img in enumerate(images, start=1):
            path = output_path + os.sep + file_name + '_' + str(i) + ".jpg"
            img.save(path, 'JPEG')

    def __tifutil(self, file, output_path):
        """ this will extract text from tif images """
        file_name = os.path.basename(file)

        images = MultiImage(file, plugin='pil')

        for i, img in enumerate(images, start=1):
            pil_img = Image.fromarray(img)
            path = output_path + os.sep + file_name + '_' + str(i) + ".jpg"
            pil_img.save(path, 'JPEG')

    def extract(self, input_path, output_path, file_type):
        if file_type == 'TIF' or file_type == 'tif':

            files = glob.glob(input_path + "/*.TIF") + glob.glob(input_path + "/*.TIFF")
            ll = len(files)
            for i, file in enumerate(files, start=1):
                print(file, " is being extracted....")
                self.__tifutil(file, output_path)
                print(i, " of ", ll, " file(s) completed")
        elif file_type == 'PDF' or file_type == 'pdf':

            files = glob.glob(input_path + "/*.PDF")
            ll = len(files)
            for i, file in enumerate(files, start=1):
                print(os.path.basename(file), " is being extracted....")
                self.__pdfutil(file, output_path)
                print(i, " of ", ll, " file(s) completed")


if __name__ == "__main__":
    ss = ImgExtractor()
    ss.extract(sys.argv[1], sys.argv[2], sys.argv[3])
