# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

from darknet2ptcaffe import darknet_lib, verify_ptcaffe_darknet, verify_ptcaffe_darknet_train

from collections import OrderedDict
from ptcaffe.utils.prototxt import parse_prototxt
import numpy as np
import copy

def save_cfg(blocks, cfgfile):
    with open(cfgfile, 'w') as fp:
        for block in blocks:
            fp.write('[%s]\n' % (block['type']))
            for key,value in block.items():
                if key != 'type':
                    fp.write('%s=%s\n' % (key, value))
            fp.write('\n')

def ptcaffe2darknet(protofile, ptcmodel):
    #from cfg import *
    from ptcaffe.caffenet import CaffeNet
    import ptcaffe.plugins.yolo
    ptc_net = CaffeNet(protofile, phase='TEST') # parse_caffemodel(ptcaffe_model)
    ptc_net.load_model(ptcmodel)
    ptc_models = ptc_net.models
    net_info = ptc_net.net_info
    props = net_info['props']

    wdata = []
    blocks = []
    block = OrderedDict()
    block['type'] = 'net'
    if 'input_shape' in props:
        block['batch'] = props['input_shape']['dim'][0]
        block['channels'] = props['input_shape']['dim'][1]
        block['height'] = props['input_shape']['dim'][2]
        block['width'] = props['input_shape']['dim'][3]
    else:
        block['batch'] = props['input_dim'][0]
        block['channels'] = props['input_dim'][1]
        block['height'] = props['input_dim'][2]
        block['width'] = props['input_dim'][3]
    blocks.append(block)

    layers = net_info['layers']
    layer_num = len(layers)
    i = 0 # layer id
    layer_id = dict()
    layer_id[props['input']] = 0
    while i < layer_num:
        layer = layers[i]
        print(i,layer['name'], layer['type'])
        if layer['type'] == 'Convolution':
            if layer_id[layer['bottom']] != len(blocks)-1:
                block = OrderedDict()
                block['type'] = 'route'
                block['layers'] = str(layer_id[layer['bottom']] - len(blocks))
                blocks.append(block)
            #assert(i+1 < layer_num and layers[i+1]['type'] == 'BatchNorm')
            #assert(i+2 < layer_num and layers[i+2]['type'] == 'Scale')
            conv_layer = layers[i]
            conv_name = conv_layer['name']
            block = OrderedDict()
            block['type'] = 'convolutional'
            block['filters'] = conv_layer['convolution_param']['num_output']
            block['size'] = conv_layer['convolution_param']['kernel_size']
            block['stride'] = conv_layer['convolution_param']['stride']
            block['pad'] = '1'
            last_layer = conv_layer 
            if i+1 < layer_num and layers[i+1]['type'] == 'BatchNorm':
                bn_layer = layers[i+1]
                bn_name = bn_layer['name']
                batch_norm_param = bn_layer.get('batch_norm_param', OrderedDict())
                affine = batch_norm_param.get('affine', 'false')
                if affine == 'true':
                    print(i+1,layers[i+1]['name'], layers[i+1]['type'])
                    block['batch_normalize'] = '1'
                    last_layer = bn_layer
                    wdata += ptc_models[bn_name].bias.data.view(-1).tolist()  ## conv_bias <- sc_beta
                    wdata += ptc_models[bn_name].weight.data.view(-1).tolist()
                    wdata += ptc_models[bn_name].running_mean.view(-1).tolist()
                    wdata += ptc_models[bn_name].running_var.view(-1).tolist()
                    i = i + 1
                else:
                    assert(i+2 < layer_num and layers[i+2]['type'] == 'Scale')
                    print(i+1,layers[i+1]['name'], layers[i+1]['type'])
                    print(i+2,layers[i+2]['name'], layers[i+2]['type'])
                    block['batch_normalize'] = '1'
                    sc_layer = layers[i+2]
                    sc_name = sc_layer['name']
                    last_layer = sc_layer
                    wdata += ptc_models[sc_name].bias.data.view(-1).tolist()  ## conv_bias <- sc_beta
                    wdata += ptc_models[sc_name].weight.data.view(-1).tolist()
                    wdata += ptc_models[bn_name].running_mean.view(-1).tolist()
                    wdata += ptc_models[bn_name].running_var.view(-1).tolist()
                    i = i + 2
            else:
                wdata += ptc_models[conv_name].bias.data.view(-1).tolist() # conv_bias
            wdata += ptc_models[conv_name].weight.data.view(-1).tolist() # conv_weight
            
            if i+1 < layer_num and layers[i+1]['type'] == 'ReLU':
                print(i+1,layers[i+1]['name'], layers[i+1]['type'])
                act_layer = layers[i+1]
                relu_param = act_layer.get('relu_param', OrderedDict())
                if 'negative_slope' in relu_param and float(relu_param['negative_slope']) == 0.1:
                    block['activation'] = 'leaky'
                else:
                    block['activation'] = 'relu'
                top = act_layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
                i = i + 1
            else:
                block['activation'] = 'linear'
                top = last_layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Pooling':
            assert(layer_id[layer['bottom']] == len(blocks)-1)
            block = OrderedDict()
            if layer['pooling_param']['pool'] == 'AVE':
                block['type'] = 'avgpool'
            elif layer['pooling_param']['pool'] == 'MAX':
                block['type'] = 'maxpool'
                block['size'] = layer['pooling_param']['kernel_size']
                block['stride'] = layer['pooling_param']['stride']
                if 'pad' in layer['pooling_param']:
                    pad = int(layer['pooling_param']['pad'])
                    if pad > 0:
                        block['pad'] = '1'
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Eltwise':
            bottoms = layer['bottom']
            bottom1 = layer_id[bottoms[0]] - len(blocks)
            bottom2 = layer_id[bottoms[1]] - len(blocks)
            assert(bottom1 == -1 or bottom2 == -1)
            from_id = bottom2 if bottom1 == -1 else bottom1
            block = OrderedDict()
            block['type'] = 'shortcut'
            block['from'] = str(from_id)
            if i+1 < layer_num and layers[i+1]['type'] == 'ReLU':
                act_layer = layers[i+1]
                relu_param = act_layer.get('relu_param', OrderedDict())
                if 'negative_slope' in relu_param and float(relu_param['negative_slope']) == 0.1:
                    block['activation'] = 'leaky'
                else:
                    block['activation'] = 'relu'
                top = layers[i+1]['top']
                i = i + 2
            else:
                block['activation'] = 'linear'
                top = layers[i]['top']
                i = i + 1
            layer_id[top] = len(blocks)
            blocks.append(block)
        elif layer['type'] == 'InnerProduct':
            assert(layer_id[layer['bottom']] == len(blocks)-1)
            block = OrderedDict()
            block['type'] = 'connected'
            block['output'] = layer['inner_product_param']['num_output']
            m_fc_layer = lmap[layer['name']]
            wdata += list(m_fc_layer.blobs[1].data)       ## fc_bias
            wdata += list(m_fc_layer.blobs[0].data)       ## fc_weights
            if i+1 < layer_num and layers[i+1]['type'] == 'ReLU':
                act_layer = layers[i+1]
                relu_param = act_layer.get('relu_param', OrderedDict())
                if 'negative_slope' in relu_param and float(relu_param['negative_slope']) == 0.1:
                    block['activation'] = 'leaky'
                else:
                    block['activation'] = 'relu'
                top = act_layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
                i = i + 2
            else:
                block['activation'] = 'linear'
                top = layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
                i = i + 1
        elif layer['type'] == 'Softmax':
            assert(layer_id[layer['bottom']] == len(blocks)-1)
            block = OrderedDict()
            block['type'] = 'softmax'
            block['groups'] = '1'
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Concat':
            block = OrderedDict()
            block['type'] = 'route'
            bnames = layer['bottom']
            assert(len(bnames) == 2)
            assert(layer_id[bnames[0]] == len(blocks)-1)
            bottom_id0 = str(layer_id[bnames[0]] - len(blocks))
            bottom_id1 = str(layer_id[bnames[1]] - len(blocks))
            block['layers'] = ','.join([bottom_id0, bottom_id1])
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'YoloUpsample':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            block = OrderedDict()
            block['type'] = 'upsample'
            block['stride'] = layer['upsample_param']['stride']
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Reorg':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            block = OrderedDict()
            block['type'] = 'reorg'
            block['stride'] = layer['reorg_param']['stride']
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'RegionLoss':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            region_param = layer.get('region_param', OrderedDict())
            block = copy.copy(region_param)
            block['type'] = 'region'
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'YoloLoss':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            yolo_param = layer.get('yolo_param', OrderedDict())
            block = OrderedDict()
            block['type'] = 'yolo'
            block['stride'] = yolo_param['stride']
            block['mask'] = yolo_param['mask']
            block['anchors'] = yolo_param['anchors']
            block['classes'] = yolo_param['classes']
            block['num'] = yolo_param['num']
            block['jitter'] = yolo_param.get('jitter', '.3')
            block['ignore_thresh'] = yolo_param['ignore_thresh']
            block['truth_thresh'] = yolo_param['truth_thresh']
            block['random'] = yolo_param.get('random', '1')
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        else:
            print('unknown type %s' % layer['type'])
            exit()
            if layer_id[layer['bottom']] != len(blocks)-1:
                block = OrderedDict()
                block['type'] = 'route'
                block['layers'] = str(layer_id[layer['bottom']] - len(blocks))
                blocks.append(block)
            block = OrderedDict()
            block['type'] = layer['type']
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)

            i = i + 1

    print('done')
    return blocks, np.array(wdata, dtype=np.float32)

def prototxt2cfg(protofile):
    net_info = parse_prototxt(protofile)
    props = net_info['props']

    blocks = []
    block = OrderedDict()
    block['type'] = 'net' 
    if 'input_shape' in props:
        block['batch'] = props['input_shape']['dim'][0]
        block['channels'] = props['input_shape']['dim'][1]
        block['height'] = props['input_shape']['dim'][2]
        block['width'] = props['input_shape']['dim'][3]
    else:
        block['batch'] = props['input_dim'][0]
        block['channels'] = props['input_dim'][1]
        block['height'] = props['input_dim'][2]
        block['width'] = props['input_dim'][3]
    blocks.append(block)

    layers = net_info['layers']
    layer_num = len(layers)
    i = 0 # layer id
    layer_id = dict()
    layer_id[props['input']] = 0
    while i < layer_num:
        layer = layers[i]
        print(i,layer['name'], layer['type'])
        if layer['type'] == 'Convolution':
            if layer_id[layer['bottom']] != len(blocks)-1:
                block = OrderedDict()
                block['type'] = 'route'
                block['layers'] = str(layer_id[layer['bottom']] - len(blocks))
                blocks.append(block)
            conv_layer = layers[i]
            block = OrderedDict()
            block['type'] = 'convolutional'
            last_layer = conv_layer 
            if i+1 < layer_num and layers[i+1]['type'] == 'BatchNorm':
                bn_layer = layers[i+1]
                batch_norm_param = bn_layer.get('batch_norm_param', OrderedDict())
                affine = batch_norm_param.get('affine', 'false')
                if affine == 'true':
                    print(i+1,layers[i+1]['name'], layers[i+1]['type'])
                    block['batch_normalize'] = '1'
                    last_layer = bn_layer
                    i = i + 1
                else:
                    assert(i+2 < layer_num and layers[i+2]['type'] == 'Scale')
                    print(i+1,layers[i+1]['name'], layers[i+1]['type'])
                    print(i+2,layers[i+2]['name'], layers[i+2]['type'])
                    block['batch_normalize'] = '1'
                    scale_layer = layers[i+2]
                    last_layer = scale_layer
                    i = i + 2

            block['filters'] = conv_layer['convolution_param']['num_output']
            block['size'] = conv_layer['convolution_param']['kernel_size']
            if 'stride' in conv_layer['convolution_param']:
                block['stride'] = conv_layer['convolution_param']['stride']
            else:
                block['stride'] = '1'
            block['pad'] = '1'

            if i+1 < layer_num and layers[i+1]['type'] == 'ReLU':
                print(i+1,layers[i+1]['name'], layers[i+1]['type'])
                act_layer = layers[i+1]
                relu_param = act_layer.get('relu_param', OrderedDict())
                if 'negative_slope' in relu_param and float(relu_param['negative_slope']) == 0.1:
                    block['activation'] = 'leaky'
                else:
                    block['activation'] = 'relu'
                top = act_layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
                i = i + 1
            else:
                block['activation'] = 'linear'
                top = last_layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Pooling':
            assert(layer_id[layer['bottom']] == len(blocks)-1)
            block = OrderedDict()
            if layer['pooling_param']['pool'] == 'AVE':
                block['type'] = 'avgpool'
            elif layer['pooling_param']['pool'] == 'MAX':
                block['type'] = 'maxpool'
                block['size'] = layer['pooling_param']['kernel_size']
                block['stride'] = layer['pooling_param']['stride']
                if 'pad' in layer['pooling_param']:
                    pad = int(layer['pooling_param']['pad'])
                    if pad > 0:
                        block['pad'] = '1'
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Eltwise':
            bottoms = layer['bottom']
            bottom1 = layer_id[bottoms[0]] - len(blocks)
            bottom2 = layer_id[bottoms[1]] - len(blocks)
            assert(bottom1 == -1 or bottom2 == -1)
            from_id = bottom2 if bottom1 == -1 else bottom1
            block = OrderedDict()
            block['type'] = 'shortcut'
            block['from'] = str(from_id)
            if i+1 < layer_num and layers[i+1]['type'] == 'ReLU':
                act_layer = layers[i+1]
                relu_param = act_layer.get('relu_param', OrderedDict())
                if 'negative_slope' in relu_param and float(relu_param['negative_slope']) == 0.1:
                    block['activation'] = 'leaky'
                else:
                    block['activation'] = 'relu'
                top = layers[i+1]['top']
                i = i + 2
            else:
                block['activation'] = 'linear'
                top = layers[i]['top']
                i = i + 1
            layer_id[top] = len(blocks)
            blocks.append(block)
        elif layer['type'] == 'InnerProduct':
            assert(layer_id[layer['bottom']] == len(blocks)-1)
            block = OrderedDict()
            block['type'] = 'connected'
            block['output'] = layer['inner_product_param']['num_output']
            if i+1 < layer_num and layers[i+1]['type'] == 'ReLU':
                act_layer = layers[i+1]
                relu_param = act_layer.get('relu_param', OrderedDict())
                if 'negative_slope' in relu_param and float(relu_param['negative_slope']) == 0.1:
                    block['activation'] = 'leaky'
                else:
                    block['activation'] = 'relu'
                top = act_layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
                i = i + 2
            else:
                block['activation'] = 'linear'
                top = layer['top']
                layer_id[top] = len(blocks)
                blocks.append(block)
                i = i + 1
        elif layer['type'] == 'Softmax':
            assert(layer_id[layer['bottom']] == len(blocks)-1)
            block = OrderedDict()
            block['type'] = 'softmax'
            block['groups'] = '1'
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Concat':
            block = OrderedDict()
            block['type'] = 'route'
            bnames = layer['bottom']
            assert(len(bnames) == 2)
            assert(layer_id[bnames[0]] == len(blocks)-1)
            bottom_id0 = str(layer_id[bnames[0]] - len(blocks))
            bottom_id1 = str(layer_id[bnames[1]] - len(blocks))
            block['layers'] = ','.join([bottom_id0, bottom_id1])
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'YoloUpsample':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            block = OrderedDict()
            block['type'] = 'upsample'
            block['stride'] = layer['upsample_param']['stride']
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'Reorg':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            block = OrderedDict()
            block['type'] = 'reorg'
            block['stride'] = layer['reorg_param']['stride']
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        elif layer['type'] == 'YoloLoss':
            assert(layer_id[layer['bottom']] == len(blocks) - 1)
            yolo_param = layer.get('yolo_param', OrderedDict())
            block = OrderedDict()
            block['type'] = 'yolo'
            block['stride'] = yolo_param['stride']
            block['mask'] = yolo_param['mask']
            block['anchors'] = yolo_param['anchors']
            block['classes'] = yolo_param['classes']
            block['num'] = yolo_param['num']
            block['jitter'] = yolo_param.get('jitter', '.3')
            block['ignore_thresh'] = yolo_param['ignore_thresh']
            block['truth_thresh'] = yolo_param['truth_thresh']
            block['random'] = yolo_param.get('random', '1')
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1
        else:
            print('unknown type %s' % layer['type'])
            exit()
            if layer_id[layer['bottom']] != len(blocks)-1:
                block = OrderedDict()
                block['type'] = 'route'
                block['layers'] = str(layer_id[layer['bottom']] - len(blocks))
                blocks.append(block)
            block = OrderedDict()
            block['type'] = layer['type']
            top = layer['top']
            layer_id[top] = len(blocks)
            blocks.append(block)
            i = i + 1

    print('done')
    return blocks


def save_weights(wdata, weightfile):
    fp = open(weightfile, 'wb')
    np.array([0,2,0], dtype=np.int32).tofile(fp)
    np.array([0], dtype=np.int64).tofile(fp)
    wdata.tofile(fp)
    fp.close()

#if __name__ == '__main__':
def main():
    import sys
    import ptcaffe
    print('ptcaffe %s' % ptcaffe.__version__)
    
    if len(sys.argv) != 3 and len(sys.argv) !=5 and len(sys.argv) !=6:
        print('try:')
        print('python ptcaffe2darknet.py protofile ptmodel cfgfile darknet_weights [verify_train]')
        print('verify_train: 0, 1; default 0')
        print('python ptcaffe2darknet.py protofile cfgfile')
        exit()
    if len(sys.argv) == 3:
        protofile = sys.argv[1]
        cfgfile = sys.argv[2]
        blocks = prototxt2cfg(protofile)
        print('save %s' % cfgfile)
        save_cfg(blocks, cfgfile)
    elif len(sys.argv) == 5 or len(sys.argv) == 6:
        protofile = sys.argv[1]
        ptcmodel = sys.argv[2]
        cfgfile = sys.argv[3]
        weightfile = sys.argv[4]
        verify_train = int(sys.argv[5]) if len(sys.argv) >= 6 else 0
        
        blocks, wdata = ptcaffe2darknet(protofile, ptcmodel)
        
        print('save %s' % weightfile)
        save_weights(wdata, weightfile)
        print('save %s' % cfgfile)
        save_cfg(blocks, cfgfile)
        
        #print_cfg(blocks)
        if verify_train:
            verify_ptcaffe_darknet_train(darknet_lib, protofile, ptcmodel, cfgfile, weightfile)
        else:
            verify_ptcaffe_darknet(darknet_lib, protofile, ptcmodel, cfgfile, weightfile)
