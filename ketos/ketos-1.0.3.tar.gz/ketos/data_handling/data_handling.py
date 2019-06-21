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

""" Data handling module within the ketos library

    This module provides utilities to load and handle data files.
"""
import numpy as np
import pandas as pd
import librosa
import os
import math
import errno
import tables
from subprocess import call
import scipy.io.wavfile as wave
import ketos.external.wavfile as wave_bit
from ketos.utils import tostring
import datetime
import datetime_glob
import re


def rel_path_unix(path, start=None):
    """ Return a relative unix filepath to path either from the current 
        directory or from an optional start directory.

        Args:
            path: str
                Path. Can be unix or windows format.
            start: str
                Optional start directory. Can be unix or windows format.

        Returns:
            u: str
                Relative unix filepath

        Examples:
            >>> from ketos.data_handling.data_handling import rel_path_unix      
            >>> path = "/home/me/documents/projectX/file1.pdf"
            >>> start = "/home/me/documents/"
            >>> u = rel_path_unix(path, start)
            >>> print(u)
            /projectX/
    """
    rel = os.path.relpath(path, start)
    h,t = os.path.split(rel)
    u = '/'
    while len(h) > 0:
        h,t = os.path.split(h)
        u = '/' + t + u

    return u



def parse_datetime(to_parse, fmt=None, replace_spaces='0'):
    """Parse date-time data from string.
       
       Returns None if parsing fails.
        
        Args:
            to_parse: str
                String with date-time data to parse.
            fmt: str
                String defining the date-time format. 
                Example: %d_%m_%Y* would capture "14_3_1999.txt"
                See https://pypi.org/project/datetime-glob/ for a list of valid directives
                
            replace_spaces: str
                If string contains spaces, replaces them with this string

        Returns:
            datetime: datetime object

        Examples:
            >>> #This will parse dates in the day/month/year format,
            >>> #separated by '/'. It will also ignore any text after the year,
            >>> # (such as a file extension )
            >>>
            >>> from ketos.data_handling.data_handling import parse_datetime           
            >>> fmt = "%d/%m/%Y*"
            >>> result = parse_datetime("10/03/1942.txt", fmt)
            >>> result.year
            1942
            >>> result.month
            3
            >>> result.day
            10
            >>>
            >>> # Now with the time (hour:minute:second) separated from the date by an underscore
            >>> fmt = "%H:%M:%S_%d/%m/%Y*"
            >>> result = parse_datetime("15:43:03_10/03/1918.wav", fmt)
            >>> result.year
            1918
            >>> result.month
            3
            >>> result.day
            10
            >>> result.hour
            15
            >>> result.minute
            43
            >>> result.second
            3
    """

    # replace spaces
    to_parse = to_parse.replace(' ', replace_spaces)
    
    if fmt is not None:
        matcher = datetime_glob.Matcher(pattern=fmt)
        match = matcher.match(path=to_parse)
        if match is None:
            return None
        else:
            return match.as_datetime()

    return None

def find_files(path, substr, fullpath=True, subdirs=False):
    """ Find all files in the specified directory containing the specified substring in their file name

        Args:
            path: str
                Directory path
            substr: str
                Substring contained in file name
            fullpath: bool
                If True, return relative path to each file. If false, only return the file names 
            subdirs: bool
                If True, search all subdirectories

        Returns:
            files: list (str)
                Alphabetically sorted list of file names

        Examples:
            >>> from ketos.data_handling.data_handling import find_files
            >>>
            >>> # Find files that contain 'super' in the name;
            >>> # Do not return the relative path
            >>> find_files(path="ketos/tests/assets", substr="super", fullpath=False)
            ['super_short_1.wav', 'super_short_2.wav']
            >>>
            >>> # find all files with '.h5" in the name
            >>> # Return the relative path
            >>> find_files(path="ketos/tests/assets", substr=".h5")
            ['ketos/tests/assets/15x_same_spec.h5', 'ketos/tests/assets/cod.h5', 'ketos/tests/assets/humpback.h5', 'ketos/tests/assets/morlet.h5']
    """
    # find all files
    allfiles = list()
    if not subdirs:
        f = os.listdir(path)
        for fil in f:
            if fullpath:
                x = path
                allfiles.append(os.path.join(x, fil))
            else:
                allfiles.append(fil)
    else:
        for r, _, f in os.walk(path):
            for fil in f:
                if fullpath:
                    allfiles.append(os.path.join(r, fil))
                else:
                    allfiles.append(fil)

    # select those that contain specified substring
    files = list()
    for f in allfiles:
        if substr in f:
            files.append(f)

    # sort alphabetically
    files.sort()

    return files


def find_wave_files(path, fullpath=True, subdirs=False):
    """ Find all wave files in the specified directory

        Args:
            path: str
                Directory path
            fullpath: bool
                Return relative path to each file or just the file name 

        Returns:
            wavefiles: list (str)
                Alphabetically sorted list of file names

        Examples:
            >>> from ketos.data_handling.data_handling import find_wave_files
            >>>
            >>> find_wave_files(path="ketos/tests/assets", fullpath=False)
            ['2min.wav', 'empty.wav', 'grunt1.wav', 'super_short_1.wav', 'super_short_2.wav']

    """
    wavefiles = find_files(path, '.wav', fullpath, subdirs)
    return wavefiles


def read_wave(file, channel=0):
    """ Read a wave file in either mono or stereo mode

        Args:
            file: str
                path to the wave file
            channel: int
                Which channel should be used in case of stereo data (0: left, 1: right) 

        Returns: (rate,data)
            rate: int
                The sampling rate
            data: numpy.array (float)
                A 1d array containing the audio data
        
        Examples:
            >>> from ketos.data_handling.data_handling import read_wave
            >>> rate, data = read_wave("ketos/tests/assets/2min.wav")
            >>> # the function returns the sampling rate (in Hz) as an integer
            >>> type(rate)
            <class 'int'>
            >>> rate
            2000
            >>> # And the actual audio data is a numpy array
            >>> type(data)
            <class 'numpy.ndarray'>
            >>> len(data)
            241664
            >>> # Since each item in the vector is one sample,
            >>> # The duration of the audio in seconds can be obtained by
            >>> # dividing the the vector length by the sampling rate
            >>> len(data)/rate
            120.832
    """
    try:
        rate, signal, _ = wave_bit.read(file)
    except TypeError:
        rate, signal = wave.read(file)
           
    if len(signal.shape) == 2:
        data = signal[:, channel]
    else:
        data = signal[:]
    return rate, data

def create_dir(dir):
    """ Create a new directory if it does not exist

        Will also create any intermediate directories that do not exist
        Args:
            dir: str
               The path to the new directory
     """
    os.makedirs(dir, exist_ok=True)

def to1hot(value,depth):
    """Converts the binary label to one hot format

            Args:
                value: scalar or numpy.array | int or float
                    The the label to be converted.
                depth: int
                    The number of possible values for the labels 
                    (number of categories).
                                
            Returns:
                one_hot:numpy array (dtype=float64)
                    A len(value) by depth array containg the one hot encoding
                    for the given value(s).

            Example:
                >>> from ketos.data_handling.data_handling import to1hot
                >>>
                >>> # An example with two possible labels (0 or 1)
                >>> values = np.array([0,1])
                >>> to1hot(values,depth=2)
                array([[1., 0.],
                       [0., 1.]])
                >>>
                >>> # The same example with 4 possible labels (0,1,2 or 3)
                >>> values = np.array([0,1])
                >>> to1hot(values,depth=4)
                array([[1., 0., 0., 0.],
                       [0., 1., 0., 0.]])
     """
    value = np.int64(value)
    one_hot = np.eye(depth)[value]
    return one_hot

def from1hot(value):
    """Converts the one hot label to binary format

            Args:
                value: scalar or numpy.array | int or float
                    The  label to be converted.
            
            Returns:
                output: int or numpy array (dtype=int64)
                    An int representing the category if 'value' has 1 dimension or an
                    array of m ints if values is an n by m array.

            Example:
                >>> from ketos.data_handling.data_handling import from1hot
                >>>
                >>> from1hot(np.array([0,0,0,1,0]))
                3
                >>> from1hot(np.array([[0,0,0,1,0],
                ...   [0,1,0,0,0]]))
                array([3, 1])

     """

    if value.ndim > 1:
        output = np.apply_along_axis(arr=value, axis=1, func1d=np.argmax)
        output.dtype = np.int64
    else:
        output = np.argmax(value)

    return output


def check_data_sanity(images, labels):
    """ Check that all images have same size, all labels have values, 
        and number of images and labels match.
     
        Args:
            images: numpy array or pandas series
                Images
            labels: numpy array or pandas series
                Labels
        Raises:
            ValueError:
                If no images or labels are passed;
                If the number of images and labels is different;
                If images have different shapes;
                If any labels are NaN.

       Returns:
            True if all checks pass.

        Examples:
            >>> from ketos.data_handling.data_handling import check_data_sanity
            >>> # Load a database with images and integer labels
            >>> data = pd.read_pickle("ketos/tests/assets/pd_img_db.pickle")
            >>> images = data['image']
            >>> labels = data['label']
            >>> # When all the images and labels  pass all the quality checks,
            >>> # The function returns True            
            >>> check_data_sanity(images, labels)
            True
            >>> # If something is wrong, like if the number of labels
            >>> # is different from the number of images, and exeption is raised
            >>> labels = data['label'][:10] 
            >>> check_data_sanity(images, labels=labels)
            Traceback (most recent call last):
                File "/usr/lib/python3.6/doctest.py", line 1330, in __run
                    compileflags, 1), test.globs)
                File "<doctest data_handling.check_data_sanity[5]>", line 1, in <module>
                    check_data_sanity(images, labels=labels)
                File "ketos/data_handling/data_handling.py", line 599, in check_data_sanity
                    raise ValueError("Image and label columns have different lengths")
            ValueError: Image and label columns have different lengths



    """
    checks = True
    if images is None or labels is None:
        raise ValueError(" Images and labels cannot be None")
        

    # check that number of images matches numbers of labels
    if len(images) != len(labels):
        raise ValueError("Image and label columns have different lengths")

    # determine image size and check that all images have same size
    image_shape = images[0].shape
    if not all(x.shape == image_shape for x in images):
        raise ValueError("Images do not all have the same size")

    # check that all labels have values
    b = np.isnan(labels)    
    n = np.count_nonzero(b)
    if n != 0:
        raise ValueError("Some labels are NaN")
    
    return checks

def get_image_size(images):
    """ Get image size and check that all images have same size.
     
        Args:
            images: numpy array or pandas series
                Images

        Results:
            image_size: tuple (int,int)
                Image size

        Examples:
            >>> from ketos.data_handling.data_handling import get_image_size
            >>> import pandas as pd
            >>>
            >>> # Load a dataset with images and integer labels
            >>> data = pd.read_pickle("ketos/tests/assets/pd_img_db.pickle")
            >>>
            >>> # Select only the images from the dataset
            >>> images = data['image']
            >>> get_image_size(images)
            (20, 20)

    """
    # determine image size and check that all images have same size
    image_shape = images[0].shape
    assert all(x.shape == image_shape for x in images), "Images do not all have the same size"

    return image_shape


def parse_seg_name(seg_name):
    """ Retrieves the segment id and label from the segment name

        Args:
            seg_name: str
            Name of the segment in the format id_*_*_l_*.wav, where 'id' is 
            followed by base name of the audio file from which the segment was extracted, '_',
            and a sequence number. The 'l' is followed by any number of characters describing the label(s).

        Raise:
            ValueError
            If seg_name is empty or in wrong format
        Returns:
            (id,label) : tuple (str,str)
            A tuple with the id and label strings.

        Examples:
            >>> from ketos.data_handling.data_handling import parse_seg_name
            >>> seg_name = "id_hydr06_23_l_[2].wav"
            >>> id, label = parse_seg_name(seg_name)
            >>> id
            'hydr06_23'
            >>> label
            '[2]'
            >>>
            >>> seg_name = "id_hydr05_279_l_[2,1].mp3"
            >>> id, label = parse_seg_name(seg_name)
            >>> id
            'hydr05_279'
            >>> label
            '[2,1]'

    """
    id, labels = None, None
    pattern=re.compile('id_(.+)_(.+)_l_\[(.+)\].*')
    if not pattern.match(seg_name):
       raise ValueError("seg_name must follow the format  id_*_*_l_[*].")


    splits = seg_name.split("_")
    if len(splits) >= 5:
        id = seg_name.split("_")[1] + "_" + seg_name.split("_")[2]
        tmp = seg_name.split("_")[4]
        labels = tmp.split(".")[0]
    
    return (id,labels)



def divide_audio_into_segs(audio_file, seg_duration, save_to, annotations=None, start_seg=None, end_seg=None, verbose=False):
    """ Divide a large .wav file into a sequence of smaller segments with the same duration.
        

        Name the resulting segments sequentially and save them as .wav files in the specified directory.
        If annotations are provided, this function will check if the segment created emcompasses any labels. If so,
        the label information will be added to the segment name.
        
        Note: segments will be saved following the name pattern "id_*_*_l_*.wav",
            where 'id_' is followed by the name of the original file, underscore ('_') 
            and the a sequence name. 'l_' is followed by the label(s) associated with that segment.
            Ex: 'id_rec03_87_l_[1,3]', 'id_rec03_88_l_[0]

            The start_seg and end_seg arguments can be used to segment only part of audio files,
            which is useful when processing large files in parallel.
            
        Args:
            audio_file:str
            .wav file name (including path).

            seg_duration: float
            desired duration for each segment

            annotations: pandas.DataFrame
            DataFrame with the the annotations. At least the following columns are expected:
                "filename": the file name. Must be the the same as audio_file
                "label": the label value for each annotaded event
                "start": the start time relative to the beginning of the audio_file.
                "end": the end time relative to the beginning of the file. 
            If None, the segments will be created and file names will have 'NULL' as labels. 
            Ex: 'id_rec03_87_l[NULL].wav.
                    
            save_to: str
            path to the directory where segments will be saved.

            start_seg: int
                Indicates the number of the segment on which the segmentation will start.
                A value of 3 would indicate the 3rd segment in a sequence(if 'seg_duration' is set to 2.0,
                that would corresponfd to 6.0 seconds from the beginning of the file')
            end_seg:int
                Indicates the number of the segment where the segmentation will stop.
                A value of 6 would indicate the 3rd segment in a sequence(if 'seg_duration' is set to 2.0,
                that would correspond to 12.0 seconds from the beginning of the file'
            verbose:bool
                If True, print "Creating segment .... name_of_segment" for each segment.
                        
         Returns:
            None   

        Examples:
            >>> from ketos.data_handling.data_handling import divide_audio_into_segs
            >>> from glob import glob
            >>> import os
            >>>
            >>> # Define the paths to the audio file that will be segmented
            >>> # And the folder where the segments will be saved
            >>> audio_file = "ketos/tests/assets/2min.wav"
            >>> save_dir = "ketos/tests/assets/tmp/divided_segs"
            >>> # Create that folder (if it does not exist)
            >>> os.makedirs(save_dir, exist_ok=True)
            >>> # Difine an annotations dataframe
            >>> annotations = pd.DataFrame({'filename':['2min.wav','2min.wav','2min.wav'],
            ...                    'label':[1,2,1], 'start':[5.0, 70.34, 105.8],
            ...                    'end':[6.0,75.98,110.0]})
            >>>
            >>> # Devide the wav file into 2 seconds segments.
            >>> # Uses the annotations dataframe to determine if each segment
            >>> # includes a label names the segments accordingly
            >>> divide_audio_into_segs(audio_file=audio_file,
            ... seg_duration=2.0, annotations=annotations, save_to=save_dir)
            >>> # Count all files have been created in the destination folder
            >>> n_seg = len(glob(save_dir + "/id_2min*.wav"))
            >>> #60 files have been created
            >>> n_seg
            60
    """
    create_dir(save_to)
    orig_audio_duration = librosa.get_duration(filename=audio_file)
    n_seg = round(orig_audio_duration/seg_duration)

    prefix = os.path.basename(audio_file).split(".wav")[0]

    if start_seg is None:
        start_seg = 0
    if end_seg is None:
        end_seg = n_seg - 1

    for s in range(start_seg, end_seg + 1):
        start = s * seg_duration - seg_duration
        end = start + seg_duration

        if annotations is None:
            label = '[NULL]'
        else:
            label =  get_labels(prefix, start, end, annotations)

        out_name = "id_" + prefix + "_" + str(s) + "_l_" + label + ".wav"
        path_to_seg = os.path.join(save_to, out_name)    
        sig, rate = librosa.load(audio_file, sr=None, offset=start, duration=seg_duration)
        if verbose:
            print("Creating segment......", path_to_seg)
        librosa.output.write_wav(path_to_seg, sig, rate)

def _filter_annotations_by_filename(annotations, filename):
    """ Filter the annotations DataFrame by the base of the original file name (without the path or extension)

        Args:
        file: str
           The original audio file name without path or extensions.
           Ex: 'file_1' will match the entry './data/sample_a/file_1.wav" in the filename
           column of the annotations DataFrame.

        annotations: pandas.DataFrame
            DataFrame with the the annotations. At least the following columns are expected:
                "filename": the file name. Must be the the same as audio_file
                "label": the label value for each annotaded event
                "start": the start time relative to the beginning of the audio_file.
                "end": the end time relative to the beginning of the file.

        Returns:
            filtered annotations: pandas.DataFrame
            A subset of the annotations DataFrame containing only the entries for the specified file.
            
        Examples:
            >>> from ketos.data_handling.data_handling import _filter_annotations_by_filename
            >>> import pandas as pd
            >>> # Create an annotations dataframe
            >>> annotations = pd.DataFrame({'filename':['2min_01.wav','2min_01.wav','2min_02.wav','2min_02.wav','2min_02.wav'],
            ...                     'label':[1,2,1,1,1], 'start':[5.0, 100.5, 105.0, 80.0, 90.0],
            ...                     'end':[6.0,103.0,108.0, 87.0, 94.0]})
            >>> # Filter the annotations associated with file "2min_01"
            >>> annot_01 = _filter_annotations_by_filename(annotations,'2min_01')
            >>> annot_01
                  filename  label  start    end
            0  2min_01.wav      1    5.0    6.0
            1  2min_01.wav      2  100.5  103.0
                                 

    """
    filtered_indices = annotations.apply(axis=1, func= lambda row: os.path.basename(row.filename).split(".wav")[0] == filename)
    filtered_annotations = annotations[filtered_indices]
    return filtered_annotations

def get_labels(file, start, end, annotations, not_in_annotations=0):
    """ Retrieves the labels that fall in the specified interval.
    
        Args:
        file: str
           The base name (without paths or extensions) for the original audio file. Will be used to match the 'filename' field
           in the annotations Dataframe. Important: The name of the files must be
           unique within the annotations, even if the path is different.
           Ex: '/data/sample_a/file_1.wav' and '/data/sample_b/file_1.wav'

        annotations: pandas.DataFrame
            DataFrame with the the annotations. At least the following columns are expected:
                "filename": the file name. Must be the the same as audio_file
                "label": the label value for each annotaded event
                "start": the start time relative to the beginning of the audio_file.
                "end": the end time relative to the beginning of the file.
            
        not_in_annotations: str
            Label to be used if the segment is not included in the annotations.

        Returns:
            labels: str
                The labels corresponding to the interval specified.
                if the interval is not in the annotations, the value 
                specified in 'not_in_annotations' will be used.

        Examples:
            >>> from ketos.data_handling.data_handling import get_labels
            >>> import pandas as pd
            >>> audio_file="2min"
            >>> # Create an annotations dataframe
            >>> annotations = pd.DataFrame({'filename':['2min.wav','2min.wav','2min.wav'],
            ...                            'label':[1,2,1], 'start':[5.0, 100.5, 105.0],
            ...                            'end':[6.0,103.0,108.0]})
            >>> # Find all labels between time 4.0 seconds and time 5.0 seconds.
            >>> get_labels(file='2min',start=4.0, end=5.5,
            ...                        annotations=annotations, not_in_annotations=0)
            '[1]'
            >>>
            >>> # Find all labels between time 99.0 seconds and time 110.0 seconds.
            >>> get_labels(file='2min',start=99.0, end=110.0,
            ...                        annotations=annotations, not_in_annotations=0)
            '[2, 1]'

    """
    interval_start = start
    interval_end = end

    data = _filter_annotations_by_filename(annotations, file)
    query_results = data.query("(@interval_start >= start & @interval_start <= end) | (@interval_end >= start & @interval_end <= end) | (@interval_start <= start & @interval_end >= end)")
    #print(query_results)
    
    if query_results.empty:
        label = [not_in_annotations]
    else:
        label=[]
        for l in query_results.label:
          label.append(l)
                 
    return str(label)


def seg_from_time_tag(audio_file, start, end, name, save_to):
    """ Extract a segment from the audio_file according to the start and end tags.

        Args:
            audio_file:str
            .wav file name (including path).

            start:float
            Start point for segment (in seconds from start of the source audio_file)

            end:float
            End point for segment (in seconds from start of the source audio_file)
            
            save_to: str
            Path to the directory where segments will be saved.
            
            name: str
            Name of segment file name (including '.wav')
            

        Returns:

            None

        Examples:
            >>> import os
            >>> from ketos.data_handling.data_handling import read_wave
            >>> from ketos.data_handling.data_handling import seg_from_time_tag
            >>>
            >>> # Define the audio file and the destination folder
            >>> audio_file = "ketos/tests/assets/2min.wav"
            >>> save_dir = "ketos/tests/assets/tmp/segs_from_tags"
            >>> # Create the folder
            >>> os.makedirs(save_dir, exist_ok=True)
            >>>
            >>> # Create a segmet starting at 0.5 seconds and ending at 2.5 seconds
            >>> seg_from_time_tag(audio_file=audio_file, start=0.5, end=2.5 , name="seg_1.wav", save_to=save_dir )
            >>>
            >>> # Read the created segment and check its duration
            >>> rate, sig  = read_wave(os.path.join(save_dir, "seg_1.wav"))
            >>> duration = len(sig)/rate
            >>> duration
            2.0

    """
    out_seg = os.path.join(save_to, name)
    sig, rate = librosa.load(audio_file, sr=None, offset=start, duration=end - start)
    librosa.output.write_wav(out_seg, sig, rate)


def segs_from_annotations(annotations, save_to):
    """ Generates segments based on the annotations DataFrame.

        Args:
            annotations: pandas.DataFrame
            DataFrame with the the annotations. At least the following columns are expected:
                "filename": the file name. Must be the the same as audio_file
                "label": the label value for each annotaded event
                "start": the start time relative to the beginning of the audio_file.
                "end": the end time relative to the beginning of the file.
            save_to: str
            path to the directory where segments will be saved.
            
            
        Returns:
            None
            
        Examples:
            >>> import os
            >>> from glob import glob
            >>> import pandas as pd
            >>> from ketos.data_handling.data_handling import segs_from_annotations
            >>>
            >>> # Define the audio file and the destination folder
            >>> audio_file_path = "ketos/tests/assets/2min.wav"
            >>> save_dir = "ketos/tests/assets/tmp/from_annot"
            >>>
            >>> # Create a dataframe with annotations
            >>> annotations = pd.DataFrame({'filename':[audio_file_path,audio_file_path,audio_file_path],
            ...                            'label':[1,2,1], 'start':[5.0, 70.5, 105.0],
            ...                            'end':[6.0,73.0,108.0]})
            >>>
            >>> # Segemnt the audio file according with the annotations           
            >>> segs_from_annotations(annotations,save_dir)
            Creating segment...... ketos/tests/assets/tmp/from_annot id_2min_0_l_[1].wav
            Creating segment...... ketos/tests/assets/tmp/from_annot id_2min_1_l_[2].wav
            Creating segment...... ketos/tests/assets/tmp/from_annot id_2min_2_l_[1].wav
            
            

    """ 
    create_dir(save_to)
    for i, row in annotations.iterrows():
        start = row.start
        end= row.end
        base_name = os.path.basename(row.filename).split(".wav")[0]
        seg_name = "id_" + base_name + "_" + str(i) + "_l_[" + str(row.label) + "].wav"
        seg_from_time_tag(row.filename, row.start, row.end, seg_name, save_to)
        print("Creating segment......", save_to, seg_name)

def pad_signal(signal,rate, length):
    """Pad a signal with zeros so it has the specified length

        Zeros will be added before and after the signal in approximately equal quantities.
        Args:
            signal: numpy.array
            The signal to be padded

            rate: int
            The sample rate

            length: float
            The desired length for the signal

         Returns:
            padded_signal: numpy.array
            Array with the original signal padded with zeros.

        Examples:
            >>> from ketos.data_handling.data_handling import read_wave
            >>> from ketos.data_handling.data_handling import pad_signal
            >>>
            >>> #Read a very short audio signal
            >>> rate, sig = read_wave("ketos/tests/assets/super_short_1.wav")
            >>> # Calculate its duration (in seconds)
            >>> len(sig)/rate
            0.00075
            >>>
            >>> # Pad the signal
            >>> padded_signal = pad_signal(signal=sig, rate=rate, length=0.5)
            >>> # Now the duration is equal to the 0.5 seconds specified by the 'length' argument
            >>> len(padded_signal)/rate
            0.5
        
    """
    length = length * rate
    input_length = signal.shape[0] 
    
    difference = ( length - input_length) 
    pad1_len =  int(np.ceil(difference/2))
    pad2_len = int(difference - pad1_len)

    pad1 =  np.zeros((pad1_len))
    pad2 =  np.zeros((pad2_len))

    padded_signal =  np.concatenate([pad1,signal,pad2])
    return padded_signal


class AudioSequenceReader:
    """ Reads sequences of audio files and serves them as a merged :class::ketos.audio_processing.audio.AudioSignal.

        Separate audio files are joined together in a single time series. 

        If the source is given as a folder (rather than a list of file names), all wav files from
        the folder will be read.
        
        If the file names have date-time information, the date-time information will be 
        parsed and used to sort the files chronologically. Any gaps will be filled with zeros.

        If the file names do not contain date-time information, the files will be sorted 
        alphabetically (if given as a folder name) or in the order provided (if given as a list 
        of file names).

        Args:
            source: str or list
                File name, list of file names, or directory name 
            recursive_search: bool
                If True, includes .wav files from all subdirectories 
            rate: float
                Sampling rate in Hz
            datetime_stamp: str
                A default datetime to be used in case the file names do not contain datetime information.
                If left to None, the the AudioSequenceReader will try to extract datetime from the filename
                using the 'datetime_fmt' argument.
            datetime_fmt: str
                Format for parsing date-time data from file names. If the file names do not contain
                datetime information and a 'datetime_stamp' is not provided, the current day will be used
                a time starting at 00:00:00:000
            n_smooth: int
                Size of region (number of samples) used for smoothly joining audio signals 
            verbose: bool
                If True, print progress messages during processing

        
        Raises:
            AssertionError:
                If the specified directory does not exist
                If the specified directory does not have any .wav files

        Examples:

        >>> from ketos.data_handling.data_handling import AudioSequenceReader
        >>> # Define the folder containing the audio files
        >>> path_to_files = "ketos/tests/assets/2s_segs"
        >>> # This folder contains 60 files (of 2 seconds each) 
        >>> # We want to read them in chunks of 10 (i.e.: 20-second long signals)       
        >>> 
        >>> # Define the size (in samples) for each batch.
        >>> size = 2000 * 20 # The sampling rate is 2000Hz
        >>> # Create an AudioSequenceReader object
        >>> reader = AudioSequenceReader(source=path_to_files, rate=2000)
        >>> # get the first audio signal
        >>> seq_1 = reader.next(size=size)
        >>> # The length the same as the specified size
        >>> len(seq_1.data)
        40000
        >>> seq_2 = reader.next(size=size)
        >>> len(seq_2.data)
        40000

    """
    def __init__(self, source, recursive_search=False, rate=None, datetime_stamp=None, datetime_fmt=None, n_smooth=100, verbose=False):
        self.rate = rate
        self.n_smooth = n_smooth
        self.times = list()
        self.files = list()
        self.batch = None
        self.signal = None
        self.index = -1
        self.time = None
        self.eof = False
        self.verbose = verbose
        self.load(source=source, recursive_search=recursive_search, datetime_stamp=datetime_stamp, datetime_fmt=datetime_fmt)

    def load(self, source, recursive_search=False, datetime_stamp=None, datetime_fmt=None):
        """
            Reset the reader and load new data.
            
            Args:
                source: str or list
                    File name, list of file names, or directory name 
                recursive_search: bool
                    If true, include wav files from all subdirectories

                datetime_stamp: str
                    A default datetime to be used in case the file names do not contain datetime information.
                    Requires the format to be specified by the 'datetime_fmt' argument.
                    If left to None, the the AudioSequenceReader will try to extract datetime from the filename
                    using the 'datetime_fmt'.
                datetime_fmt: str
                    Format for parsing date-time data from file names. If the file names do not contain
                    datetime information and a 'datetime_stamp' is not provided, the current day will be used
                    a time starting at 00:00:00:000

            Raises:
                AssertionError:
                    If the specified directory does not exist
                    If the specified directory does not have any .wav files

            Examples:

                >>> from glob import glob
                >>> from ketos.data_handling.data_handling import AudioSequenceReader
                >>>
                >>> # Define the folder containing the audio files
                >>> path_to_files = "ketos/tests/assets/2s_segs"
                >>> # Define a list with the 10 files
                >>> list_of_files_1 = glob(path_to_files + "/*" )[0:10]
                >>> # Define another list with 10 different files
                >>> list_of_files_2 = glob(path_to_files + "/*" )[10:20]
                >>>
                >>> # Define the size (in samples) for each batch.
                >>> size = 2000 * 20 # The sampling rate is 2000Hz
                >>>                
                >>> # Create an AudioSequenceReader object with the first list of files
                >>> reader = AudioSequenceReader(source=list_of_files_1, rate=2000)
                >>> # Load the reader with a new source of files
                >>> reader.load(source=list_of_files_1)

        """
        self.files.clear()

        # get list of file names
        fnames = list()
        if isinstance(source, list):
            fnames = source
        else:
            if source[-4:] == '.wav':
                fnames = [source]
            else:
                fnames = find_wave_files(path=source, subdirs=recursive_search)

            # sort file names alphabetically
            fnames = sorted(fnames)

        # check that files exist
        for f in fnames:
            assert os.path.exists(f), " Could not find {0}".format(f)

        # check that we have at least 1 file
        assert len(fnames) > 0, " No wave files found in {0}".format(source)

        # default time stamp
        if datetime_stamp is not None:
            t0 = datetime.datetime.strptime(datetime_stamp, datetime_fmt)  
        else:
            t0 = datetime.datetime.today()
            t0 = datetime.datetime.combine(t0, datetime.datetime.min.time())

        # time stamps
        for f in fnames:
            fmt = datetime_fmt
            p_unix = f.rfind('/')
            p_win = f.rfind('\\')
            p = max(p_unix, p_win)
            folder = f[:p+1]
            if folder is not None and fmt is not None:
                fmt = folder + fmt
            t = parse_datetime(f, fmt)
            if t is None:
                t = t0
            self.files.append([f, t])

        # sort signals in chronological order
        def sorting(y):
            return y[1]
        self.files.sort(key=sorting)

        # reset the reader
        self.reset()

    def _read_file(self, i):
        from ketos.audio_processing.audio import TimeStampedAudioSignal
    
        assert i < len(self.files), "attempt to read file with id {0} but only {1} files have been loaded".format(i, len(self.files))

        if self.verbose:
            print(' File {0} of {1}'.format(i+1, len(self.files)), end="\r")
            
        f = self.files[i]
        s = TimeStampedAudioSignal.from_wav(path=f[0], time_stamp=f[1]) # read in audio data from wav file
        
        if self.rate is not None:
            s.resample(new_rate=self.rate) # resamples

        return s
        
    def _read_next_file(self):
        """
            Read next file, increment file counter, and update time.
        """
        self.index += 1 # increment counter
        if self.index < len(self.files):
            self.signal = self._read_file(self.index) # read audio file
            self.time = self.signal.begin() # start time of this audio file
        else:
            self.signal = None
            self.time = None
            
        if self.signal is None:
            self.eof = True

    def _add_to_batch(self, size, new_batch):
        """
            Add audio from current file to batch.
            
            Args:
                size: int
                    Maximum batch size (number of samples) 
                new_batch: bool
                    Start a new batch or add to existing
        """
        if self.signal.empty():
            self._read_next_file()
           
        if self.signal is None:
            return

        file_is_new = self.signal.begin() == self.time # check if we have already read from this file

        if new_batch:
            if self.batch is not None:
                t_prev = self.batch.end() # end time of the previous batch
            else:
                t_prev = None

            self.batch = self.signal.split(s=size) # create a new batch

            if t_prev is not None and self.batch.begin() < t_prev: 
                self.batch.time_stamp = t_prev # ensure that new batch starts after the end of the previous batch
                
            if file_is_new: 
                self.times.append(self.batch.begin()) # collect times
        else:
            l = len(self.signal.data)
            if file_is_new:
                n_smooth = self.n_smooth
            else:
                n_smooth = 0
            t = self.batch.append(signal=self.signal, n_smooth=n_smooth, max_length=size) # add to existing batch
            if file_is_new and (self.signal.empty() or len(self.signal.data) < l): 
                self.times.append(t) # collect times
        
        if self.signal.empty() and self.index == len(self.files) - 1: # check if there is more data
            self.eof = True 

    def next(self, size=math.inf):
        """
            Read next batch of audio files and merge into a single audio signal. 
            
            If no maximum size is given, all loaded files will be read and merged.
            
            Args:
                size: int
                    Maximum batch size (number of samples) 
                    
            Returns:
                batch: TimeStampedAudioSignal
                    Merged audio signal

            Examples:

                >>> from ketos.data_handling.data_handling import AudioSequenceReader
                >>>
                >>> # Define the folder containing the audio files
                >>> path_to_files = "ketos/tests/assets/2s_segs"
                >>> 
                >>> # Define the size (in samples) for each batch.
                >>> size = 2000 * 20 # The sampling rate is 2000Hz, so each batch will be 20s long
                >>> # Create an AudioSequenceReader object
                >>> reader = AudioSequenceReader(source = path_to_files, rate=2000)
                >>>
                >>> seq1 = reader.next(size=size)
                >>> len(seq1.data)
                40000
                >>> seq2 = reader.next(size=size)
                >>> len(seq2.data)
                40000
        """
        if self.finished():
            return None
        
        length = 0
        
        while length < size and not self.finished():

            self._add_to_batch(size, new_batch=(length==0))
            
            if self.batch is not None:
                length = len(self.batch.data)

        if self.finished() and self.verbose:
            print(' Successfully processed {0} files'.format(len(self.files)))

        return self.batch
        
                
    def finished(self):
        """
            Reader has read all load data.
            
            Returns: 
                x: bool
                True if all data has been process, False otherwise
            
            Example:

                >>> from ketos.data_handling.data_handling import AudioSequenceReader
                >>> # Define the folder containing the audio files
                >>> path_to_files = "ketos/tests/assets/2s_segs"
                >>> # This folder contains 60 files (of 2 seconds each) 
                >>> # We want to read them in chunks of 10 (i.e.: 20-second long signals)       
                >>> 
                >>> # Define the size (in samples) for each batch.
                >>> size = 2000 * 20 # The sampling rate is 2000Hz
                >>> # Create an AudioSequenceReader object
                >>> reader = AudioSequenceReader(source=path_to_files, rate=2000)
                >>>
                >>> # Go through the batches, retriving the merged ausio signal
                >>> # and printing the number of samples in each, until there are no btaches left unprocessed
                >>> while reader.finished() != True:
                ...     seq = reader.next(size=size)
                ...     print(len(seq.data))
                40000
                40000
                40000
                40000
                40000
                30300
                >>> # The last batch generated a signal with 30300 samples only, because there were not 
                >>> # enough files to create a 40000 samples signal as specified by the 'size' argument

            
        """
        return self.eof
    
    def reset(self):
        """
            Go back and start reading from the beginning of the first file.

            Examples:

                >>> from ketos.data_handling.data_handling import AudioSequenceReader
                >>> # Define the folder containing the audio files
                >>> path_to_files = "ketos/tests/assets/2s_segs"
                >>> 
                >>> # Define the size (in samples) for each batch.
                >>> size = 2000 * 60 # The sampling rate is 2000Hz, so each batch will be 60s long
                >>> # Create an AudioSequenceReader object
                >>> reader = AudioSequenceReader(source=path_to_files, rate=2000)
                
                >>> # Here we want 5 signals, even it it means they'll come from repeated batches.
                >>> 
                >>> for i in range(5):
                ...    seq = reader.next(size=size)
                ...    print(len(seq.data))
                ...    if reader.finished(): #When there are no batches left, reset the reader
                ...        reader.reset()
                120000
                110200
                120000
                110200
                120000


                
            
        """
        # reset 
        self.index = -1
        self.times.clear()
        self.eof = False
        self.batch = None

        # read the first file 
        self._read_next_file()

    def log(self):
        """
            Generate summary of all processed data.

            Returns:
                df: pandas DataFrame
                    Table with file names and time stamps

            Example:

                >>> from glob import glob
                >>> from ketos.data_handling.data_handling import AudioSequenceReader
                >>>
                >>> # Define the folder containing the audio files
                >>> path_to_files = "ketos/tests/assets/2s_segs"
                >>> # Define a list with the 10 files that start with 'id_2min_1'
                >>> list_of_files = glob(path_to_files + "/id_2min_1*" )
                >>> list_of_files.sort()
                >>> 
                >>> # Define the size (in samples) for each batch.
                >>> size = 2000 * 20 # The sampling rate is 2000Hz, so each batch will be 20s long
                >>> # Define a default datetime stamp
                >>> datetime_stamp = "1960-06-10 16:30:00.000"
                >>> # Define the datetime format specification
                >>> datetime_fmt = "%Y-%m-%d %H:%M:%S.%f"
                >>>
                >>> # Create an AudioSequenceReader object
                >>> reader = AudioSequenceReader(source = list_of_files, rate=2000, datetime_stamp=datetime_stamp, datetime_fmt=datetime_fmt)
                >>>
                >>> seq1 = reader.next(size=size)
                >>> seq2 = reader.next(size=size)
                >>> reader.log()
                                      time                                             file
                0  1960-06-10 16:30:00.000  ketos/tests/assets/2s_segs/id_2min_10_l_[0].wav
                1  1960-06-10 16:30:01.950  ketos/tests/assets/2s_segs/id_2min_11_l_[0].wav
                2  1960-06-10 16:30:03.900  ketos/tests/assets/2s_segs/id_2min_12_l_[0].wav
                3  1960-06-10 16:30:05.850  ketos/tests/assets/2s_segs/id_2min_13_l_[0].wav
                4  1960-06-10 16:30:07.800  ketos/tests/assets/2s_segs/id_2min_14_l_[0].wav
                5  1960-06-10 16:30:09.750  ketos/tests/assets/2s_segs/id_2min_15_l_[0].wav
                6  1960-06-10 16:30:11.700  ketos/tests/assets/2s_segs/id_2min_16_l_[0].wav
                7  1960-06-10 16:30:13.650  ketos/tests/assets/2s_segs/id_2min_17_l_[0].wav
                8  1960-06-10 16:30:15.600  ketos/tests/assets/2s_segs/id_2min_18_l_[0].wav
                9  1960-06-10 16:30:17.550  ketos/tests/assets/2s_segs/id_2min_19_l_[0].wav
                10 1960-06-10 16:30:19.500   ketos/tests/assets/2s_segs/id_2min_1_l_[0].wav

        """
        n = len(self.times)
        fnames = [x[0] for x in self.files]
        df = pd.DataFrame(data={'time':self.times,'file':fnames[:n]})
        return df


class AnnotationTableReader():
    """ Reads annotation data from csv file

        The csv file should have at least the following columns:

            "filename": file name
            "label": label value (0, 1, 2, ...)
            "start": start time in seconds measured from the beginning of the audio file
            "end": end time in seconds

        In addition, it can the following two optional columns:

            "flow": frequency lower boundary in Hz
            "fhigh": frequency upper boundary in Hz

        Args:
            path: str
                Full path to annotation csv file

        Example:

            >>> # create a pandas dataframe with dummy annotations
            >>> import pandas as pd
            >>> d = {'filename': ['x.wav', 'y.wav'], 'start': [3.0, 4.0], 'end': [17.0, 12.0], 'label': [0, 1]}
            >>> df = pd.DataFrame(data=d)
            >>> # save the dataframe to a csv file
            >>> fname = "ketos/tests/assets/tmp/ann.csv"
            >>> df.to_csv(fname)
            >>> # create an annotation reader
            >>> from ketos.data_handling.data_handling import AnnotationTableReader
            >>> reader = AnnotationTableReader(fname)
            >>> # get the annotations for x.wav
            >>> labels, boxes = reader.get_annotations('x.wav')
            >>> print(labels, boxes)
            [0] [[3.0, 17.0, 0.0, inf]]
    """
    def __init__(self, path):

        self.df = pd.read_csv(path)

        required_cols = ['filename', 'start', 'end', 'label']

        for r in required_cols:
            assert r in self.df.columns, 'column {0} is missing'.format(r)

        self.max_ann = None
        
    def get_max_annotations(self):
        """ Returns the maximum number of annotations attached to any single audio file.
            
            Returns:
                m: int
                    Number of annotations
        """        
        if self.max_ann is not None:
            m = self.max_ann
        else:
            x = self.df['filename'].values
            _, counts = np.unique(x, return_counts=True)
            m = np.max(counts)
            self.max_ann = m

        return m

    def get_annotations(self, filename):
        """ Get annotations associated with the specified file 
            
            Args:
                filename: str
                    File name
                    
            Returns:
                labels: list(int)
                    Labels
                boxes: list(tuple)
                    Boxes
        """
        # select rows with matching file name
        sel = self.df[self.df['filename']==filename]

        m = len(sel)

        # get labels
        labels = sel['label'].values

        # get times
        start = sel['start'].values
        stop  = sel['end'].values

        # get frequencies
        if 'flow' in sel.columns:
            flow = sel['flow'].values
        else:
            flow = np.zeros(m)
        if 'fhigh' in sel.columns:
            fhigh = sel['fhigh'].values        
        else:
            fhigh = np.ones(m) * math.inf

        # construct boxes
        boxes = list()
        for t1,t2,f1,f2 in zip(start, stop, flow, fhigh):
            b = [t1, t2, f1, f2]
            boxes.append(b)

        return labels, boxes


