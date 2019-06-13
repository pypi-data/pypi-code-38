
import codecs
import os

from pysp.sbasic import SFile, SStamp


class STextFile(SFile):
    SPLIT_FILE_FORMAT = '{fname}-{idx:03d}.{ext}'
    EOL = '\r\n'

    def __init__(self, path):
        apath = path.split('.')
        self.fname = '.'.join(apath[:-1])
        self.ext = apath[-1]
        self.split_index = 0
        self.open_file(path)

    def __del__(self):
        if self.fd:
            self.fd.close()

    def generate_file_name(self, increment=0):
        self.split_index += increment
        return self.SPLIT_FILE_FORMAT.format(
                fname=self.fname, idx=self.split_index, ext=self.ext)

    def open_file(self, fname):
        self.mkdir(os.path.dirname(fname))
        self.curname = fname
        self.fd = codecs.open(fname, 'w', encoding='utf-8')

    def split_file(self, callback=None):
        self.fd.close()
        if self.split_index == 0:
            rename = self.generate_file_name(0)
            os.rename(self.curname, rename)
        self.open_file(self.generate_file_name(1))
        if callback:
            callback()

    def writeln(self, string):
        self.fd.write(string+self.EOL)


class SCSV(STextFile):
    MAX_FIELD_COUNT = 100000
    APPEND_SUBTITLE = '{title} / continue {idx:03d}'

    def __init__(self, path, title, columns):
        super(SCSV, self).__init__(path)
        self.title = title
        # self.schema = schema
        self.columns = columns
        self.title = title
        self.field_index = 0
        self.blank_line = ','*len(columns)
        self._need_split = False
        self.write_header()
        # for col in columns:
        #     if col not in schema:
        #         emsg = 'Not exists {col} in schema.'.format(col=col)
        #         raise PyJoyousError(DTAG, emsg)

    def write_header(self):
        if self.field_index == 0:
            _title = self.title
        else:
            _title = self.APPEND_SUBTITLE.format(
                                title=self.title, idx=self.split_index)
        self.writeln(_title + self.blank_line[:-1])
        self.writeln(SStamp.now() + self.blank_line[:-1])
        self.writeln(','+','.join(self.columns))

    def column_to_str(self, value):
        if type(value) is str and value.find('\n') >= 0:
            return '"'+value+'"'
        return '"=""'+str(value)+'"""'

    def write_field(self, field, to_str=False):
        if self._need_split:
            self._need_split = False
            self.split_file(self.write_header)

        self.field_index += 1
        if (self.field_index % self.MAX_FIELD_COUNT) == 0:
            self._need_split = True
        ftext = str(self.field_index)
        for i, v in enumerate(field):
            if to_str:
                ftext += ','+self.column_to_str(v)
            elif type(v) is str and v.find('\n') >= 0:
                ftext += ','+'"'+v+'"'
            else:
                ftext += ','+str(v)
        self.writeln(ftext)
