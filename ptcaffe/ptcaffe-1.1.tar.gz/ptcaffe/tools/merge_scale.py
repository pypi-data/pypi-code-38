# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by diwanying
# --------------------------------------------------------

from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.prototxt import save_prototxt, parse_prototxt
from collections import OrderedDict
import copy
import torch

def make_list(obj):
    return obj if isinstance(obj, list) else [obj]

def get_lname(layer):
    lname = layer['name']
    if 'include' in layer and 'phase' in layer['include']:
        lname = lname + '@' + layer['include']['phase']
    return lname

def merge_scale_proto(input_protofile, output_prototxt):
    input_net_info = parse_prototxt(input_protofile)
    layers = input_net_info['layers']
    # create layer_from
    blob_from = dict()
    layer_from = OrderedDict()
    lname_index = dict()
    index = 0
    for layer in layers:
        lname = get_lname(layer)
        lname_index[lname] = index
        if 'bottom' in layer:
            bnames = make_list(layer['bottom'])
            from_layers = []
            for bname in bnames:
                if bname in blob_from:
                    from_layers.append(blob_from[bname])
            layer_from[lname] = from_layers
        else:
            layer_from[lname] = []
        assert('top' in layer)
        tnames = make_list(layer['top'])
        for tname in tnames:
            blob_from[tname] = lname
        index += 1

    # absorb bn-scale in layers
    new_net_info = copy.deepcopy(input_net_info)
    new_layers = new_net_info['layers']
    del_lnames = []
    saved_bn_lnames = []
    for lname in layer_from.keys():
        index = lname_index[lname]
        layer = layers[index]
        ltype = layer['type']
        if ltype == 'Scale':
            scale_lname = lname
            scale_layer = layer
            scale_from_layers = layer_from[scale_lname]
            if len(scale_from_layers) == 1:
                bn_lname = scale_from_layers[0]
                bn_layer = layers[lname_index[bn_lname]]
                bn_type  = bn_layer['type']
                if bn_type == 'BatchNorm':
                    del_lnames.append(scale_lname)
                    bn_params = bn_layer.get('batch_norm_param', OrderedDict())
                    eps = float(bn_params.get('eps', 1e-5))
                    bn_from_layers = layer_from[bn_lname]

                    new_bn_layer = new_layers[lname_index[bn_lname]]
                    new_scale_layer = new_layers[lname_index[scale_lname]]
                    new_bn_layer['top'] = new_scale_layer['top']
                    new_bn_params = copy.deepcopy(bn_params)
                    new_bn_params['affine'] = 'true'
                    new_bn_layer['batch_norm_param'] = new_bn_params
                    saved_bn_lnames.append(bn_lname)

    remaining_layers = []
    for lname in layer_from.keys():
        if lname not in del_lnames:
            index = lname_index[lname]
            layer = new_layers[index]
            remaining_layers.append(layer)
    new_net_info['layers'] = remaining_layers
    print('save %s' % output_prototxt)
    save_prototxt(new_net_info, output_prototxt)

def merge_scale(input_protofile, input_ptmodel, output_prototxt, output_ptmodel):
    input_net = CaffeNet(input_protofile)
    input_net.load_model(input_ptmodel)
    layers = input_net.net_info['layers']
    # create layer_from
    blob_from = dict()
    layer_from = OrderedDict()
    lname_index = dict()
    index = 0
    for layer in layers:
        assert('include' not in layer)
        lname = get_lname(layer)
        lname_index[lname] = index
        if 'bottom' in layer:
            bnames = make_list(layer['bottom'])
            from_layers = []
            for bname in bnames:
                if bname in blob_from:
                    from_layers.append(blob_from[bname])
            layer_from[lname] = from_layers
        else:
            layer_from[lname] = []
        assert('top' in layer)
        tnames = make_list(layer['top'])
        for tname in tnames:
            blob_from[tname] = lname
        index += 1

    # absorb bn-scale in layers
    new_net_info = copy.deepcopy(input_net.net_info)
    new_layers = new_net_info['layers']
    del_lnames = []
    saved_bn_lnames = []
    saved_bn_weights = dict()
    saved_bn_biases = dict()
    for lname in layer_from.keys():
        index = lname_index[lname]
        layer = layers[index]
        ltype = layer['type']
        if ltype == 'Scale':
            scale_lname = lname
            scale_layer = layer
            scale_from_layers = layer_from[scale_lname]
            if len(scale_from_layers) == 1:
                bn_lname = scale_from_layers[0]
                bn_layer = layers[lname_index[bn_lname]]
                bn_type  = bn_layer['type']
                if bn_type == 'BatchNorm':
                    del_lnames.append(scale_lname)
                    bn_params = bn_layer.get('batch_norm_param', OrderedDict())
                    eps = float(bn_params.get('eps', 1e-5))
                    bn_from_layers = layer_from[bn_lname]

                    saved_bn_weights[bn_lname] = input_net.models[scale_lname].weight.data
                    saved_bn_biases[bn_lname] = input_net.models[scale_lname].bias.data

                    new_bn_layer = new_layers[lname_index[bn_lname]]
                    new_scale_layer = new_layers[lname_index[scale_lname]]
                    new_bn_layer['top'] = new_scale_layer['top']
                    new_bn_params = copy.deepcopy(bn_params)
                    new_bn_params['affine'] = 'true'
                    new_bn_layer['batch_norm_param'] = new_bn_params
                    saved_bn_lnames.append(bn_lname)

    remaining_layers = []
    for lname in layer_from.keys():
        if lname not in del_lnames:
            index = lname_index[lname]
            layer = new_layers[index]
            remaining_layers.append(layer)
    new_net_info['layers'] = remaining_layers
    print('save %s' % output_prototxt)
    save_prototxt(new_net_info, output_prototxt)
    output_net = CaffeNet(output_prototxt)
    input_state_dict = input_net.state_dict()
    output_state_dict = output_net.state_dict()
    for key in output_state_dict.keys():
        if key in input_state_dict.keys():
            output_state_dict[key][:] = input_state_dict[key][:]
    for lname in output_net.models.keys():
        if lname in saved_bn_lnames:
            output_net.models[lname].weight.data.copy_(saved_bn_weights[lname])
            output_net.models[lname].bias.data.copy_(saved_bn_biases[lname])
    print('save %s' % output_ptmodel)
    output_net.save_model(output_ptmodel)

    # verify networks
    props = input_net.net_info['props']
    assert('input' in props)
    if type(props['input']) != list:
        if 'input_shape' in props:
            dims = props['input_shape']['dim']
        elif 'input_dim' in props:
            dims = props['input_dim']
        input_shape = [int(dim) for dim in dims]
    input = torch.rand(input_shape)
    input_net.set_automatic_outputs()
    output_net.set_automatic_outputs()
    input_net.eval()
    output_net.eval()
    orig_output = input_net(input)
    noscale_output = output_net(input)
    diff = (orig_output - noscale_output).abs().mean()
    print('differene = %f' % diff)

def main():
    import sys
    if len(sys.argv) != 3 and len(sys.argv) != 5:
        print("Usage: merge_scale input.protofile input.ptcmodel output.protofile output.ptcmodel")
        print("or: merge_scale input.protofile output.protofile")
        exit()
    if len(sys.argv) == 3:
        input_protofile = sys.argv[1]
        output_protofile = sys.argv[2]
        print('input_protofile = %s' % input_protofile)
        print('output_protofile = %s' % output_protofile)
        merge_scale_proto(input_protofile, output_protofile)
    elif len(sys.argv) == 5:
        input_protofile = sys.argv[1]
        input_ptcmodel = sys.argv[2]
        output_protofile = sys.argv[3]
        output_ptcmodel = sys.argv[4]
        print('input_protofile = %s' % input_protofile)
        print('input_ptcmodel = %s' % input_ptcmodel)
        print('output_protofile = %s' % output_protofile)
        print('output_ptcmodel = %s' % output_ptcmodel)
        merge_scale(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel)

if __name__ == "__main__":
    main()
