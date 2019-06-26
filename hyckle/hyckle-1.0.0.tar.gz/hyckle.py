import base64
import fileinput
import gzip
import linecache
import lzma
import os
import pickle

__version__ = '1.0.0'
__git__ = 'https://github.com/zylo117/hyckle'


class Hyckle:
    def __init__(self, filepath, compression='gzip', buffer_size=16, ignore_data_corruption=False):
        """
        A high-level warpper of pickle that provides data serialization for all python-pickleable object
        with the support of local read & write, better compression (approximately 50%-60% filesize smaller than original pickle @ default)
        and more memory-friendly.

        一个pickle的高层封装，可以为所有可pickle的python变量提供数据序列化，
        同时支持局部读写，拥有更好的压缩率（文件大小在默认模式下比原生pickle小了约50%-60%）,
        并更节省内存。

        :param filepath: str
        :param compression: use str 'gzip' or int 0~9 to use gzip with 0-9 compression level (recommended),
                            or use str 'lzma' for better compression but much slower,
                            use None to disable compression.

                            Noted: if hyckle existed, it will force using the existed compression method
        :param buffer_size: int, flush to disk every k data input.
        :param ignore_data_corruption: bool
        """
        assert compression in ['gzip', 'lzma', None] or isinstance(compression, int)

        self.keys = []
        self.ttl_counter = 0
        self.current_counter = 0
        self.buffer = {}
        self.permanent_removed = []
        self.buffer_size = buffer_size
        self.filepath = filepath
        self.ignore_data_corruption = ignore_data_corruption

        self._set_compression(compression)

        if not os.path.exists(self.filepath):
            # create hyckle if not exists, and write title
            self._create_hyckle(compression)
        else:
            with open(self.filepath) as f:
                title = f.readline().strip()
                if title == '':
                    self._create_hyckle(compression)
                else:
                    print('[INFO] loading previous data.')
                    title = title.split(',')
                    try:
                        self.current_version = title[1]
                        compression = title[-1]
                        if compression.isdigit():
                            compression = int(compression)
                    except:
                        raise Exception('[ERROR] unexpected/corrupted hyckle header.')

                    self._set_compression(compression)

                    # load previous data
                    self._load_lines(f.readlines())
                f.close()

        self.hyckle_handle = open(self.filepath, 'a+')

    def __len__(self):
        return len(self.keys)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_counter == self.ttl_counter:
            raise StopIteration
        else:
            obj = self.get(self.keys[self.current_counter])
            self.current_counter += 1
            return obj

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get(self.keys[item])
        elif isinstance(item, str):
            return self.get(item)
        elif isinstance(item, slice):
            return [self[i] for i in range(*item.indices(len(self)))]
        else:
            return None

    def _create_hyckle(self, compression):
        with open(self.filepath, 'w') as f:
            f.write('Hyckle,{},{},{}\n'.format(__version__, __git__, compression))
            f.close()
        self.current_version = __version__

    def _set_compression(self, compression):
        self.compression_level = 2
        self.compression_method = None
        if compression == 'gzip' or isinstance(compression, int):
            if isinstance(compression, int):
                if compression > 9:
                    self.compression_level = 9
                elif compression < 0:
                    self.compression_level = 0
                else:
                    self.compression_level = compression

            self.compression = gzip
            self.compression_method = 'gzip'

        elif compression == 'lzma':
            self.compression = lzma
            self.compression_method = lzma
        else:
            self.compression = None
            self.compression_method = None

    @staticmethod
    def _parse_line(line):
        """
        text line to hyckle element
        :param line:
        :return:
        """
        line = line.split(':')
        key, text = line[0], line[1]
        text = text.strip()
        return key, text

    def _encode(self, obj):
        """
        compress binary data and encode in base64 format, then decode to string
        :param bin_data: binary data
        :return:
        """
        bin_data = pickle.dumps(obj)
        if self.compression is not None:
            if self.compression_method == 'gzip':
                bin_data = self.compression.compress(bin_data, compresslevel=self.compression_level)
            else:
                bin_data = self.compression.compress(bin_data)
        text = base64.encodebytes(bin_data).decode()
        text = text.replace('\n', '')  # remove redundant and confusing \n from base64 string
        return text

    def _decode(self, text):
        bin_data = text.encode()
        bin_data = base64.decodebytes(bin_data)
        if self.compression is not None:
            bin_data = self.compression.decompress(bin_data)

        obj = pickle.loads(bin_data)
        return obj

    def _load_lines(self, lines):
        """
        load lines to hyckle
        :param lines:
        :return:
        """
        for line in lines:
            line = line.strip()
            try:
                key, text = self._parse_line(line)

                self.keys.append(key)
                self.ttl_counter += 1
            except IndexError:
                if self.ignore_data_corruption:
                    pass
                else:
                    raise Exception('[ERROR] unexpected/corrupted data format.')

    def _mod_line(self, key, new_line):
        # TODO: this algorithm is a little expensive, could be optimized.
        # close hyckle handle for modification
        self.close()
        idx = self.keys.index(key) + 1
        handle = fileinput.input(self.filepath, inplace=True)
        for line_idx, line in enumerate(handle):
            if line_idx == idx:
                if new_line == '<REMOVED>':
                    continue
                else:
                    print(new_line.strip())
            else:
                print(line.strip())
        # reopen hyckle handle after modification
        self.hyckle_handle = open(self.filepath, 'a+')

    def _get_line(self, key):
        if key in self.buffer:
            line = self.buffer[key]
        else:
            line = linecache.getline(self.filepath, self.keys.index(key) + 2)
            if line == '':
                linecache.updatecache(self.filepath)
                line = linecache.getline(self.filepath, self.keys.index(key) + 2)
        return line

    def add(self, key: str, obj):
        """
        use hyckle as a dict
        :param key: str.
        :param obj:
        :return:
        """

        if not isinstance(key, str):
            UserWarning('[WARNING] key {} will force-cast to str type'.format(key))
            print('[WARNING] key {} will force-cast to str type'.format(key))
            key = repr(key)

        new_line = self._encode(obj)
        new_line = '{}:{}\n'.format(key, new_line)

        if key not in self.keys:
            self.buffer[key] = new_line

            # record
            self.keys.append(key)
            self.ttl_counter += 1
        else:
            # if key existed and its data is different, replace data that has been written to disk
            old_line = self._get_line(key)
            if new_line != old_line:
                self._mod_line(key, new_line)

        # flush to disk if buffer is full
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def append(self, obj):
        """
        use hyckle as a list, but eventually a dict.
        :param obj:
        :return:
        """
        key = str(self.ttl_counter)
        self.add(key, obj)

    def flush(self):
        self.hyckle_handle.writelines(self.buffer.values())

        # make sure write to disk
        self.hyckle_handle.flush()

        # clear queue
        self.buffer = {}

    def get(self, key):
        line = self._get_line(key)

        key, text = self._parse_line(line)
        obj = self._decode(text)

        return obj

    def remove(self, key):
        if key in self.buffer:
            self.buffer.pop(key)
        else:
            self._mod_line(key, '<REMOVED>')
            self.keys.remove(key)
            self.ttl_counter -= 1

    def close(self):
        self.flush()
        self.hyckle_handle.close()
