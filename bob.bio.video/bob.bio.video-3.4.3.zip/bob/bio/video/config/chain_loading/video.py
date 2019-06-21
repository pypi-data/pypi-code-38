try:
    preprocessor
    from bob.bio.video.preprocessor import Wrapper
    preprocessor = Wrapper(preprocessor)
except NameError as e:
    pass
try:
    extractor
    from bob.bio.video.extractor import Wrapper
    extractor = Wrapper(extractor)
except NameError as e:
    pass
try:
    algorithm
    from bob.bio.video.algorithm import Wrapper
    algorithm = Wrapper(algorithm)
except NameError as e:
    pass
try:
    annotator
    from bob.bio.video.annotator import Wrapper
    annotator = Wrapper(annotator)
except NameError as e:
    pass
