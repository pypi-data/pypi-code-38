""" Exported Compressed File api
"""
from core_exporters_app.components.exported_compressed_file.models import ExportedCompressedFile


def get_by_id(exported_compressed_file_id):
    """ Gets Exported compressed file with the given id

    Args:
        exported_compressed_file_id: id

    Returns:

    """
    return ExportedCompressedFile.get_by_id(exported_compressed_file_id)


def upsert(exported_compressed_file):
    """ Saves or updates the file

    Args:
        exported_compressed_file:

    Returns:

    """
    return exported_compressed_file.save()
