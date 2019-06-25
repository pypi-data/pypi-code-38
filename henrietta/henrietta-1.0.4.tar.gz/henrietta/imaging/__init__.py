try:
    from .simulations import *
except ImportError:
    print("""
    The image input/output tools were not loaded, probabaly because
    astroquery is unavailable. Try running `pip install astroquery` to
    install it.
    """)

try:
    from .visualize import *
except ImportError:
    print("""
    The image input/output tools were not loaded, probabaly because
    illumination is unavailable. Try running `pip install illumination`
    to install it.
    """)

try:
    from .io import *
except ImportError:
    print("""
    The image input/output tools were not loaded, probabaly because
    skimage is unavailable. Try running `pip install skimage` to
    install it.
    """)
