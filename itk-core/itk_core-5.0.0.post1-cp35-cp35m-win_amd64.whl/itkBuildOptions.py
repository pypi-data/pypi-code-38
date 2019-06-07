
import itkTemplate
import itkTypes

DIMS = [int(s) for s in "2;3".split(";") if s]
USIGN_INTS = [getattr(itkTypes, s) for s in "UC;US".split(";") if s]
SIGN_INTS = [getattr(itkTypes, s) for s in "SS".split(";") if s]
REALS = [getattr(itkTypes, s) for s in "F".split(";") if s]

VECTOR_REALS = [itkTemplate.itkTemplate.__templates__[itkTemplate.normalizeName(s)] for s in "itk::Vector< float,2 >;itk::Vector< float,3 >".split(";") if s]
COV_VECTOR_REALS = [itkTemplate.itkTemplate.__templates__[itkTemplate.normalizeName(s)] for s in "itk::CovariantVector< float,2 >;itk::CovariantVector< float,3 >".split(";") if s]
RGBS = [itkTemplate.itkTemplate.__templates__[itkTemplate.normalizeName(s)] for s in "itk::RGBPixel< unsigned char >".split(";") if s]
RGBAS = [itkTemplate.itkTemplate.__templates__[itkTemplate.normalizeName(s)] for s in "itk::RGBAPixel< unsigned char >".split(";") if s]
COMPLEX_REALS = [itkTemplate.itkTemplate.__templates__[itkTemplate.normalizeName(s)] for s in "std::complex< float >".split(";") if s]


INTS = SIGN_INTS + USIGN_INTS
SCALARS = INTS + REALS
VECTORS = VECTOR_REALS + COV_VECTOR_REALS
COLORS = RGBS + RGBAS
ALL_TYPES = COLORS + VECTORS + SCALARS + COMPLEX_REALS

del itkTemplate
del itkTypes
