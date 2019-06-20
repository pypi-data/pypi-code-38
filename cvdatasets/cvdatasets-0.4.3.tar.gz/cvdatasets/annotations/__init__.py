from .cub import CUB_Annotations
from .nab import NAB_Annotations
from .cars import CARS_Annotations
from .inat import INAT19_Annotations
from .flowers import FLOWERS_Annotations
from .dogs import DOGS_Annotations
from .hed import HED_Annotations

from .base import BaseAnnotations

from cvargparse.utils import BaseChoiceType
from functools import partial

class AnnotationType(BaseChoiceType):
	CUB200 = CUB_Annotations
	CUB200_2FOLD = partial(CUB_Annotations)
	NAB = NAB_Annotations
	CARS = CARS_Annotations
	DOGS = DOGS_Annotations
	FLOWERS = FLOWERS_Annotations
	HED = HED_Annotations

	INAT19 = INAT19_Annotations
	INAT19_MINI = partial(INAT19_Annotations)
	INAT19_TEST = partial(INAT19_Annotations)

	Default = CUB200
