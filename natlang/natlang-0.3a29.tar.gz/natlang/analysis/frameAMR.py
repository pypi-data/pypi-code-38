# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Provide a brief analysis of propbank-frame-arg-descr.txt from AMR2.0 dataset
# Simon Fraser University
# Jetic Gu
#
#
from __future__ import absolute_import
import os
import sys
import inspect
import argparse

from natlang.loader import DataLoader

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description="""AMR 2.0 Frame Analyser""")
    ap.add_argument(
        "filename", metavar='FILENAME', nargs='+',
        help="""AMR 2.0 frame file. Multiple files supported.
                If bash reports argument list too long, use quotation marks""")
    args = ap.parse_args()

    loader = DataLoader("semanticFrame")
    frames = loader.load(args.filename)

    print("----- Statistics -----")
    print("# of frames:          " + str(len(frames)))
    args = {}
    for frame, a in frames:
        for ar in a:
            if ar not in args:
                args[ar] = {}
            args[ar][frame] = a[ar]
    print("# of different ARGs:  " + str(len(args)))
    for arg in args:
        print("# of frames with " + arg + ": " + str(len(args[arg])))
    frames = dict(frames)
    words = {}
    for frame in frames:
        try:
            if "." in frame:
                word, frameId = tuple(frame.rsplit(".", 1))
            elif "-" in frame:
                word, frameId = tuple(frame.rsplit("-", 1))
            else:
                sys.stderr.write(
                    "main [WARN]: frame without ID: " + frame + "\n")
                word, frameId = (frame, "NaN")
        except ValueError:
            print(frame)
            raise
        if word not in words:
            words[word] = {}
        words[word][frameId] = frames[frame]
    frameCount = sorted([(len(words[word]), word) for word in words],
                        key=lambda x: -x[0])
    print("Most frames in a word: " + str(frameCount[0]))
    if bool(getattr(sys, 'ps1', sys.flags.interactive)):
        print("Use frames (dict of frameName:{argName, description})) to see" +
              " frames.")
        print("Use words (dict of word:frameId:{argName, description})) to " +
              "see frames of a word.")
        print("Use args (dict of arg:frameName:description) to see all args")
        print("Use framesCount to see sorted list of words (based on # of " +
              "frames)")
