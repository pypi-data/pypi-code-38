from PyPDF2 import PdfFileMerger


def merge(input_file_objs, output_file_obj, _pypdf2_import_bookmarks=False):
    merger = PdfFileMerger()
    for file_obj in input_file_objs:
        merger.append(file_obj, import_bookmarks=_pypdf2_import_bookmarks)

    merger.write(output_file_obj)

    merger.close()


__all__ = [
    'merge',
]
