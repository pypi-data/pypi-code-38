import os, subprocess
import glob
from . import cnf

# Platform-independent re-implementation of dl2.sh

def dl_srt(youtube_url):
    """Takes YouTube URL, downloads .srt subtitles to srt folder,
    returns .srt filename."""

    youtube_hash = youtube_url[-11:]

    def vtt_files():
        """Returns .vtt filenames in folder."""
        files = os.listdir()
        vtt_files = []
        for file in files:
            if str(file).endswith('vtt'):
                vtt_files.append(str(file))
        return vtt_files
    
    # build path to srt folder
    
    srt_path = cnf.srt_folder_path + cnf.os_sep + '*.srt'

    filenames = glob.glob(srt_path)

    # check file cache first
    for filename in filenames:
        if youtube_hash in filename:
            return filename

    os.chdir(cnf.srt_folder_path)

    if cnf.platform == 'linux':
        shell_str = 'youtube-dl "' + youtube_url + '" --skip-download --write-auto-sub 1> /dev/null'
    else:
        shell_str = 'youtube-dl "' + youtube_url + '" --skip-download --write-auto-sub'
    #print('shell_str:', shell_str)
    subprocess.Popen([shell_str], shell=True).wait()
    
    vtt_files_after = vtt_files()
    
    if len(vtt_files_after) > 1:
        ValueError('More than one .vtt files found after download, please remove any .vtt files in the folder ' + srt_path)
    
    elif len(vtt_files_after) == 1:    
        vtt_filename = vtt_files_after[0]
        filename_wo_end = vtt_filename[:-4]
        srt_filename = filename_wo_end  + '.srt'
        # rename the downloaded .vtt to .srt
        os.rename(vtt_filename, srt_filename)

        return srt_filename



