#!/usr/bin/env python
#-*- coding:utf-8 -*-


from __future__ import print_function, unicode_literals, division, absolute_import

import getopt
import io
import sys
import os
import mistune
try:
    from pynlpl.formats import folia
except:
    print("ERROR: pynlpl not found, please obtain PyNLPL from the Python Package Manager ($ sudo easy_install pynlpl) or directly from github: $ git clone git://github.com/proycon/pynlpl.git", file=sys.stderr)
    sys.exit(2)

def usage():
    print("markdown2folia",file=sys.stderr)
    print("  by Maarten van Gompel (proycon)",file=sys.stderr)
    print("  Tilburg University / Radboud University Nijmegen",file=sys.stderr)
    print("  2014 - Licensed under GPLv3",file=sys.stderr)
    print("",file=sys.stderr)
    print("This conversion script converts a markdown document to FoLiA XML",file=sys.stderr)
    print("",file=sys.stderr)
    print("Usage: markdown2folia [options] file",file=sys.stderr)
    print("",file=sys.stderr)
    print("Input parameters",file=sys.stderr)
    print("  -e [filename]                Encoding of the markdown file (default: utf-8",file=sys.stderr)
    print("Parameters for output:",file=sys.stderr)
    print("  -o [filename]                Output to a single file (instead of default stdout)",file=sys.stderr)



class MD2FoLiARenderer(mistune.Renderer):
    def paragraph(self, text):
        return '<p><t>' + text + '</t></p>'

    def block_code(self, code, lang):
        if lang:
            return '<gap><desc>code (' + lang + ')</desc><content>' + code + '</content></gap>'
        else:
            return '<gap><desc>code</desc><content>' + code + '</content></gap>'

def process(filename, encoding, outputfile = None):
    print("Converting " + filename, file=sys.stderr)
    md = mistune.Markdown(renderer=MD2FoLiARenderer())
    with io.open(filename,'r', encoding=encoding) as f:
        if outputfile:
            with io.open(outputfile,'w',encoding='utf-8') as fout:
                fout.write(md.render(f.read()) + "\n")
        else:
            print(md.render(f.read()))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:e:", ["help"])
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        usage()
        sys.exit(2)


    outputfile = None
    encoding= 'utf-8'


    for o, a in opts:
        if o == '-h' or o == '--help':
            usage()
            sys.exit(0)
        elif o == '-o':
            outputfile = a
        elif o == '-e':
            encoding = a
        else:
            raise Exception("No such option: " + o)




    if args:
        x = args[0]
        if os.path.isfile(x):
            process(x, encoding, outputfile)
        else:
            print("ERROR: File not found: " + x,file=sys.stderr)
            sys.exit(3)
    else:
        print("ERROR: Nothing to do, specify a file",file=sys.stderr)

    if outputfile: outputfile.close()

if __name__ == "__main__":
    main()
