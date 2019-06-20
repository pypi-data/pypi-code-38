import zipfile
from StringIO import StringIO

class DKZipHelper:

    def __init__(self):
        pass

    @staticmethod
    def unzip_first_file_as_string(input_data):
        zip_raw_data = StringIO()
        zip_raw_data.write(input_data)
        the_zip_file = zipfile.ZipFile(zip_raw_data)
        info_list =the_zip_file.infolist()
        for item in info_list:
            filename = item.filename
            the_file = the_zip_file.open(filename)
            return the_file.read()
