from staplesremoval import staples_detector
from staplesremoval import  inpainting

def remove_staples(image):
    colormask, mask = staples_detector.generate_mask(image)
    inpainted = inpainting.inpaint_from_mask(image, mask)
    return(inpainted)