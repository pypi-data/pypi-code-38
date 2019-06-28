from CrystalMatch.dls_imagematch.crystal.align import AlignedImages


class CrystalMatcherResults:
    """ Represents a pair of images with a set of crystal location matches between them. The client
    specifies a list of points in Image 1 which are to be matched in Image 2, and later supplies a
    transformation which calculates the point in Image 2 from that in Image 1. """
    def __init__(self, aligned_images):
        """ Initialize a new CrystalMatchSet object.

        Parameters
        ----------
        aligned_images - AlignedImages object, containing the two images to draw crystal matches between
        """
        if not isinstance(aligned_images, AlignedImages):
            raise TypeError("Argument must be instance of {}".format(AlignedImages.__name__))

        self._aligned_images = aligned_images
        self._matches = []

    def get_matches(self):
        return self._matches

    def append_match(self, crystal_match):
        self._matches.append(crystal_match)

    def num(self):
        """ The number of crystal matches in the set. """
        return len(self._matches)

    def get_crystal_match(self, index):
        """ Get a specific match object by index. """
        return self._matches[index]

    def image1(self):
        """ The first image; contains the user-selected crystal locations. """
        return self._aligned_images.image1

    def image2(self):
        """ The second image. """
        return self._aligned_images.image2

    def pixel_offset(self):
        """ The alignment offset between Image 1 and Image 2 (in pixels). """
        return self._aligned_images.pixel_offset()

    def real_offset(self):
        """ The alignment offset between Image 1 and Image 2 (in um). """
        return self._aligned_images.real_offset()
