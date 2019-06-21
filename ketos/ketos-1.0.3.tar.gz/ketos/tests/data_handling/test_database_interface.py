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

""" Unit tests for the database_interface module within the ketos library
"""
import pytest
import tables
import os
import ketos.data_handling.database_interface as di
import ketos.data_handling.data_handling as dh
from ketos.audio_processing.spectrogram import MagSpectrogram, Spectrogram


current_dir = os.path.dirname(os.path.realpath(__file__))
path_to_assets = os.path.join(os.path.dirname(current_dir),"assets")
path_to_tmp = os.path.join(path_to_assets,'tmp')


@pytest.mark.test_open_table
def test_open_non_existing_table():
    """ Test if the expected exception is raised when the table does not exist """
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp1_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # open non-existing table
    with pytest.raises(tables.NoSuchNodeError):
        tbl = di.open_table(h5file=h5file, table_path='/group_1/table_1')
        assert tbl == None
    # clean
    h5file.close()
    os.remove(fpath)

@pytest.mark.test_open_table
def test_open_existing_table():
    """ Test if the expected table is open """
    # open h5 file
    fpath = os.path.join(path_to_assets, '15x_same_spec.h5')
    h5file = tables.open_file(fpath, 'r')
    # open non-existing table
    tbl = di.open_table(h5file=h5file, table_path='/train/species1')
    assert isinstance(tbl, tables.table.Table)
    assert tbl.nrows == 15
    # clean
    h5file.close()
   

@pytest.mark.test_create_table
def test_create_table():
    """Test if a table and its group are created"""
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp2_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    _ = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=(20,60))
    group = h5file.get_node("/group_1")
    assert isinstance(group, tables.group.Group)
    table = h5file.get_node("/group_1/table_1")
    assert isinstance(table, tables.table.Table)    
    # clean
    h5file.close()
    os.remove(fpath)

@pytest.mark.test_create_table
def test_create_table_existing():
    """Test if a table is open when it already exists"""
    # open h5 file
    fpath = os.path.join(path_to_assets, '15x_same_spec.h5')
    h5file = tables.open_file(fpath, 'a')
    # create table
    _ = di.create_table(h5file=h5file, path='/train/', name='species1', shape=(20,60))
    table = h5file.get_node("/train/species1")
    assert table.nrows == 15
    assert table[0]['data'].shape == (2413,201)
    assert table[1]['id'] == b'1'
    # clean
    h5file.close()
    

@pytest.mark.test_write_spec
def test_write_spec(sine_audio):
    """Test if spectrograms are written and have the expected ids"""
    # create spectrogram    
    spec = MagSpectrogram(sine_audio, 0.5, 0.1)
    # add annotation
    spec.annotate(labels=(1,2), boxes=((1,2,3,4),(1.5,2.5,3.5,4.5)))
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp3_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    tbl = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=spec.image.shape)
    # write spectrogram to table
    di.write_spec(table=tbl, spec=spec) # should return None after writing spectrogram to table
    # write spectrogram to table with id
    di.write_spec(table=tbl, spec=spec, id='123%')

    assert tbl[0]['id'].decode() == ''
    assert tbl[0]['labels'].decode() == '[1,2]'
    assert tbl[0]['boxes'].decode() == '[[1.0,2.0,3.0,4.0],[1.5,2.5,3.5,4.5]]'

    assert tbl[1]['id'].decode() == '123%'
    assert tbl[1]['labels'].decode() == '[1,2]'
    assert tbl[1]['boxes'].decode() == '[[1.0,2.0,3.0,4.0],[1.5,2.5,3.5,4.5]]'

    h5file.close()
    os.remove(fpath)

@pytest.mark.test_write_spec
def test_write_spec_TypeError(sine_audio):
    """Test if a type error is raised when trying to pass an object that isn't an instance of Spectrogram (or its subclasses)"""
    sine_audio.annotate(labels=(1,2), boxes=((1,2,3,4),(1.5,2.5,3.5,4.5)))
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp4_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    tbl = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=sine_audio.data.shape)
    # write spectrogram to table
    with pytest.raises(TypeError):
        di.write_spec(table=tbl, spec=sine_audio)
       
    assert tbl.nrows == 0
    
    h5file.close()
    os.remove(fpath)


@pytest.mark.test_extract
def test_extract(sine_audio):
    """ Test if annotations are correctly extracted from spectrograms"""
    # create spectrogram    
    spec1 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec1.annotate(labels=(1), boxes=((1.001, 1.401, 50, 300)))
    spec2 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec2.annotate(labels=(1), boxes=((1.1, 1.5)))
    tshape_orig = spec1.image.shape[0]
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp5_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    tbl = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=spec1.image.shape)
    # write spectrograms to table
    di.write_spec(table=tbl, spec=spec1, id='1')  # Box: 1.0-1.4 s & 50-300 Hz
    di.write_spec(table=tbl, spec=spec2, id='2')  # Box: 1.1-1.5 s Hz
   
    # get segments with label=1
    selection, complements = di.extract(table=tbl, label=1, min_length=0.8, fpad=False, center=True)
    assert len(selection) == 2
    assert len(complements) == 2
    
    assert selection[0].image.shape == (40,51)
    assert complements[0].image.shape[0] == (spec1.image.shape[0] - selection[0].image.shape[0])

    assert selection[1].image.shape == (40,4411)
    assert complements[1].image.shape[0] == (spec2.image.shape[0] - selection[1].image.shape[0])

    tshape = int(0.8 / spec1.tres)
    assert selection[0].image.shape[0] == tshape
    fshape = int(250 / spec1.fres) + 1
    assert selection[0].image.shape[1] == fshape
    assert selection[0].boxes[0][0] == pytest.approx(0.201, abs=0.000001)
    assert selection[0].boxes[0][1] == pytest.approx(0.601, abs=0.000001)

    h5file.close()
    os.remove(fpath)



@pytest.mark.test_parse_labels
def test_parse_labels(sine_audio):
    """Test if labels with the expected format are correctly parsed"""
    # create spectrogram    
    spec1 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec1.annotate(labels=(1), boxes=[[1.001, 1.401, 50, 300]])
    spec2 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec2.annotate(labels=(1,2), boxes=[[1.1, 1.5], [1.6, 1.7]])
    tshape_orig = spec1.image.shape[0]
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp6_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    tbl = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=spec1.image.shape)
    # write spectrograms to table
    di.write_spec(table=tbl, spec=spec1, id='1')  # Box: 1.0-1.4 s & 50-300 Hz
    di.write_spec(table=tbl, spec=spec2, id='2')  # Box: 1.1-1.5 s Hz
    #parse labels
    labels = tbl[0]['labels']
    labels = di.parse_labels(labels)
    assert type(labels) == list
    assert labels == [1]

    labels = tbl[1]['labels']
    labels = di.parse_labels(labels)
    assert type(labels) == list
    assert labels == [1,2]

    h5file.close()
    os.remove(fpath)
    

@pytest.mark.test_parse_boxes
def test_parse_boxes(sine_audio):
    """Test if boxes with the expected format are correctly parsed"""
    # create spectrogram    
    spec1 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec1.annotate(labels=(1), boxes=[[1.001, 1.401, 50, 300]])
    spec2 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec2.annotate(labels=(1,2), boxes=[[1.1, 1.5], [1.6, 1.7]])
    tshape_orig = spec1.image.shape[0]
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp7_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    tbl = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=spec1.image.shape)
    # write spectrograms to table
    di.write_spec(table=tbl, spec=spec1, id='1')  # Box: 1.0-1.4 s & 50-300 Hz
    di.write_spec(table=tbl, spec=spec2, id='2')  # Box: 1.1-1.5 s Hz
    # parse boxes
    boxes = tbl[0]['boxes']
    boxes = di.parse_boxes(boxes)
    assert type(boxes) == list
    assert boxes == [[1.001, 1.401, 50, 300]]

    boxes = tbl[1]['boxes']
    boxes = di.parse_boxes(boxes)
    assert type(boxes) == list
    assert boxes == [[1.1, 1.5, 0.0, 22050.0], [1.6, 1.7, 0.0, 22050.0]]

    h5file.close()
    os.remove(fpath)


@pytest.mark.filter_by_label
def test_filter_by_label(sine_audio):
    """ Test if filter_by_label works when providing an int or list of ints as the label argument"""
    # create spectrogram  
    spec1 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec1.annotate(labels=(1), boxes=((1.0, 1.4, 50, 300)))

    spec2 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec2.annotate(labels=(2), boxes=((1.0, 1.4, 50, 300)))

    spec3 = MagSpectrogram(sine_audio, winlen=0.2, winstep=0.02)
    spec3.annotate(labels=(2,3), boxes=((1.0, 1.4, 50, 300), (2.0, 2.4, 80, 200)))
    # open h5 file
    fpath = os.path.join(path_to_tmp, 'tmp8_db.h5')
    h5file = tables.open_file(fpath, 'w')
    # create table
    tbl = di.create_table(h5file=h5file, path='/group_1/', name='table_1', shape=spec1.image.shape)
    # write spectrogram to table
    di.write_spec(table=tbl, spec=spec1, id='A') 
    di.write_spec(table=tbl, spec=spec1, id='B') 
    di.write_spec(table=tbl, spec=spec2, id='C') 
    di.write_spec(table=tbl, spec=spec2, id='D')
    di.write_spec(table=tbl, spec=spec3, id='E') 
    

    # select spectrograms containing the label 1
    rows = di.filter_by_label(table=tbl, label=1)
    assert len(rows) == 2
    assert rows == [0,1]

    # select spectrograms containing the label 2
    rows = di.filter_by_label(table=tbl, label=[2])
    assert len(rows) == 3
    assert rows == [2,3,4]

    # select spectrograms containing the labels 1 or 3
    rows = di.filter_by_label(table=tbl, label=[1,3])
    assert len(rows) == 3
    assert rows == [0,1,4]

    h5file.close()
    os.remove(fpath)


@pytest.mark.filter_by_label
def test_filter_by_label_raises(sine_audio):
    """ Test if filter_by_label raises expected exception when the the label argument is of the wrong type"""
    # open h5 file
    fpath = os.path.join(path_to_assets, '15x_same_spec.h5')
    h5file = tables.open_file(fpath, 'r')
    tbl = di.open_table(h5file,"/train/species1")
    
    with pytest.raises(TypeError):
        di.filter_by_label(table=tbl, label='a')
    with pytest.raises(TypeError):
        di.filter_by_label(table=tbl, label=['a','b'])
    with pytest.raises(TypeError):        
        di.filter_by_label(table=tbl, label='1')
    with pytest.raises(TypeError):    
        di.filter_by_label(table=tbl, label='1,2')
    with pytest.raises(TypeError):    
        di.filter_by_label(table=tbl, label=b'1')
    with pytest.raises(TypeError):    
        di.filter_by_label(table=tbl, label=1.0)
    with pytest.raises(TypeError):    
        di.filter_by_label(table=tbl, label= (1,2))
    with pytest.raises(TypeError):    
        di.filter_by_label(table=tbl, label=[1.0,2])
   
    h5file.close()



@pytest.mark.load_specs
def test_load_specs_no_index_list():
    """Test if load specs loads the entire table if index_list is None""" 

    fpath = os.path.join(path_to_assets, '15x_same_spec.h5')
    h5file = tables.open_file(fpath, 'r')
    tbl = di.open_table(h5file,"/train/species1")
    
    selected_specs = di.load_specs(tbl)
    assert len(selected_specs) == tbl.nrows
    is_spec = [isinstance(item, Spectrogram) for item in selected_specs]
    assert all(is_spec)
    
    h5file.close()

@pytest.mark.load_specs
def test_load_specs_with_index_list():
    """Test if load_specs loads the spectrograms specified by index_list""" 

    fpath = os.path.join(path_to_assets, '15x_same_spec.h5')
    h5file = tables.open_file(fpath, 'r')
    tbl = di.open_table(h5file,"/train/species1")
    
    selected_specs = di.load_specs(tbl, index_list=[0,3,14])
    assert len(selected_specs) == 3
    is_spec = [isinstance(item, Spectrogram) for item in selected_specs]
    assert all(is_spec)

    h5file.close()

def test_create_spec_database_with_default_args():

    output_file = os.path.join(path_to_assets, 'tmp/db_spec.h5')
    input_dir = os.path.join(path_to_assets, 'wav_files/')

    di.create_spec_database(output_file=output_file, input_dir=input_dir)

    path = os.path.join(path_to_assets, 'tmp/db_spec.h5')
    fil = tables.open_file(path, 'r')
    tbl = di.open_table(fil, "/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 2
    assert specs[0].tres == 0.02
    tbl = di.open_table(fil, "/subf/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 1
    assert specs[0].tres == 0.02

    fil.close()

def test_create_spec_database_with_size_limit():

    output_file = os.path.join(path_to_assets, 'tmp/db2_spec.h5')
    input_dir = os.path.join(path_to_assets, 'wav_files/')

    di.create_spec_database(output_file=output_file, input_dir=input_dir, max_size=5E6)

    path = os.path.join(path_to_assets, 'tmp/db2_spec_000.h5')
    fil = tables.open_file(path, 'r')
    tbl = di.open_table(fil, "/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 1
    tbl = di.open_table(fil, "/subf/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 1
    fil.close()

    path = os.path.join(path_to_assets, 'tmp/db2_spec_001.h5')
    fil = tables.open_file(path, 'r')
    tbl = di.open_table(fil, "/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 1
    fil.close()

def test_create_spec_database_with_annotations():

    csvfile = os.path.join(path_to_assets, 'tmp/ann.csv')
    output_file = os.path.join(path_to_assets, 'tmp/db3_spec.h5')
    input_dir = os.path.join(path_to_assets, 'wav_files/')

    # create annotations
    import pandas as pd
    d = {'filename': ['w1.wav'], 'start': [0.1], 'end': [0.7], 'label': [1]}
    df = pd.DataFrame(data=d)
    df.to_csv(csvfile)

    # create database
    di.create_spec_database(output_file=output_file, input_dir=input_dir, annotations_file=csvfile)

    path = os.path.join(path_to_assets, 'tmp/db3_spec.h5')
    fil = tables.open_file(path, 'r')
    tbl = di.open_table(fil, "/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 2
    assert len(specs[0].labels) == 1
    assert specs[0].labels[0] == 1
    tbl = di.open_table(fil, "/subf/spec")
    specs = di.load_specs(tbl)
    assert len(specs) == 1
    assert len(specs[0].labels) == 0

    fil.close()

def test_init_spec_writer():
    out = os.path.join(path_to_assets, 'tmp/db4.h5')
    di.SpecWriter(output_file=out)

def test_spec_writer_can_write_one_spec(sine_audio):
    out = os.path.join(path_to_assets, 'tmp/db5.h5')
    writer = di.SpecWriter(output_file=out)
    spec = MagSpectrogram(sine_audio, 0.5, 0.1)
    writer.write(spec=spec)
    writer.close()
    fname = os.path.join(path_to_assets, 'tmp/db5.h5')
    fil = tables.open_file(fname, 'r')
    assert '/spec' in fil
    specs = di.load_specs(fil.root.spec)
    assert len(specs) == 1

def test_spec_writer_can_write_two_specs_to_same_node(sine_audio):
    out = os.path.join(path_to_assets, 'tmp/db6.h5')
    writer = di.SpecWriter(output_file=out)
    spec = MagSpectrogram(sine_audio, 0.5, 0.1)
    writer.write(spec=spec)
    writer.write(spec=spec)
    writer.close()
    fname = os.path.join(path_to_assets, 'tmp/db6.h5')
    fil = tables.open_file(fname, 'r')
    assert '/spec' in fil
    specs = di.load_specs(fil.root.spec)
    assert len(specs) == 2

def test_spec_writer_can_write_several_specs_to_different_nodes(sine_audio):
    out = os.path.join(path_to_assets, 'tmp/db7.h5')
    writer = di.SpecWriter(output_file=out)
    spec = MagSpectrogram(sine_audio, 0.5, 0.1)
    writer.write(spec=spec, path='/first', name='test')
    writer.write(spec=spec, path='/first', name='test')
    writer.write(spec=spec, path='/second', name='temp')
    writer.write(spec=spec, path='/second', name='temp')
    writer.write(spec=spec, path='/second', name='temp')
    writer.close()
    fname = os.path.join(path_to_assets, 'tmp/db7.h5')
    fil = tables.open_file(fname, 'r')
    assert '/first/test' in fil
    assert '/second/temp' in fil
    specs = di.load_specs(fil.root.first.test)
    assert len(specs) == 2
    specs = di.load_specs(fil.root.second.temp)
    assert len(specs) == 3

def test_spec_writer_splits_into_several_files_when_max_size_is_reached(sine_audio):
    out = os.path.join(path_to_assets, 'tmp/db8.h5')
    writer = di.SpecWriter(output_file=out, max_size=1E6) # max size: 1 Mbyte
    spec = MagSpectrogram(sine_audio, 0.5, 0.1)
    writer.write(spec=spec)
    writer.write(spec=spec)
    writer.write(spec=spec)
    writer.close()

    fname = os.path.join(path_to_assets, 'tmp/db8_000.h5')
    fil = tables.open_file(fname, 'r')
    assert '/spec' in fil
    specs = di.load_specs(fil.root.spec)
    assert len(specs) == 2

    fname = os.path.join(path_to_assets, 'tmp/db8_001.h5')
    fil = tables.open_file(fname, 'r')
    assert '/spec' in fil
    specs = di.load_specs(fil.root.spec)
    assert len(specs) == 1

def test_spec_writer_change_directory(sine_audio):
    out = os.path.join(path_to_assets, 'tmp/db9.h5')
    writer = di.SpecWriter(output_file=out)
    spec = MagSpectrogram(sine_audio, 0.5, 0.1)
    writer.cd('/home/fish')
    writer.write(spec=spec)
    writer.write(spec=spec)
    writer.write(spec=spec)
    writer.cd('/home/whale')
    writer.write(spec=spec)
    writer.write(spec=spec)
    writer.close()
    fname = os.path.join(path_to_assets, 'tmp/db9.h5')
    fil = tables.open_file(fname, 'r')
    assert '/home/fish' in fil
    assert '/home/whale' in fil
    specs = di.load_specs(fil.root.home.fish)
    assert len(specs) == 3
    specs = di.load_specs(fil.root.home.whale)
    assert len(specs) == 2
