import numpy as np
from .info_reader import InfoReader


class FrameStream:

    def __init__(self, filename=None, gridfs=None):
        if filename:
            self.gridfs = None
            self.measurement_info = InfoReader.read_info_from_file(filename)
            self.filename = filename
            self.file_stream = open(filename)
            self.number_of_lines = 0
            self._nr_of_bytes_before_each_line_of_data = []
            self._nr_of_bytes_in_header = 0
            self._initialise_class_variables_from_file()
            self.time = self._read_time_from_file()
        elif gridfs:
            self.file_stream = None
            self.measurement_info = InfoReader.read_info_from_gridfs(gridfs)
            self.gridfs = gridfs
            self.number_of_lines = 0
            self._nr_of_bytes_before_each_line_of_data = []
            self._nr_of_bytes_in_header = 0
            self._initialise_class_variables_from_gridfs()
            self.time = self._read_time_from_gridfs()
        self.x_pixels = self.measurement_info['x pixels']
        self.y_pixels = self.measurement_info['y pixels']
        self.current_frame = 0

    def __iter__(self):
        for n in range(0, len(self.time)):
            intensity = self.get_intensity_from_line(n)
            yield self._reshape_line_of_intensity_to_a_frame(intensity)
        return

    def __getitem__(self, item):
        try:
            intensity = self.get_intensity_from_line(item)
            return self._reshape_line_of_intensity_to_a_frame(intensity)
        except TypeError:
            intensity = self.get_intensity_from_line(0)
            return self._reshape_line_of_intensity_to_a_frame(intensity)

    def __next__(self):
        return self.next()

    def next(self):
        if self.current_frame < len(self.time):
            current_frame, self.current_frame = self.current_frame, self.current_frame + 1
            return self.__getitem__(cur)
        else:
            raise StopIteration()

    def _reshape_line_of_intensity_to_a_frame(self, intensity):
        return np.reshape(intensity, (self.y_pixels, self.x_pixels))

    def get_frame_at_time(self, time):
        line_nr = self._find_index_of_nearest(self.time, time)
        intensity = self.get_intensity_from_line(line_nr)
        return np.reshape(intensity, (self.y_pixels, self.x_pixels))

    def _get_line_nr(self, nr):
        offset_in_bytes = self._nr_of_bytes_before_each_line_of_data[nr]
        if self.file_stream:
            self.file_stream.seek(offset_in_bytes)
            return self.file_stream.readline()
        elif self.gridfs:
            self.gridfs.seek(offset_in_bytes)
            return self.gridfs.readline().decode("utf-8")

    def _read_time_from_gridfs(self):
        time = []
        for nr_of_bytes in self._nr_of_bytes_before_each_line_of_data[:-1]:
            self.gridfs.seek(nr_of_bytes)
            t = self._extract_time_from_line(self.gridfs.readline().decode("utf-8"))
            time.append(t)
        return np.array(time)

    def _read_time_from_file(self):
        time = []
        for nr_of_bytes in self._nr_of_bytes_before_each_line_of_data[:-1]:
            self.file_stream.seek(nr_of_bytes)
            t = self._extract_time_from_line(self.file_stream.readline())
            time.append(t)
        return np.array(time)

    def _initialise_class_variables_from_gridfs(self):
        self.gridfs.seek(0)
        end_of_header_string = 'Time, Intensity:'
        is_in_header = True
        line = self.gridfs.readline()
        line_nr = 0
        while line is not b'':
            decoded_line = line.decode("utf-8")
            if is_in_header and end_of_header_string in decoded_line:
                self._nr_of_bytes_before_each_line_of_data.append(self.gridfs.tell())
                is_in_header = False
            elif not is_in_header:
                self._nr_of_bytes_before_each_line_of_data.append(self.gridfs.tell())
            line = self.gridfs.readline()
            line_nr += 1
        self.number_of_lines = line_nr - 1

    def _initialise_class_variables_from_file(self):
        byte_count = 0
        end_of_header_string = 'Time, Intensity:'
        is_in_header = True
        for line_nr, line in enumerate(self.file_stream):
            byte_count += bytes(line, encoding='utf-8').__sizeof__() - 33
            if is_in_header and end_of_header_string in line:
                self._nr_of_bytes_before_each_line_of_data.append(byte_count)
                is_in_header = False
                self.number_of_lines = line_nr + 2
            elif not is_in_header:
                self._nr_of_bytes_before_each_line_of_data.append(byte_count)
                self.number_of_lines = line_nr + 2

    @staticmethod
    def _extract_time_from_line(line):
        return float(line.split(',')[0])

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(np.array(array) - value)).argmin()

    def get_intensity_from_line(self, line_nr):
        line = self._get_line_nr(line_nr)
        return FrameStream._extract_intensity_from_line(line)

    @staticmethod
    def _extract_intensity_from_line(line):
        intensity_string = line.split(',')[1].split(';')[:-1]
        return np.array([float(i) for i in intensity_string])

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(np.array(array) - value)).argmin()
