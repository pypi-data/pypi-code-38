"""play.py: 

Play a note for given duration.
"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import re
import time
from pathlib import Path
import sounddevice as sd
import soundfile as sf

#  intrument_ = 'KawaiUprightPiano'
#  notedir_ = Path(__file__).resolve().parent / 'data' / intrument_ / 'samples'
notedir_ = Path(__file__).resolve().parent / 'data' / 'FreeSound'
notes_ = {}

def note_name(x):
    xPath = Path(x).name
    noteName = re.search( r'(?P<name>[a-gA-G]#?\d).wav', xPath)
    if not noteName:
        return None
    return noteName.group('name').upper()

def find_note(note):
    global notes_
    global notedir_
    # Build the dictionary of notes only once.
    if not notes_:
        assert notedir_.exists(), notedir_
        notes_ = { note_name(x) : x for x in notedir_.glob( '*.wav') }
    return notes_.get(note, None)

def play_note_aplay(notePath, duration):
    import subprocess
    cmd = ["aplay", str(notePath), "--duration", f'{int(duration):d}' ]
    # Do not block
    subprocess.Popen( cmd , shell = False)
    time.sleep(duration)
    return True

def play_note_sounddevice(notePath, duration):
    data, fs = sf.read(notePath, dtype='float32')
    sd.play(data, fs)
    time.sleep(duration)
    return True

def play(note, duration):
    notePath = find_note(note)
    assert notePath, f"{note} not found: {notes_}" 
    #  return play_note_aplay(notePath, duration)
    return play_note_sounddevice(notePath, duration)

def main():
    note = sys.argv[1]
    duration = float(sys.argv[2])
    #  print( f"[INFO ] Playing {note} for {duration} s" )
    play(note, duration)
    
if __name__ == '__main__':
    main()
