from rhythmic.general import faultReturnHandler;
from zipfile import ZipFile, ZIP_DEFLATED;

@faultReturnHandler
def packFiles(folder_path, archive_absolute_path, files_list):
    """
    packFiles(folder_path, archive_absolute_path, files_list)

    folder_path - a folder scanned with folder_scan.scanModelFolder to get files_list;
    files_list - a list of dictionaries, containing "file_path" items: {"file-path": path [,... ]}

    """
    relative_index = len(folder_path) + 1;

    with ZipFile(archive_absolute_path, compression = ZIP_DEFLATED, mode = 'w') as version_zip:

        for item in files_list:
            version_zip.write(item["file_path"], item["file_path"][relative_index:]);

    return "[ {} ] packed to [ {} ]".format(folder_path, archive_absolute_path);