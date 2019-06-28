from staplesremoval import staples_detector
from staplesremoval import  inpainting

def remove_staples(image):
    """Computes the reconstruction of an image computing previously the mask.

    Args:
      image: An RGB image.
    Returns:
      An RGB inpainted image.
    """
    colormask, mask = staples_detector.generate_mask(image)
    inpainted = inpainting.inpaint_from_mask(image, mask)
    return(inpainted)