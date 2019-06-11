"""main.py: 
"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

from MyPiano import play_midi
from MyPiano import play_note

class Args: pass 
args = Args()

def main():
    global args
    import argparse
    # Argument parser.
    description = '''MyPiano'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--midifile', '-m'
            , required = False
            , help = 'Midi file to play'
            )
    parser.add_argument('--note', '-n'
            , required = False, default = 'A0'
            , help = 'A note to play'
            )
    parser.add_argument('--duration', '-d'
            , required = False, default = 1.0, type=float
            , help = 'Note duration (use it with --note)'
            )
    parser.parse_args(namespace=args)

    if args.midifile:
        play_midi.play(args.midifile)
    elif args.note:
        play_note.play(args.note, args.duration)
    else:
        raise RuntimeError("Argument is not supported")

if __name__ == '__main__':
    main()
