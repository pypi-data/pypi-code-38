from ..imports import *
from ..imaging import visualize, io, simulations
from ..utilities import mkdir

directory = 'examples'
mkdir(directory)

def cartoon_rgb():
    x, y = np.meshgrid(np.linspace(0, 1, 1000), np.linspace(0, 1, 500))
    r = x
    g = y
    b = np.random.uniform(0, 1, r.shape)
    return r, g, b

def test_io():
    '''
    This tests the tools for reading and writing images.
    '''
    # create a test image
    xsize, ysize = 200, 100
    x = np.arange(xsize)
    image = np.random.uniform(0, 1.0, (ysize, xsize))
    rgb = io.compile_rgb(*cartoon_rgb())
    for suffix in ['jpg', 'png', 'gif']:
        filename = os.path.join(directory, 'image-gray.{}'.format(suffix))
        io.write_image(image, filename=filename)
        gray = io.read_gray(filename)
        r, g, b = io.read_rgb(filename)
        filename = os.path.join(directory, 'image-rgb.{}'.format(suffix))
        io.write_image(rgb, filename=filename)
        r, g, b = io.read_rgb(filename)

def test_rgb():
    r, g, b = cartoon_rgb()
    visualize.display_rgb(r, g, b)
