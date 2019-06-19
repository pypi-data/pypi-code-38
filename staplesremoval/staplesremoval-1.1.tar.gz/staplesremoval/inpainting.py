from softcolor.morphology import MorphologyInCIELab, soften_structuring_element
from skimage.morphology import disk
from skimage import img_as_float
import numpy

def inpaint_from_mask(image,mask):
    morphology = MorphologyInCIELab()
    se = disk(1).astype('float64')

    se[se == 0] = numpy.nan

    image_with_nans = generate_image_with_nans(image,mask)
    image_inpainted, img_inpainted_steps = morphology.inpaint_with_steps(image_with_nans,
                                                                       structuring_element=se,
                                                                       max_iterations = 100)

    return image_inpainted

def generate_image_with_nans(image,mask):
    image_size = image.shape
    image_with_nans = img_as_float(image.copy())
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            if (mask[i,j] == True):
                image_with_nans[i, j, 0] = numpy.nan
                image_with_nans[i, j, 1] = numpy.nan
                image_with_nans[i, j, 2] = numpy.nan

    return(image_with_nans)

