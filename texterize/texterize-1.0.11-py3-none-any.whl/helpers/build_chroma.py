from PIL import Image
import math, numpy as np

#Converts an image to a scaled 3D RGB numpy array
def buildChroma(img_path, text_length):
    '''
    params:
    -img_path: the path to the image that the texterized image should be based on
    -text: A string containing the input text

    return:
    A tuple containing an N-by-N-by-3 numpy array containing the RGB values for each pixel of the given image and its shape
    '''
    try:
        img = Image.open(img_path)
        img_matrix = np.array(img.convert('RGB'))
    except:
        raise Exception(f"Could not open image {img_path}, aborting.")

    ORIG_WIDTH, ORIG_HEIGHT, _ = img_matrix.shape
    if ORIG_WIDTH * ORIG_HEIGHT < text_length:
        return img_matrix, img_matrix.shape

    SCALING_FACTOR = math.gcd(ORIG_WIDTH, ORIG_HEIGHT)
    img_width = int(ORIG_WIDTH / SCALING_FACTOR)
    img_height = int(ORIG_HEIGHT / SCALING_FACTOR)
    REDUCED_WIDTH = img_width
    REDUCED_HEIGHT = img_height
    while img_width * img_height < text_length:
        img_width += REDUCED_WIDTH
        img_height += REDUCED_HEIGHT

    img_compressed = img.thumbnail((img_width, img_height), Image.ANTIALIAS)
    img_matrix_compressed = np.array(img.convert('RGB'))
    return img_matrix_compressed, img_matrix_compressed.shape