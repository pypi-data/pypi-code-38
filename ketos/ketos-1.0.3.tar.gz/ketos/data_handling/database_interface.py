# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" database_interface module within the ketos library

    This module provides functions to create and use HDF5 databases as storage for acoustic data. 
"""

import tables
import os
import ast
import math
import numpy as np
from ketos.utils import tostring
from ketos.audio_processing.audio import AudioSignal
from ketos.audio_processing.spectrogram import Spectrogram,MagSpectrogram,PowerSpectrogram, MelSpectrogram, ensure_same_length
from ketos.data_handling.data_handling import find_wave_files, AnnotationTableReader, rel_path_unix
from tqdm import tqdm

def open_table(h5file, table_path):
    """ Open a table from an HDF5 file.
        
        Args:
            h5file: tables.file.File object
                HDF5 file handler.
            table_path: str
                The table's full path.

        Raises: 
            NoSuchNodeError if table does not exist.

        Returns:
            table: table.Table object or None
                The table, if it exists. Otherwise, raises an exeption and returns None.

        Examples:
            >>> import tables
            >>> from ketos.data_handling.database_interface import open_table
            >>>
            >>> h5file = tables.open_file("ketos/tests/assets/15x_same_spec.h5", 'r')
            >>> data = open_table(h5file, "/train/species1")
            >>> #data is a pytables 'Table' object
            >>> type(data)
            <class 'tables.table.Table'>
            >>>
            >>> # with 15 items (rows)
            >>> data.nrows
            15
            >>> h5file.close()
        
    """
    try:
       table = h5file.get_node(table_path)
    
    except tables.NoSuchNodeError:  
        print('Attempt to open non-existing table {0} in file {1}'.format(table_path, h5file))
        raise
        table = None

    return table

def create_table(h5file, path, name, shape, max_annotations=10, chunkshape=None, verbose=False):
    """ Create a new table.
        
        If the table already exists, open it.

        Args:
            h5file: tables.file.File object
                HDF5 file handler.
            path: str
                The group where the table will be located. Ex: '/features/spectrograms'
            name: str
                The name of the table.
            shape : tuple (ints)
                The shape of the audio signal (n_samples) or spectrogram (n_rows,n_cols) 
                to be stored in the table. Optionally, a third integer can be added if the 
                spectrogram has multiple channels (n_rows, n_cols, n_channels).
            max_annotations: int
                Maximum number of annotations allowed for any of the items in this table.
            chunkshape: tuple
                The chunk shape to be used for compression

        Returns:
            table: table.Table object
                The created/open table.    

        Examples:

            >>> import tables
            >>> from ketos.data_handling.database_interface import create_table
            >>>
            >>> # Open a connection to the database
            >>> h5file = tables.open_file("ketos/tests/assets/tmp/database1.h5", 'w')
            >>> # Create 'table1' within 'group1'
            >>> my_table = create_table(h5file, "/group1/", "table1", shape=(64,20)) 
            >>> # Show the table description, with the field names (columns)
            >>> # and information about types and shapes
            >>> my_table
            /group1/table1 (Table(0,), fletcher32, shuffle, zlib(1)) ''
              description := {
              "boxes": StringCol(itemsize=421, shape=(), dflt=b'', pos=0),
              "data": Float32Col(shape=(64, 20), dflt=0.0, pos=1),
              "file_vector": UInt8Col(shape=(64,), dflt=0, pos=2),
              "files": StringCol(itemsize=100, shape=(), dflt=b'', pos=3),
              "id": StringCol(itemsize=25, shape=(), dflt=b'', pos=4),
              "labels": StringCol(itemsize=31, shape=(), dflt=b'', pos=5),
              "time_vector": Float32Col(shape=(64,), dflt=0.0, pos=6)}
              byteorder := 'little'
              chunkshape := (21,)
            >>>
            >>> h5file.close()
            
    """
    max_annotations = max(1, int(max_annotations))

    try:
       group = h5file.get_node(path)
    
    except tables.NoSuchNodeError:
        if verbose:
            print("group '{0}' not found. Creating it now...".format(path))
    
        if path.endswith('/'): 
            path = path[:-1]

        group_name = os.path.basename(path)
        path_to_group = path.split(group_name)[0]
        if path_to_group.endswith('/'): 
            path_to_group = path_to_group[:-1]
        
        group = h5file.create_group(path_to_group, group_name, createparents=True)
        
    try:
        table = h5file.get_node("{0}/{1}".format(path, name))
    
    except tables.NoSuchNodeError:    
        filters = tables.Filters(complevel=1, fletcher32=True)
        labels_len = 2 + max_annotations * 3 - 1 # assumes that labels have at most 2 digits (i.e. 0-99)
        boxes_len = 2 + max_annotations * (6 + 4*9) - 1 # assumes that box values have format xxxxx.xxx  
        descrip = table_description(shape=shape, labels_len=labels_len, boxes_len=boxes_len)
        table = h5file.create_table(group, "{0}".format(name), descrip, filters=filters, chunkshape=chunkshape)

    return table

def table_description(shape, id_len=25, labels_len=100, boxes_len=100, files_len=100):
    """ Create the class that describes the table structure for the HDF5 database.

        The columns in the table are described as the class Attributes (see Attr section below)
             
        Args:
            shape : tuple (ints)
                The shape of the audio signal (n_samples) or spectrogram (n_rows,n_cols) 
                to be stored in the table. Optionally, a third integer can be added if the 
                spectrogram has multiple channels (n_rows, n_cols, n_channels).
            id_len : int
                The number of characters for the 'id' field
            labels_len : int
                The number of characters for the 'labels' field
            boxes_len : int
                The number of characters for the 'boxes' field
            files_len: int
                The number of characters for the 'files' field.


        Attr:
            id: A string column to store a unique identifier for each entry
            labels: A string column to store the labels associated with each entry
                    Conventional format: '[1], [2], [1]'
            data: A Float32  columns to store arrays with shape defined by the 'shape' argument
            boxes: A string column to store the coordinates (as start time, end time, start frequency, end frequency)\
                    of the acoustic events labelled in the 'labels' field.
                    Conventional format: '[[2, 5, 200, 400],[8, 14, 220, 450],[21, 25, 200, 400]]'
                    Where the first box correspond to the first label ([1]), the second box to the second label ([2]) and so forth. 
            files: A string column to store file names. In case the spectrogram is created from multiple files, this field stores all of them.
            file_vector: An Int8 column to store an array with length equal to the number of bins in the spectrogram.
                         Each value indicates the file that originated that bin, with 0 representing the first file listed in the 'files' field, 1 the second and so on. 
            time_vector: A Float32 column to store an array with length equal to the number of bins in the spectrogram. The array maps each bin to the time (seconds from start) in the original audio file (as stored in the file_vector_field)


        Results:
            TableDescription: class (tables.IsDescription)
                The class describing the table structure to be used when creating tables that 
                will store images in the HDF5 database.

        Examples:
            >>> from ketos.data_handling.database_interface import table_description
            >>> # create a table description with shape (64,20)
            >>> descr =  table_description(shape=(64,20))
            >>> descr.columns
            {'id': StringCol(itemsize=25, shape=(), dflt=b'', pos=None), 'labels': StringCol(itemsize=100, shape=(), dflt=b'', pos=None), 'data': Float32Col(shape=(64, 20), dflt=0.0, pos=None), 'boxes': StringCol(itemsize=100, shape=(), dflt=b'', pos=None), 'files': StringCol(itemsize=100, shape=(), dflt=b'', pos=None), 'file_vector': UInt8Col(shape=(64,), dflt=0, pos=None), 'time_vector': Float32Col(shape=(64,), dflt=0.0, pos=None)}


    """
    class TableDescription(tables.IsDescription):
            id = tables.StringCol(id_len)
            labels = tables.StringCol(labels_len)
            data = tables.Float32Col(shape)
            boxes = tables.StringCol(boxes_len) 
            files = tables.StringCol(files_len)
            file_vector = tables.UInt8Col(shape[0])
            time_vector = tables.Float32Col(shape[0])
    
    return TableDescription

def write_spec(table, spec, id=None):
    """ Write data into the HDF5 table.

        Note: If the id field is left blank, it 
        will be replaced with the tag attribute.

        Args:
            table: tables.Table
                Table in which the spectrogram will be stored
                (described by spec_description()).

            spec: instance of :class:`spectrogram.MagSpectrogram', \
            :class:`spectrogram.PowerSpectrogram', :class:`spectrogram.MelSpectrogram', \
                the spectrogram object to be stored in the table.

        Raises:
            TypeError: if spec is not an Spectrogram object    

        Returns:
            None.

        Examples:
            >>> import tables
            >>> from ketos.data_handling.database_interface import create_table
            >>> from ketos.audio_processing.spectrogram import MagSpectrogram
            >>> from ketos.audio_processing.audio import AudioSignal
            >>>
            >>> # Create an AudioSignal object from a .wav file
            >>> audio = AudioSignal.from_wav('ketos/tests/assets/2min.wav')
            >>> # Use that signal to create a spectrogram
            >>> spec = MagSpectrogram(audio,winlen=0.2, winstep=0.05)
            >>> # Annotate the spectrogram, adding two boxes and their corresponding labels
            >>> spec.annotate(boxes=[[5.3,8.9,200,350], [103.3,105.8,180,320]], labels=[1,2])
            >>>
            >>> # Open a connection to a database (and create the file)
            >>> h5file = tables.open_file("ketos/tests/assets/tmp/database2.h5", 'w')
            >>> # Create a table
            >>> my_table = create_table(h5file, "/group1/", "table1", shape=spec.image.shape)
            >>> # And write the spectrogram in the table
            >>> write_spec(my_table, spec)
            
            >>> # The table now has one item
            >>> my_table.nrows
            1
            >>> # We can check that the labels and boxes are the ones we created
            >>> my_table[0]['labels']
            b'[1,2]'
            >>> my_table[0]['boxes']
            b'[[5.3,8.9,200.0,350.0],[103.3,105.8,180.0,320.0]]'
            >>>
            >>> h5file.close()
    """

    try:
        assert(isinstance(spec, Spectrogram))
    except AssertionError:
        raise TypeError("spec must be an instance of Spectrogram")      

    table.attrs.time_res = spec.tres
    table.attrs.freq_res = spec.fres
    table.attrs.freq_min = spec.fmin

    if id is None:
        id_str = ''
    else:
        id_str = id

    if spec.labels is not None:
        labels_str = tostring(spec.labels, decimals=0)
    else:
        labels_str = ''

    if spec.boxes is not None:          
        boxes_str = tostring(spec.boxes, decimals=3)
    else:
        boxes_str = ''

    files_str = '['
    for it in spec.get_file_dict().items():
        val = it[1]
        files_str += val + ','
    if files_str[-1] == ',':
        files_str = files_str[:-1] 
    files_str += ']'    

    seg_r = table.row
    seg_r["data"] = spec.get_data()
    seg_r["id"] = id_str
    seg_r["labels"] = labels_str
    seg_r["boxes"] = boxes_str
    seg_r["files"] = files_str
    seg_r["file_vector"] = spec.get_file_vector()
    seg_r["time_vector"] = spec.get_time_vector()

    seg_r.append()

def filter_by_label(table, label):
    """ Find all spectrograms in the table with the specified label.

        Args:
            table: tables.Table
                The table containing the spectrograms
            label: int or list of ints
                The labels to be searched
        Raises:
            TypeError: if label is not an int or list of ints.

        Returns:
            rows: list(int)
                List of row numbers of the objects that have the specified label.
                If there are no spectrograms that match the label, returs an empty list.

        Examples:

            >>> import tables
            >>> from ketos.data_handling.database_interface import open_table
            >>>
            >>> # Open a database and an existing table
            >>> h5file = tables.open_file("ketos/tests/assets/15x_same_spec.h5", 'r')
            >>> table = open_table(h5file, "/train/species1")
            >>>
            >>> # Retrieve the indices for all spectrograms that contain the label 1
            >>> # (all spectrograms in this table)
            >>> filter_by_label(table, 1)
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            >>>
            >>> # Since none of the spectrograms in the table include the label 2, 
            >>> # an empty list is returned
            >>> filter_by_label(table, 2)
            []
            >>>
            >>> h5file.close()
    """
    if isinstance(label, (list)):
        if not all (isinstance(l, int) for l in label):
            raise TypeError("label must be an int or a list of ints")    
    elif isinstance(label, int):
        label = [label]
    else:
        raise TypeError("label must be an int or a list of ints")    
    
    
    matching_rows = []

    for i,row in enumerate(table.iterrows()):
        r_labels = row['labels']
        r_labels = parse_labels(r_labels)

        if any([l in label for l in r_labels]):
            matching_rows.append(i)
    

    return matching_rows

def load_specs(table, index_list=None):
    """ Retrieve all the spectrograms in a table or a subset specified by the index_list

        Warnings: Loading all spectrograms in a table might cause memory problems.

        Args:
            table: tables.Table
                The table containing the spectrogtrams
            index_list: list of ints or None
                A list with the indices of the spectrograms that will be retrieved.
                If set to None, loads all spectrograms in the table.

        Returns:
            res: list
                List of spectrogram objects.


        Examples:

            >>> import tables
            >>> from ketos.data_handling.database_interface import open_table
            >>>
            >>> # Open a connection to the database.
            >>> h5file = tables.open_file("ketos/tests/assets/15x_same_spec.h5", 'r')
            >>> # Open the species1 table in the train group
            >>> table = open_table(h5file, "/train/species1")
            >>>
            >>> # Load the spectrograms stored on rows 0, 3 and 10 of the species1 table
            >>> selected_specs = load_specs(table, [0,3,10])
            >>> # The resulting list has the 3 spectrogram objects
            >>> len(selected_specs)
            3
            >>> type(selected_specs[0])
            <class 'ketos.audio_processing.spectrogram.Spectrogram'>
            >>>
            >>> h5file.close()

    """
    res = list()
    if index_list is None:
        index_list = list(range(table.nrows))

    # loop over items in table
    for idx in index_list:

        it = table[idx]
        # parse labels and boxes
        labels = it['labels']
        labels = parse_labels(labels)
        boxes = it['boxes']
        boxes = parse_boxes(boxes)
        
        # get the spectrogram data
        data = it['data']

        # create audio signal or spectrogram object
        x = Spectrogram(image=data, tres=table.attrs.time_res, fres=table.attrs.freq_res, fmin=table.attrs.freq_min, tag='')

        # annotate
        #import pdb; pdb.set_trace()
        x.annotate(labels=labels, boxes=boxes)

        # handle file and time info
        x.time_vector = it['time_vector']
        x.file_vector = it['file_vector']
        files = it['files'].decode()[1:-1]
        if len(files) == 0:
            x.file_dict = {0: ''}
        else:
            files = files.split(',')
            file_dict = {}
            for i, f in enumerate(files):
                file_dict[i] = f
            x.file_dict = file_dict

        res.append(x)

    return res

def extract(table, label, min_length=None, center=False, fpad=True, keep_time=False):
    """ Create new spectrograms by croping segments annotated with the specified label.

        Filter the table by the specified label. In each of the selected spectrograms,
        search for the individual annotations (i.e.: boxes that match the specified label).
        Each annotation will result in a new spectrogram. After the matching segments are extracted,
        what is left is stiched together to create a spectrogram object. This spectrogram contains all
        the parts of the original spectrogram that did not contain any matching annotations and is treated
        as a complement to the extracted spectrograms. All the extracted spectrograms are returned in a list and 
        the complements in another.
        
        Any spectrogram in the table that does not contain any annotations of interest is added to the complements list. 

        Args:
            table: tables.Table
                The table containing the spectrograms.
            label: int
                The label
            min_length: float
                Minimum duration (in seconds) the of extracted segments.
            center: bool
                If True, place the annotation box in the center of the segments.
                Otherwise, place it randomly within the spectrogram.
            fpad: bool
                If True, ensure that all extracted spectrograms have the same 
                frequency range by padding with zeros, if necessary.
                If False, the resulting spectrograms will be cropped at the minimum
                and maximum frequencies specified by the bounding box.
            keep_time: bool
                If True, the initial time in the extracted spectrograms will maintained
                 (i.e.: will be equal to the start_time of the box).
                If false, the initial time is set to 0. 

            

        Returns:
            extractated: list
                List of spectrograms, created from segments matching the specified label
            complements: spectrogram or audio signal
                A list of spectrograms containing the joined segments that did not match the specified label.
                There will be on such spectrogram for each of the original spectrograms in the table.
                In case nothing is left after the extraction (i.e.: the whole spectrogram was covered by 
                the box/label of interest), the item in the complement list will have a None value.

        Examples:
            >>> import tables
            >>> from ketos.data_handling.database_interface import open_table
            >>>
            >>> # Open a connection to the database.
            >>> h5file = tables.open_file("ketos/tests/assets/15x_same_spec.h5", 'r')
            >>> # Open the species1 table in the train group
            >>> table = open_table(h5file, "/train/species1")
            >>>
            >>> # Extract the portions of the spectrograms annotated with label 1
            >>> extracted_specs, spec_complements = extract(table, label=1, min_length=2)
            >>> h5file.close()
            >>>
            >>> # The results show 
            >>> len(extracted_specs)
            15
            >>> len(spec_complements)
            15
            >>> 
            >>> #Plot one of the extracted spectrograms        
            >>> spec_1_fig = extracted_specs[0].plot()
            >>> spec_1_fig.savefig("ketos/tests/assets/tmp/extract_spec_1.png")
              
            .. image:: ../../../../ketos/tests/assets/tmp/extract_spec_1.png
                           
            >>> # Plot the portion without any annotations
            >>> comp_1_fig = spec_complements[0].plot()
            >>> comp_1_fig.savefig("ketos/tests/assets/tmp/extract_comp_1.png")
           
            .. image:: ../../../../ketos/tests/assets/tmp/extract_comp_1.png

            

    """

    # selected segments
    extracted = list()
    complements = list()

    items = load_specs(table)

    # loop over items in table
    for spec in items:

        # extract segments of interest
        segs = spec.extract(label=label, min_length=min_length, fpad=fpad, center=center, keep_time=keep_time)
        extracted = extracted + segs

        # collect
        complements.append(spec)
    

    return extracted, complements

def parse_labels(label):
    """ Parse the 'labels' field from an item in a hdf5 spectrogram table 
        

        Args:
            label: bytes str
            The bytes string containing the label (e.g.:b'[1]', b'[1,2]')

        Returns:
            parsed_labels: list(int)
            List of labels

        Example:
            >>> import tables
            >>> from ketos.data_handling.database_interface import open_table
            >>>
            >>> # Open a connection to the database.
            >>> h5file = tables.open_file("ketos/tests/assets/15x_same_spec.h5", 'r')
            >>> # Open the species1 table in the train group
            >>> table = open_table(h5file, "/train/species1")
            >>>
            >>> #The labels are stored as byte strings in the table
            >>> type(table[0]['labels'])
            <class 'numpy.bytes_'>
            >>> table[0]['labels']
            b'[1]'
            >>>
            >>> label =table[0]['labels']
            >>> parsed_label = parse_labels(label)
            >>> type(parsed_label)
            <class 'list'>
            >>> # After parsing, they are lists of integers and can be used as such
            >>> parsed_label
            [1]
            >>>
            >>> h5file.close()
  
    """
    labels_str = label.decode()
    parsed_labels = np.fromstring(string=labels_str[1:-1], dtype=int, sep=',')
    parsed_labels = list(parsed_labels)
    return parsed_labels

def parse_boxes(boxes):
    """ Parse the 'boxes' field from an item in a hdf5 spectrogram table

        Args:
            boxex: bytes str
            The bytes string containing the label (e.g.:b'[[105, 107, 200,400]]', b'[[105,107,200,400], [230,238,220,400]]')
        Returns:
            labels: list(tuple)
                List of boxes
        Example:
            >>> import tables
            >>> from ketos.data_handling.database_interface import open_table
            >>>
            >>> # Open a connection to the database.
            >>> h5file = tables.open_file("ketos/tests/assets/15x_same_spec.h5", 'r')
            >>> # Open the species1 table in the train group
            >>> table = open_table(h5file, "/train/species1")
            >>>
            >>> #The boxes are stored as byte strings in the table
            >>> boxes = table[0]['boxes']
            >>> type(boxes)
            <class 'numpy.bytes_'>
            >>> boxes
            b'[[10,15,200,400]]'
            >>>
            >>> parsed_box = parse_boxes(boxes)
            >>> type(parsed_box)
            <class 'list'>
            >>> # After parsing, the all of boxes becomes a list, which
            >>> # has each box as a list of integers
            >>> parsed_box
            [[10, 15, 200, 400]]
            >>>
            >>> h5file.close()
    """
    
    boxes_str = boxes.decode()
    boxes_str = boxes_str.replace("inf", "-99")
    try:
        boxes_str = ast.literal_eval(boxes_str)
    except:
        parsed_boxes = []

    parsed_boxes = np.array(boxes_str)

    if (parsed_boxes == -99).any():
         parsed_boxes[parsed_boxes == -99] = math.inf

    parsed_boxes = parsed_boxes.tolist()
    
    return parsed_boxes

def create_spec_database(output_file, input_dir, annotations_file=None,\
        sampling_rate=None, channel=0, window_size=0.2, step_size=0.02, duration=None,\
        flow=None, fhigh=None, max_size=1E9, progress_bar=False, verbose=True, **kwargs):
    """ Create a database with spectrograms computed from raw audio (*.wav) files

        One spectrogram is created for each audio file.
        
        However, if the spectrogram is longer than the specified duration, the spectrogram 
        will be split into segments, each with the desired duration.

        On the other hand, if a spectrogram is shorter than the specified duration, the spectrogram will 
        be padded with zeros to achieve the desired duration. 

        If duration is not specified (default), it will be set equal to the duration 
        of the first spectrogram that is processed.

        Thus, all saved spectrograms will have the same duration.

        If the combined size of the spectrograms exceeds max_size (1 GB by default), the output database 
        file will be split into several files, with _000, _001, etc, appended to the filename.

        The internal file structure of the database file will mirror the structure of the 
        data directory where the audio data is stored. See the example below.

        Args:
            output_file: str
                Full path to output database file (*.h5)
            input_dir: str
                Full path to folder containing the input audio files (*.wav)
            annotations_file: str
                Full path to file containing annotations (*.csv)
            sampling_rate: float
                If specified, audio data will be resampled at this rate
            channel: int
                For stereo recordings, this can be used to select which channel to read from
            window_size: float
                Window size (seconds) used for computing the spectrogram
            step_size: float
                Step size (seconds) used for computing the spectrogram
            duration: float
                Duration in seconds of individual spectrograms.
            flow: float
                Lower cut on frequency (Hz)
            fhigh: float
                Upper cut on frequency (Hz)
            max_size: int
                Maximum size of output database file in bytes
                If file exceeds this size, it will be split up into several 
                files with _000, _001, etc, appended to the filename.
                The default values is max_size=1E9 (1 Gbyte)
            progress_bar: bool
                Option to display progress bar.
            verbose: bool
                Print relevant information during execution such as files written to disk

            Example:

                >>> # create a few audio files and save them as *.wav files
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> cos7 = AudioSignal.cosine(rate=1000, frequency=7.0, duration=1.0)
                >>> cos8 = AudioSignal.cosine(rate=1000, frequency=8.0, duration=1.0)
                >>> cos21 = AudioSignal.cosine(rate=1000, frequency=21.0, duration=1.0)
                >>> folder = "ketos/tests/assets/tmp/harmonic/"
                >>> cos7.to_wav(folder+'cos7.wav')
                >>> cos8.to_wav(folder+'cos8.wav')
                >>> cos21.to_wav(folder+'highfreq/cos21.wav')
                >>> # now create a database of spectrograms from these audio files
                >>> from ketos.data_handling.database_interface import create_spec_database
                >>> fout = folder + 'harmonic.h5'
                >>> create_spec_database(output_file=fout, input_dir=folder)
                3 spectrograms saved to ketos/tests/assets/tmp/harmonic/harmonic.h5
                >>> # inspect the contacts of the database file
                >>> import tables
                >>> f = tables.open_file(fout, 'r')
                >>> print(f.root.spec)
                /spec (Table(2,), fletcher32, shuffle, zlib(1)) ''
                >>> print(f.root.highfreq.spec)
                /highfreq/spec (Table(1,), fletcher32, shuffle, zlib(1)) ''
                >>> f.close()
    """
    # annotation reader
    if annotations_file is None:
        areader = None
        max_ann = 1
    else:
        areader = AnnotationTableReader(annotations_file)
        max_ann = areader.get_max_annotations()

    # spectrogram writer
    swriter = SpecWriter(output_file=output_file, max_size=max_size, max_annotations=max_ann, verbose=verbose)

    # get all wav files in the folder
    files = find_wave_files(path=input_dir, fullpath=True, subdirs=True)

    # subfolder unix structure
    subfolders = list()
    for f in files:
        sf = rel_path_unix(f, input_dir)
        subfolders.append(sf)

    # loop over files
    for i in tqdm(range(len(files)), disable = not progress_bar):
    
        f = files[i]
        sf = subfolders[i]

        # check if files exists
        exists = os.path.exists(f)
        if exists is False:
            continue

        # read audio and resample
        a = AudioSignal.from_wav(path=f, channel=channel)  
        if sampling_rate is not None:
            a.resample(new_rate=sampling_rate) 

        # compute the spectrogram
        s = MagSpectrogram(audio_signal=a, winlen=window_size, winstep=step_size, decibel=True) 

        # add annotations
        if areader is not None:
            fname = f[f.rfind('/')+1:]
            labels, boxes = areader.get_annotations(fname)
            s.annotate(labels, boxes) 

        # crop frequencies
        s.crop(flow=flow, fhigh=fhigh) 

        # if duration is not specified, use duration of first spectrogram
        if duration is None: 
            duration = s.duration()

        # ensure desired duration 
        specs = s.segment(length=duration, pad=True, **kwargs)

        # save spectrogram(s) to file        
        path = sf + 'spec'
        swriter.cd(path)
        for spec in specs:
            swriter.write(spec)

    swriter.close()

class SpecWriter():
    """ Saves spectrograms to a database file (*.h5).

        If the combined size of the spectrograms exceeds max_size (1 GB by default), the output database 
        file will be split into several files, with _000, _001, etc, appended to the filename.

        Args:
            output_file: str
                Full path to output database file (*.h5)
            max_annotations: int
                Maximum number of annotations allowed for any spectrogram
            max_size: int
                Maximum size of output database file in bytes
                If file exceeds this size, it will be split up into several 
                files with _000, _001, etc, appended to the filename.
                The default values is max_size=1E9 (1 Gbyte)
            verbose: bool
                Print relevant information during execution such as files written to disk

        Attributes:
            base: str
                Output filename base
            ext: str
                Output filename extension (*.h5)
            file: tables.File
                Database file
            file_counter: int
                Keeps track of how many files have been written to disk
            spec_counter: int
                Keeps track of how many spectrograms have been written to files
            path: str
                Path to table within database filesystem
            name: str
                Name of table 
            max_annotations: int
                Maximum number of annotations allowed for any spectrogram
            max_file_size: int
                Maximum size of output database file in bytes
                If file exceeds this size, it will be split up into several 
                files with _000, _001, etc, appended to the filename.
                The default values is max_size=1E9 (1 Gbyte)
            verbose: bool
                Print relevant information during execution such as files written to disk

            Example:

                >>> # create a few cosine wave forms
                >>> from ketos.audio_processing.audio import AudioSignal
                >>> cos7 = AudioSignal.cosine(rate=1000, frequency=7.0, duration=1.0)
                >>> cos8 = AudioSignal.cosine(rate=1000, frequency=8.0, duration=1.0)
                >>> cos21 = AudioSignal.cosine(rate=1000, frequency=21.0, duration=1.0)
                >>> # compute spectrograms
                >>> from ketos.audio_processing.spectrogram import MagSpectrogram
                >>> s7 = MagSpectrogram(cos7, winlen=0.2, winstep=0.02)
                >>> s8 = MagSpectrogram(cos8, winlen=0.2, winstep=0.02)
                >>> s21 = MagSpectrogram(cos21, winlen=0.2, winstep=0.02)
                >>> # save the spectrograms to a database file
                >>> from ketos.data_handling.database_interface import SpecWriter
                >>> fname = "ketos/tests/assets/tmp/db_harm.h5"
                >>> writer = SpecWriter(output_file=fname)
                >>> writer.write(s7)
                >>> writer.write(s8)
                >>> writer.write(s21)
                >>> writer.close()
                3 spectrograms saved to ketos/tests/assets/tmp/db_harm.h5
                >>> # inspect the contacts of the database file
                >>> import tables
                >>> f = tables.open_file(fname, 'r')
                >>> print(f.root.spec)
                /spec (Table(3,), fletcher32, shuffle, zlib(1)) ''
    """
    def __init__(self, output_file, max_size=1E9, verbose=True, max_annotations=100):
        
        self.base = output_file[:output_file.rfind('.')]
        self.ext = output_file[output_file.rfind('.'):]
        self.file = None
        self.file_counter = 0
        self.max_annotations = max_annotations
        self.max_file_size = max_size
        self.path = '/'
        self.name = 'spec'
        self.verbose = verbose
        self.spec_counter = 0

    def cd(self, fullpath='/'):
        """ Change the current directory within the database file system

            Args:
                fullpath: str
                    Full path to the table. For example, /data/spec
        """
        self.path = fullpath[:fullpath.rfind('/')+1]
        self.name = fullpath[fullpath.rfind('/')+1:]

    def write(self, spec, path=None, name=None):
        """ Write spectrogram to a table in the database file

            If path and name are not specified, the spectrogram will be 
            saved to the current directory (as set with the cd() method).

            Args:
                spec: Spectrogram
                    Spectrogram to be saved
                path: str
                    Path to the group containing the table
                name: str
                    Name of the table
        """
        if path is None:
            path = self.path
        if name is None:
            name = self.name

        # ensure a file is open
        self._open_file() 

        # open/create table
        tbl = self._open_table(path=path, name=name, shape=spec.image.shape) 

        # write spectrogram to table
        write_spec(tbl, spec)
        self.spec_counter += 1

        # close file if size reaches limit
        siz = self.file.get_filesize()
        if siz > self.max_file_size:
            self.close(final=False)

    def close(self, final=True):
        """ Close the currently open database file, if any

            Args:
                final: bool
                    If True, this instance of SpecWriter will not be able to save more spectrograms to file
        """        
        if self.file is not None:

            actual_fname = self.file.filename
            self.file.close()
            self.file = None

            if final and self.file_counter == 1:
                fname = self.base + self.ext
                os.rename(actual_fname, fname)
            else:
                fname = actual_fname

            if self.verbose:
                plural = ['', 's']
                print('{0} spectrogram{1} saved to {2}'.format(self.spec_counter, plural[self.spec_counter > 1], fname))

            self.spec_counter = 0

    def _open_table(self, path, name, shape):
        """ Open the specified table.

            If the table does not exist, create it.

            Args:
                path: str
                    Path to the group containing the table
                name: str
                    Name of the table
                shape: tuple
                    Shape of spectrogram image

            Returns:
                tbl: tables.Table
                    Table
        """        

        if path == '/':
            x = path + name
        elif path[-1] == '/':
            x = path + name
            path = path[:-1]
        else:
            x = path + '/' + name

        if x in self.file:
            tbl = self.file.get_node(path, name)
        else:
            tbl = create_table(h5file=self.file, path=path, name=name, shape=shape, max_annotations=self.max_annotations)

        return tbl

    def _open_file(self):
        """ Open a new database file, if none is open
        """                
        if self.file is None:
            fname = self.base + '_{:03d}'.format(self.file_counter) + self.ext
            self.file = tables.open_file(fname, 'w')
            self.file_counter += 1
