"""play_song.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import time
import mido
import MyPiano.midi2notes as midi2notes
import MyPiano.play_note as play_note

def play(midifile):
    t0 = time.time()
    for m in mido.MidiFile(midifile).play():
        if m.type == 'note_on':
            n = m.note
            nName = midi2notes.notes_.get(n, None)[0]
            t = time.time() - t0
            print( f"[{t:.3f}] Playing {nName}" )
            play_note.play(nName, m.time)
        else:
            time.sleep(m.time)

if __name__ == '__main__':
    midifile = sys.argv[1]
    play(midifile)

