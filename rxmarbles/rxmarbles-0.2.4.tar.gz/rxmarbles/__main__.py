#!/usr/bin/env python

from __future__ import print_function
from pyparsing import *
import argparse
import importlib
from .svgshapes import *
from .generator import *


def generate_single(diagram, output_file_name, args, theme):
        if args.verbose > 0:
            print ("Generating diagram for '%s' => %s" % (diagram[0], output_file_name))
    
        marbles = diagram[1:]
        r = get_objects(marbles, theme)
        svg = SvgDocument(r, theme, args.scale)
        f = open(output_file_name, "w")
        f.write(svg.get_document())
        f.close()

def generate_batch(diagrams, args, theme):
    for diagram in diagrams:
        output_file_name = diagram.diagram_name + ".svg"
        generate_single(diagram, output_file_name, args, theme)
        
def main():
    parser = argparse.ArgumentParser(description='Generate marbles from textual representation.')
    parser.add_argument('inputfile', metavar='MARBLES-FILE', type=str, help='path to a text file with marble diagrams')
    parser.add_argument('--scale', type=float, default=100.0, help='scale used to control zoom level of the generated images')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='enables verbose mode')
    parser.add_argument('--output', '-o', default=None, type=str, help='sets the file name for the output. Note: only first diagram from the input file will be generated.')
    parser.add_argument('--theme', '-t', default='default', type=str, help='sets the theme used to render SVG output.')
    args = parser.parse_args()
    
    # this is where we import global theme object
    theme = importlib.import_module('rxmarbles.theme.' + args.theme)
    
    diagrams_file_name = args.inputfile
    f = open(diagrams_file_name, "r")
    a = f.read()
    f.close()
    
    diagrams = marble_diagrams.parseString(a)
    
    if not args.output is None:
        output_file_name = args.output
        generate_single(diagrams[0], output_file_name, args, theme)
    else:
        generate_batch(diagrams, args, theme)
            

if __name__ == "__main__":
    main()    
