from . import bit
from . import yota
from . import cnf

from pydub import AudioSegment

import urllib.request
import os
import wget
import glob
import re


def cache_or_download(sampleObj):
    
    """Takes Sample, checks file cache, 
    downloads if needed, returns filename."""
    
    cache_result_found, filename = check_cache(sampleObj)
    if cache_result_found:
        print(f'using file from cache {filename}')
        return(filename)

    else:
        download_mp3(sampleObj)
        m = re.search('[^\/]+?mp3$', sampleObj.link)
        filename = m.group(0)
        return filename

def check_cache(sampleObj):
    filenames = get_sorted_mp3_filenames()
    m = re.search('[^\/]+?mp3$', sampleObj.link)
    sample_filename = m.group(0)
    for item in filenames:
        m = re.search(sample_filename, item)
        if m:
            return True, sample_filename
    return False, ""

def download_mp3(sampleObj):
    # download MP3 file
    print(f'downloading {sampleObj.link}')
    wget.download(sampleObj.link, cnf.package_path)

def cut_sample(sampleObj, filename, keep_original=False):
    """Cut Sample, save Sample MP3."""
    
    # load MP3 into memory (not fast, seconds)
    song = AudioSegment.from_mp3(filename)
    # cut sample from MP3
    cut_sample = song[sampleObj.time_start*1000:sampleObj.time_end*1000]
    try:
        len(sampleObj.title) > 0
    # set default bit title
    except:
        sampleObj.title = 'MyBit'
    clip_filename = sampleObj.title + '_' + str(sampleObj.time_start) + '_' + str(sampleObj.time_end) + '.mp3'
    # write sample to file
    cut_sample.export(clip_filename, format="mp3")
    print(f'sample {clip_filename} successfully cut...')
    
    if keep_original == False:
        os.remove(filename)
        print(f'original file {filename} deleted')

def get_sorted_mp3_filenames():
    """Returns MP3 filename list in order of creation."""
    files_path = cnf.package_path + cnf.os_sep + '*'
    files = sorted(
        glob.iglob(files_path), key=os.path.getctime) 
    mp3_filenames = []
    for filename in files:
        if str(filename).endswith('.mp3'):
            mp3_filenames.append(filename)
    return(mp3_filenames)

def splice_samples(mix_filename, transition_sound=False):
    filenames = get_sorted_mp3_chapters()
    first_clip = AudioSegment.from_mp3(filenames[0])
    if transition_sound:
        transition_clip = AudioSegment.from_mp3(transition_sound)
    for i, item in enumerate(filenames[1:]):
        if transition_sound:
            first_clip += transition_clip
        next_clip = AudioSegment.from_mp3(item)
        first_clip += next_clip
    first_clip.export(mix_filename, format="mp3")
    print(f'successfully wrote file {mix_filename}')

def get_sorted_mp3_chapters():
    """Returns MP3 filename list in order of creation."""
    files_path = os.path.join('.', '*')
    files = sorted(
        glob.iglob(files_path), key=os.path.getctime) 
    mp3_filenames = []
    for filename in files:
        if str(filename).endswith('.mp3'):
            mp3_filenames.append(filename)
    return(mp3_filenames)

def main(sampleObj, keep_original=False, splice=False):

    if isinstance(sampleObj, bit.Mp3):
        filename = cache_or_download(sampleObj)
        if filename and len(filename) > 0:
            filenames = get_sorted_mp3_filenames()
            filename = filenames[0]
            cut_sample(item, filename, keep_original=keep_original)

    elif isinstance(sampleObj, yota.Mixtape):
        for item in sampleObj:
            filename = cnf.package_path + cnf.os_sep + cache_or_download(item)
            cut_sample(item, filename, keep_original=keep_original)
