from CrystalMatch.dls_focusstack.focus.fourier import Fourier
from CrystalMatch.dls_focusstack.focus.pointfft import PointFFT

class PointFFTManager:
    """
    Initialise z new PointFFTManager object.
    :param fftimages: list of fftimages
    :param match: single point match result
    :param z_level_region_size: size of region used in pointfft
    """
    def __init__(self, fftimages, point, z_level_region_size):
        self.images = fftimages
        self.point = point
        self.region_size = z_level_region_size

    def find_z_level_for_point(self):
        if self.images is not None:
            fftpois = []
            for image in self.images:
                pointfft = PointFFT(self.point, image.get_image(), self.region_size)
                square = pointfft.crop_region_from_image()
                level = Fourier(square).runFFT()
                pointfft.setFFT(level)
                pointfft.set_image_number(image.get_image_number())
                pointfft.set_image_name(image.get_image_name())
                fftpois.append(pointfft)
            max_poi =  max(fftpois, key=lambda fftpoint: fftpoint.getFFT())
            return max_poi.get_image_number()
