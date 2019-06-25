from __future__ import print_function
import os
import sys
from collections import OrderedDict
from ptcaffe.utils.prototxt import parse_prototxt
from ptcaffe.utils.utils import make_list

def prototxt2graph(protofile):
    blob_dict = dict()
    print('digraph g {')

    net_info = parse_prototxt(protofile)
    layers = net_info['layers']
    props = net_info['props']
    if 'input' in props:
        input_names = make_list(props['input'])
        for input_name in input_names:
            print('    %s [shape = "ellipse"]' % input_name)
            blob_dict[input_name] = input_name
    for layer in layers:
        lname = layer['name']
        ltype = layer['type']
        include_param = layer.get('include', OrderedDict())
        if 'phase' in include_param:
            lname = lname + '_' + include_param['phase']
        if 'bottom' in layer:
            bnames = make_list(layer['bottom'])
        else:
            bnames = []

        if 'top' in layer:
            tnames = make_list(layer['top'])
        else:
            tnames = []

        lnode = "node_%s" % lname.replace('/','_').replace('-','_')
        print('    %s [shape = "box", label = "%s"]' % (lnode, lname.replace('/','_').replace('-','_')))
        for bname in bnames:
            bblob = blob_dict[bname]
            print('    %s -> %s' % (bblob, lnode))
        for tname in tnames:
            if tname in blob_dict:
                blob_dict[tname] = blob_dict[tname] + "_"
            else:
                blob_dict[tname] = tname.replace('/','_').replace('-','_')
            tblob = blob_dict[tname]
            print('    %s [shape = "ellipse", label = "%s"]' % (tblob, tname.replace('/','_').replace('-','_')))
            print('    %s -> %s' % (lnode, tblob))
    print('}')

def prototxt2graph_advanced(protofile, outfile):
    fp = open(outfile, 'w')
    blob_from = dict()
    print('digraph g {', file=fp)

    net_info = parse_prototxt(protofile)
    layers = net_info['layers']
    props = net_info['props']
    if 'input' in props:
        print('    node_data [shape = "box", label = "data"]', file=fp)
        input_names = make_list(props['input'])
        for input_name in input_names:
            blob_from[input_name] = "node_data"
    for layer in layers:
        lname = layer['name']
        include_param = layer.get('include', OrderedDict())
        if 'phase' in include_param:
            lname = lname + '_' + include_param['phase']
        if 'bottom' in layer:
            bnames = make_list(layer['bottom'])
        else:
            bnames = []

        if 'top' in layer:
            tnames = make_list(layer['top'])
        else:
            tnames = []

        lnode = "node_%s" % lname.replace('/','_').replace('-','_')
        print('    %s [shape = "box", label = "%s"]' % (lnode, lname.replace('/','_').replace('-','_')), file=fp)
        for bname in bnames:
            snode = blob_from[bname]
            print('    %s -> %s' % (snode, lnode), file=fp)
        for tname in tnames:
            blob_from[tname] = lnode
    print('}', file=fp)
    fp.close()


def main():
    if len(sys.argv) == 1:
        print("Usage: python prototxt2graph input_prototxt output_image")
        exit()

    prototxt2graph_advanced(sys.argv[1], ".tmp.dot")
    outfile = sys.argv[2] if len(sys.argv) >= 3 else "out.png"

    print("save %s ..." % outfile)
    if outfile.find('.png') >= 0:
        os.system("dot -Tpng -o %s .tmp.dot" % outfile)
    elif outfile.find('.pdf') >= 0:
        os.system("dot -Tpdf -o %s .tmp.dot" % outfile)
    else:
        print("unknown output file type, support .png, .pdf")
        exit()
    print("finish!")

if __name__ == '__main__':
    main()


