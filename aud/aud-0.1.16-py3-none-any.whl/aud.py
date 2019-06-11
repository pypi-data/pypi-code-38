"""
This is the documentation for aud
"""
#import .AudFile
#import .AudDir
#import .AudLib
from aud.AudFile import AudFile
from aud.AudDir import AudDir
from aud.AudLib import setupLogger, createFolder
import begin

@begin.start(auto_convert=True)
def main(file: 'File' = "", dir: 'Directory' = "", rename: 'Rename' = [], convert: 'Convert' = [], pad: 'Padding' = [], metadata: 'Metadata Tags' = [], extensions: 'Extensions' = []):
    '''
    aud: Quick tools for an audio studio environment
    '''
    logger = setupLogger()
    ## Decipher arguments and run the right command
    ## Designed to work well in the interpreter
    logger.debug("Import to start")

    ### SINGLE FILE COMMANDS ###
    if file != "":
        _file = AudFile(file)
        ## RENAME MODULES ##
        if rename[0].lower() == "lower":
            _file.renameLower()
        elif rename[0].lower() == "upper":
            _file.renameUpper()
        elif rename[0].lower() == "replacespaces":
            _file.renameReplaceSpaces()
        elif rename[0].lower() == "prepend":
            prefix = rename[1]
            _file.renamePrepend(prefix)

        ## METADTA MODULES ##
        if metadata != []:
            _file.metadata(metadata)

        ## FFMPEG MODULES ##
        ext = ".wav"
        sr = "44100"
        bd = "16"
        dr = "320k"
        if convert != []:
            if convert['extension']:
                ext = convert['extension']
            if convert['samplerate']:
                sr = convert['samplerate']
            if convert['bitdepth']:
                bd = convert['bitdepth']
            if convert['bitrate']:
                dr = convert['bitrate']
            _file.convertTo(_extension=ext, _target_samplerate=sr, _target_bitdepth=bd, _target_bitrate=br)

        _in = 0
        _out = 0
        if pad != []:
            if pad['in']:
                _in = pad['in']
            if pad['out']:
                _out = pad['out']
            _file.pad(_in=_in, _out=_out)

    ### DIR COMMANDS ###
    elif dir != "":
        _dir = AudDir(dir)
        # load extensions
        if extensions != []:
            _dir.extenstions = extensions

        ## RENAME MODULES ##
        if rename[0].lower() == "lower":
            _dir.renameLower()
        elif rename[0].lower() == "upper":
            _dir.renameUpper()
        elif rename[0].lower() == "replacespaces":
            _dir.renameReplaceSpaces()
        elif rename[0].lower() == "prepend":
            prefix = rename[1]
            _dir.renamePrepend(prefix)

        ## METADTA MODULES ##
        if metadata != []:
            _dir.metadata(metadata)

        ## FFMPEG MODULES ##
        ext = ".wav"
        sr = "44100"
        bd = "16"
        dr = "320k"
        if convert != []:
            if convert['extension']:
                ext = convert['extension']
            if convert['samplerate']:
                sr = convert['samplerate']
            if convert['bitdepth']:
                bd = convert['bitdepth']
            if convert['bitrate']:
                dr = convert['bitrate']
            _dir.convertTo(_extension=ext, _target_samplerate=sr, _target_bitdepth=bd, _target_bitrate=br)

        _in = 0.0
        _out = 0.0
        if pad != []:
            if pad['in']:
                _in = pad['in']
            if pad['out']:
                _out =pad['out']
            _dir.pad(_in=_in, _out=_out)
