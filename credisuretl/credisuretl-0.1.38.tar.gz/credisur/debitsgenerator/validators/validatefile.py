import os
from .errorsiterator import ErrorsIterator

def validate_file(excel_path):
    errors = ErrorsIterator()
    if not os.path.isfile(excel_path):
        errors.add_error("El archivo %s no existe." % (excel_path))

    return errors
