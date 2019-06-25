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

def split_scale(input_protofile,input_ptmodel,output_protofile,output_ptmodel):
    input_net=CaffeNet(input_protofile)
    input_net.load_model(input_ptmodel)
    layers=input_net.net_info['layers']
    # create layer_from
    blob_from=dict()
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

    #make the Caffe files
    new_net_info = copy.deepcopy(input_net.net_info)
    new_layers = new_net_info['layers']
    
    saved_scale_lnames=[]
    saved_scale_weights=dict()
    saved_scale_biases=dict()

    remaining_layers=[]
    for lname in layer_from.keys():
        index = lname_index[lname]
        layer = layers[index]
        ltype = layer['type']
        if ltype =='BatchNorm':
            old_bn_lname = lname
            old_bn_layer = layer
            old_bn_from_layers = layer_from[old_bn_lname]

            if len(old_bn_from_layers)==1:
                old_bn_params=old_bn_layer.get('batch_norm_param', OrderedDict())
                new_bn_layer = layers[lname_index[old_bn_lname]]
                if 'affine' in old_bn_params.keys() and old_bn_params['affine']=='true':
                    del new_bn_layer['batch_norm_param']['affine']
                    if not new_bn_layer['batch_norm_param']:
                        del new_bn_layer['batch_norm_param']
                    remaining_layers.append(new_bn_layer)

                    scale_layer = copy.deepcopy(new_bn_layer)
                    scale_layer['name'] = 'scale_'+new_bn_layer['name']
                    scale_layer['type'] = 'Scale'
                    scale_param = OrderedDict()
                    scale_param['bias_term'] = 'true'
                    scale_layer['scale_param'] = scale_param
                    remaining_layers.append(scale_layer)

                    saved_scale_weights[scale_layer['name']] = input_net.models[old_bn_lname].weight.data
                    saved_scale_biases[scale_layer['name']] = input_net.models[old_bn_lname].bias.data
                    saved_scale_lnames.append(scale_layer['name'])
                else:
                    if not new_bn_layer['batch_norm_param']:
                        del new_bn_layer['batch_norm_param']
                    remaining_layers.append(new_bn_layer)
        else:
            remaining_layers.append(layer)
    new_net_info['layers'] = remaining_layers
    print('save %s' % output_protofile)
    save_prototxt(new_net_info, output_protofile)
    output_net = CaffeNet(output_protofile)
    input_state_dict = input_net.state_dict()
    output_state_dict = output_net.state_dict()
    for key in output_state_dict.keys():
        if key in input_state_dict.keys():
            output_state_dict[key][:] = input_state_dict[key][:]
    for lname in output_net.models.keys():
        if lname in saved_scale_lnames:
            output_net.models[lname].weight.data.copy_(saved_scale_weights[lname])
            output_net.models[lname].bias.data.copy_(saved_scale_biases[lname])
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
    if len(sys.argv) != 5:
        print("Usage: split_scale input.prototxt input.ptcmodel output.prototxt output.ptcmodel")
        exit()
    input_protofile = sys.argv[1]
    input_ptcmodel = sys.argv[2]
    output_protofile = sys.argv[3]
    output_ptcmodel = sys.argv[4]
    print('input_protofile = %s' % input_protofile)
    print('input_ptcmodel = %s' % input_ptcmodel)
    print('output_protofile = %s' % output_protofile)
    print('output_ptcmodel = %s' % output_ptcmodel)
    split_scale(input_protofile,input_ptcmodel,output_protofile,output_ptcmodel)
       
if __name__ == "__main__":
    main()
