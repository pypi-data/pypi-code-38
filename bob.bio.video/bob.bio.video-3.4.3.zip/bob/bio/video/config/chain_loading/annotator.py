try:
    annotator
    from bob.bio.video.annotator import Wrapper
    annotator = Wrapper(annotator)
except NameError as e:
    print("This configuration is meant to be used in chain loading of "
          "configuration files. Please see the documentation of "
          "bob.extension for chain loading.")
    raise e
