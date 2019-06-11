# Python 2 to 3 changed the use of __init__.py
# To avoid namespace problems use this for 2 and 3 compatibility
# https://packaging.python.org/namespace_packages/?highlight=__init__
# Otherwise omit __init__.py entirely unless you have sub-packages

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

# from .project_quickstart import project_quickstart
# from .project_quickstart import projectQuickstart
