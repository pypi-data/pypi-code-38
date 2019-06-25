# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2017.12.16
# --------------------------------------------------------

from __future__ import division, print_function

import copy
import time

import numpy as np
import torch
import torch.nn as nn

from ptcaffe.layer_dict import LAYER_DICT, DATA_LAYERS, LOSS_LAYERS
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.prototxt import parse_prototxt, parse_caffemodel, print_prototxt
from ptcaffe.utils.utils import *
from collections import OrderedDict


class CaffeNet(nn.Module):
    def __init__(self, protofile, phase='TRAIN'):
        super(CaffeNet, self).__init__()
        self.selector = ''
        if phase == 'TEST':
            self.set_save_memory_eval(True)
        else:
            self.set_save_memory_eval(False)

        assert protofile.find('.prototxt') > 0
        self.net_info = parse_prototxt(protofile)
        self.protofile = protofile
        self.phase = phase

        # craete network in TRAIN phase and TEST phase
        self.models = OrderedDict()
        for layer in self.net_info['layers']:
            lname = get_lname(layer)
            self.models[lname] = None

        branch_infos = self.get_branch_infos(self.net_info)
        for branch_info in branch_infos:
            logger.info("create branch %s" % str(branch_info))
            temp_models = self.create_network(self.net_info, *branch_info)
            self.merge_models(temp_models)

        # register models
        for name, model in self.models.items():
            new_name = name.replace('.', 'DOT')
            self.add_module(new_name, model)
        self.set_phase(phase)

        self.train_outputs = []
        self.eval_outputs = []
        self.set_automatic_outputs()

        self.init_fwd_time()
        self.VERIFY_DEBUG = False

        self.broadcast_apply('set_network', SafeNetwork(self))
        self.nested = False # special use for CaffeNetLayer

    def set_nested(self, flag=True):
        self.nested = flag

    def cuda(self, device=None):
        if device is None:
            self.broadcast_device_id(0)
        else:
            self.broadcast_device_id(device)
        return self._apply(lambda t: t.cuda(device))

    def set_save_memory_eval(self, save_memory_eval):
        self.save_memory_eval = save_memory_eval

    def train(self, mode=True):
        self.phase = 'TRAIN' if mode else 'TEST'
        self.training = mode
        for module in self.children():
            module.train(mode)
        return self

    def eval(self):
        return self.train(False)

    def set_phase(self, phase):
        assert phase in ['TEST', 'TRAIN']
        self.phase = phase
        mode = (phase == 'TRAIN')
        self.training = mode
        for module in self.children():
            module.train(mode)

    def set_selector(self, selector):
        self.selector = selector

    # used in trainer for display
    def get_loss_weights(self):
        loss_weights = OrderedDict()
        layers = self.net_info['layers']
        for layer in layers:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
                if phase != self.phase:
                    continue
            if 'include' in layer and 'selector' in layer['include']:
                selector = layer['include']['selector']
                if self.selector != '' and selector != self.selector:
                    continue
            ltype = layer['type']
            if ltype == 'Python':
                ltype = layer['python_param']['layer']
            #tname = layer.get('top', [])
            tname = get_layer_tnames(layer, self.phase)
            tnames = tname if isinstance(tname, list) else [tname]
            if ltype in LOSS_LAYERS or 'loss_weight' in layer:
                if 'loss_weight' in layer:
                    loss_weight = layer['loss_weight']
                    if isinstance(loss_weight, list):
                        for idx, w in enumerate(loss_weight):
                            loss_weights[tnames[idx]] = float(w)
                    else:
                        loss_weights[tnames[0]] = float(loss_weight)
                else:
                    loss_weights[tnames[0]] = 1.0
        return loss_weights

    def set_automatic_outputs(self, phase=""):
        blob_train_relys = OrderedDict()
        blob_eval_relys = OrderedDict()

        props = self.net_info['props']

        if 'input' in props:
            props_input = props['input']
            if not isinstance(props_input, list):
                props_input = [props_input]
            for idx, input_name in enumerate(props_input):
                blob_train_relys[input_name] = 0
                blob_eval_relys[input_name] = 0

        layers = self.net_info['layers']
        for layer in layers:
            lphase = phase
            if 'include' in layer and 'phase' in layer['include']:
                lphase = layer['include']['phase']
            if 'include' in layer and 'selector' in layer['include']:
                selector = layer['include']['selector']
                if self.selector != '' and selector != self.selector:
                    continue

            if (phase == '' or phase == 'TRAIN') and (lphase == 'TRAIN' or lphase == ''):
                bnames = get_layer_bnames(layer,"TRAIN")
                bnames = bnames if isinstance(bnames, list) else [bnames]
                tnames = get_layer_tnames(layer, "TRAIN")
                tnames = tnames if isinstance(tnames, list) else [tnames]
                for bname in bnames:
                    if bname in blob_train_relys:
                        blob_train_relys[bname] += 1
                    else:
                        blob_train_relys[bname] = 1
                for tname in tnames:
                    blob_train_relys[tname] = 0

            if (phase == '' or phase == 'TEST') and (lphase == 'TEST' or lphase == ''):
                bnames = get_layer_bnames(layer,"TEST")
                bnames = bnames if isinstance(bnames, list) else [bnames]
                tnames = get_layer_tnames(layer, "TEST")
                tnames = tnames if isinstance(tnames, list) else [tnames]
                for bname in bnames:
                    if bname in blob_eval_relys:
                        blob_eval_relys[bname] += 1
                    else:
                        blob_eval_relys[bname] = 1
                for tname in tnames:
                    blob_eval_relys[tname] = 0

        if phase == '' or phase == 'TRAIN':
            train_outputs = []
            for key, value in blob_train_relys.items():
                if value == 0:
                    train_outputs.append(key)
            self.set_train_outputs(*train_outputs)

        if phase == '' or phase == 'TEST':
            eval_outputs = []
            for key, value in blob_eval_relys.items():
                if value == 0:
                    eval_outputs.append(key)
            self.set_eval_outputs(*eval_outputs)

    def set_train_outputs(self, *outputs):
        self.train_outputs = list(outputs)

    def set_eval_outputs(self, *outputs):
        self.eval_outputs = list(outputs)

    def set_outputs(self, *outputs):
        self.train_outputs = list(outputs)
        self.eval_outputs = list(outputs)

    @staticmethod
    def create_blob_eval_relys( net_info, eval_outputs):
        blob_eval_relys = dict()

        layers = net_info['layers']
        layer_num = len(layers)

        # set bottom relys
        i = 0
        while i < layer_num:
            layer = layers[i]
            lname = layer['name']
            if 'include' in layer:
                if 'phase' in layer['include']:
                    phase = layer['include']['phase']
                    lname = lname + '@' + phase
                    if phase != "TEST":
                        i = i + 1
                        continue
                else: pass
                assert 'selector' not in layer['include']
            bnames = []
            if 'bottom' in layer:
                bnames = get_layer_bnames(layer,"TEST")
                if not isinstance(bnames, list):
                    bnames = [bnames]
            for bname in bnames:
                if bname in blob_eval_relys:
                    blob_eval_relys[bname] += 1
                else:
                    blob_eval_relys[bname] = 1
            i = i + 1

        # set output relys
        for name in eval_outputs:
            if name in blob_eval_relys:
                blob_eval_relys[name] += 1
            else:
                blob_eval_relys[name] = 1
        return blob_eval_relys

    # init fwd_tim_sum and fwd_count
    def init_fwd_time(self):
        self.fwd_time_sum = OrderedDict()
        self.fwd_count = OrderedDict()
        self.fwd_time_sum['network'] = 0.0
        self.fwd_count['network'] = 0
        for layer in self.net_info['layers']:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
            self.fwd_time_sum[lname] = 0.0
            self.fwd_count[lname] = 0

    def reset_forward_time(self):
        for key in self.fwd_time_sum.keys():
            self.fwd_time_sum[key] = 0.0
            self.fwd_count[key] = 0

    def print_forward_time(self, auto_format=False):
        seen = self.fwd_count['network']
        head_len = 30
        if auto_format:
            head_len = max([len(key) for key in self.fwd_time_sum.keys()])
        logger.print(('%' + str(head_len) + 's%20s%20s%20s%20s') % ('layer', 'total', 'average', 'count', 'percentage'))
        net_time = self.fwd_time_sum['network']
        net_time_avg = net_time / seen
        sum_time = 0.0
        for key in self.fwd_time_sum.keys():
            if key != 'network':
                t = self.fwd_time_sum[key]
                n = self.fwd_count[key]
                p = int(t * 10000.0 / net_time) / 100.0
                avg = 0.0 if n == 0 else t / n
                logger.print(('%' + str(head_len) + 's%20f%20f%20d%17.2f%%') % (key, t, avg, n, p))
                sum_time += t
        diff_time = net_time - sum_time
        diff_time_avg = diff_time / seen
        pdiff = int(diff_time * 10000.0 / net_time) / 100.0
        logger.print(('%' + str(head_len) + 's%20f%20f%20d%17.2f%%') % ('other', diff_time, diff_time_avg, seen, pdiff))
        logger.print('%30s' % '----')
        logger.print(('%' + str(head_len) + 's%20f%20f%20d') % ('network', net_time, net_time_avg, seen))

    def forward(self, *inputs):
        # optional step: create blob eval relys for save_memory_eval
        if (not self.training) and self.save_memory_eval:
            blob_eval_relys = self.create_blob_eval_relys(self.net_info, self.eval_outputs)

        # step1: create input blobs according to input props if exist
        self_blobs = OrderedDict()
        props = self.net_info['props']
        if 'input' in props:
            props_input = props['input']
            if not isinstance(props_input, list):
                props_input = [props_input]
            assert len(props_input) == len(inputs)
            for idx, input_name in enumerate(props_input):
                self_blobs[input_name] = inputs[idx]

        # step2: forward network layer by layer
        layers = self.net_info['layers']
        layer_num = len(layers)
        output_losses = []
        net_start = time.time()
        for layer in layers:
            # step2.1: filter layer according to phase and selector
            start_time = time.time()
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                lphase = layer['include']['phase']
                lname = lname + '@' + lphase
                if lphase != self.phase:
                    continue
            _lname = lname.replace('.', 'DOT')
            if 'include' in layer and 'selector' in layer['include']:
                selector = layer['include']['selector']
                if self.selector != '' and selector != self.selector:
                    continue
            ltype = layer['type']
            if ltype == 'Python':
                ltype = layer['python_param']['layer']
            tname = get_layer_tnames(layer, self.phase)
            tnames = tname if isinstance(tname, list) else [tname]

            # step2.2: process data layers
            if ltype in DATA_LAYERS:
                if len(inputs) == 0:
                    tdatas = self._modules[_lname]()
                    if not isinstance(tdatas, tuple):
                        tdatas = (tdatas,)

                    assert len(tdatas) == len(tnames)
                    for index, tdata in enumerate(tdatas):
                        self_blobs[tnames[index]] = tdata
                else:  # set input blobs
                    for idx, name in enumerate(tnames):
                        self_blobs[name] = inputs[idx]
                if logger.getEffectiveLevel() >= logger.DEBUG:
                    output_sizes = [list(self_blobs[name].size()) for name in tnames]
                    logger.debug('forward %-15s %-30s produce -> %s' % (ltype, lname, list(output_sizes)))
                end_time = time.time()
                if len(inputs) == 0:
                    assert lname in self.fwd_time_sum
                    self.fwd_time_sum[lname] += end_time - start_time
                    self.fwd_count[lname] += 1
                continue

            # step2.3: deal with empty bottom
            if 'bottom' in layer:
                bname = get_layer_bnames(layer,self.phase)
                bnames = bname if isinstance(bname, list) else [bname]
                bdatas = [self_blobs[name] for name in bnames]
            else:
                bnames = []
                bdatas = ()

            # step2.4: forward layer
            try:
                tdatas = self._modules[_lname](*bdatas)
            except Exception as e:
                print("---------DEBUG INFO-----------")
                print("Fail as ****{}**** in forward, ".format(str(e)) )
                #print("lname:{}, bdatas:{}".format(_lname, bdatas))
                print("lname: {}, tname: {}, bname: {}".format(_lname, tname, bname))
                print("---------DEBUG INFO end-------")
                raise(e)

            # step2.5: deal with empty top
            if isinstance(tdatas, tuple):
                pass
            elif isinstance(tdatas, torch.Tensor):  # should before None judgement
                tdatas = (tdatas,)
            elif tdatas is None:
                tdatas = ()
            else:
                tdatas = (tdatas,)

            # optional step: for extra functions
            if hasattr(self._modules[_lname], 'forward_extra'):
                self.models[lname].forward_extra(self)

            # step2.6: save top blob to a dictionary
            assert len(tdatas) == len(tnames), "top data length != top names with {}, {}".format(len(tdatas), len(tnames))

            for index, tdata in enumerate(tdatas):
                self_blobs[tnames[index]] = tdata

            # step2.7: deal with loss layer
            if self.training and (ltype in LOSS_LAYERS or 'loss_weight' in layer):
                if 'loss_weight' in layer:
                    loss_weight = layer['loss_weight']
                    if isinstance(loss_weight, list):
                        assert len(tdatas) >= len(loss_weight)
                        for idx, w in enumerate(loss_weight):
                            output_losses.append(float(w) * tdatas[idx].sum())
                    else:
                        output_losses.append(float(loss_weight) * tdatas[0].sum())
                else:
                    output_losses.append(tdatas[0].sum())

            # optional step: output verbose information
            if logger.getEffectiveLevel() >= logger.DEBUG:
                input_sizes = [list(self_blobs[name].size()) if hasattr(self_blobs[name], 'size') else [1] for name in bnames]
                output_sizes = [list(self_blobs[name].size()) if hasattr(self_blobs[name], 'size') else [1] for name in tnames]
                logger.debug('forward %-15s %-30s %s -> %s' % (ltype, lname, list(input_sizes), list(output_sizes)))
            if (not self.training) and self.save_memory_eval:
                for name in bnames:
                    blob_eval_relys[name] -= 1
                    if blob_eval_relys[name] == 0:
                        del self_blobs[name]
            end_time = time.time()
            assert lname in self.fwd_time_sum
            self.fwd_time_sum[lname] += end_time - start_time
            self.fwd_count[lname] += 1

        net_end = time.time()
        assert 'network' in self.fwd_time_sum
        self.fwd_time_sum['network'] += net_end - net_start
        self.fwd_count['network'] += 1

        # step3: return forward results
        if self.training:
            if self.VERIFY_DEBUG:
                return self_blobs
            if self.nested:
                if len(self.train_outputs) > 1:
                    outputs = [self_blobs[name] for name in self.train_outputs]
                    return tuple(outputs)
                elif len(self.train_outputs) == 1:
                    return self_blobs[self.train_outputs[0]]
                else:
                    return

            if len(output_losses) > 0:
                output_loss = sum(output_losses).view(1)
            else:
                output_loss = None
            if len(self.train_outputs) > 1:
                outputs = [self_blobs[name] for name in self.train_outputs]
                outputs.insert(0, output_loss)
                return tuple(outputs)
            elif len(self.train_outputs) == 1:
                try:
                    assert self.train_outputs[0] in self_blobs
                except Exception as e:
                    print("-----DEBUG INFO-----")
                    print(self.train_outputs[0])
                    print(self_blobs)
                    raise(e)
                if self.train_outputs[0] in self_blobs:
                    return output_loss, self_blobs[self.train_outputs[0]]
                else:
                    return output_loss
            else:
                return output_loss
        else:
            if self.VERIFY_DEBUG:
                return self_blobs
            if len(self.eval_outputs) > 1:
                odatas = [self_blobs[name] for name in self.eval_outputs]
                return tuple(odatas)
            elif len(self.eval_outputs) == 1:
                return self_blobs[self.eval_outputs[0]]
            else:
                return

    def print_network(self):
        logger.print(self)
        print_prototxt(self.net_info)

    def save_model(self, modelpath, other_protofile=None):
        if modelpath.find('.caffemodel') > 0:
            self.save_caffemodel(modelpath, other_protofile)
        elif modelpath.find('.ptcmodel') > 0:
            import ptcaffe
            state_dict = self.state_dict()
            for key in state_dict:
                state_dict[key] = state_dict[key].cpu()
            state_dict['ptcaffe_version'] = ptcaffe.__version__
            state_dict['python_version'] = python_version()
            state_dict['torch_version'] = torch.__version__
            try:
                import ptcaffe_plugins
                state_dict['plugin_version'] = ptcaffe_plugins.__version__
            except BaseException:
                state_dict['plugin_version'] = 'None'
            state_dict['seed_value'] = cfg.SEED
            state_dict['net_info'] = self.net_info
            
            torch.save(state_dict, modelpath)
        elif modelpath.find('.pth') > 0:
            torch.save(self.state_dict(), modelpath)
        else:
            assert False

    # used to modify the name in prototxt
    def load_renamed_model(self, modelpath):
        self_dict = self.state_dict()
        loaded_dict = torch.load(modelpath)
        loaded_dict.pop('ptcaffe_version')
        loaded_dict.pop('python_version')
        loaded_dict.pop('torch_version')
        loaded_dict.pop('plugin_version')
        loaded_dict.pop('seed_value')
        loaded_dict.pop('net_info')
        assert len(self_dict) == len(loaded_dict)
        for key1, key2 in zip(self_dict, loaded_dict):
            value1 = self_dict[key1]
            value2 = loaded_dict[key2]
            assert value1.size() == value2.size()
            if len(value1.shape) == 0:
                value1 = value2
            else:
                value1[:] = value2[:]
            logger.print('load model %s -> %s success' % (key1, key2))

    def load_model(self, modelpath):
        assert check_file_exists(modelpath)
        if modelpath.find('.pth') > 0 or modelpath.find('.ptcmodel') > 0:
            loaded_dict = torch.load(modelpath)
            self_dict = self.state_dict()
            self_num = len(self_dict)
            loaded_num = len(loaded_dict)
            used_num = 0
            for key in self_dict.keys():
                if key in loaded_dict.keys():
                    logger.debug('load %s' % key)
                    if self_dict[key].size() == loaded_dict[key].size():
                        used_num += 1
                        if self_dict[key].dim() == 0:
                            self_dict[key] = loaded_dict[key]
                        else:
                            self_dict[key][:] = loaded_dict[key][:]
                    else:
                        if cfg.ALLOW_MISMATCH_SIZE_WEIGHT_LOADING:
                            continue
                        else:
                            logger.warning("weight %s size mismatch, please set ALLOW_MISMATCH_SIZE_WEIGHT_LOADING = True" % key)
                            exit()
            logger.info('load model: loaded %d / %d, total needed %d' % (used_num, loaded_num, self_num))
        elif modelpath.find('.caffemodel') > 0:
            return self.load_caffemodel(modelpath)
        else:
            assert False, "unknown model file"

    def save_caffemodel(self, caffemodel, other_protofile=None):
        import ptcaffe.proto.caffe_pb2 as caffe_pb2
        import google.protobuf.text_format
        input_protofile = other_protofile if other_protofile else self.protofile
        assert input_protofile.find('.prototxt') > 0
        caffe_net = caffe_pb2.NetParameter()
        with open(input_protofile, 'rb') as fp:
            buf = fp.read()
            google.protobuf.text_format.Merge(buf, caffe_net)

        caffe_layers = caffe_net.layer
        if len(caffe_layers) == 0:
            #logger.info('Using V1LayerParameter')
            caffe_layers = caffe_net.layers

        caffe_lmap = {}
        for l in caffe_layers:
            caffe_lmap[l.name] = l

        pytorch_layers = self.net_info['layers']
        layer_num = len(pytorch_layers)
        for layer in pytorch_layers:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
            ltype = layer['type']
            if ltype == 'Python':
                ltype = layer['python_param']['layer']
            if lname not in caffe_lmap:
                continue
            blobs = []
            if ltype in ['Convolution', 'Deconvolution']:
                logger.debug('save conv weights %s' % lname)
                convolution_param = layer['convolution_param']
                bias = True
                if 'bias_term' in convolution_param and convolution_param['bias_term'] == 'false':
                    bias = False
                blobs.append(tensor2blob(self.models[lname].weight.data))
                if bias:
                    blobs.append(tensor2blob(self.models[lname].bias.data))
            elif ltype == 'Convolution3D':
                logger.debug('save conv weights %s' % lname)
                convolution_param = layer['convolution3d_param']
                bias = True
                if 'bias_term' in convolution_param and convolution_param['bias_term'] == 'false':
                    bias = False
                blobs.append(tensor2blob(self.models[lname].weight.data))
                if bias:
                    # bias shape in Convolution3D is [1,1,1,1,num_out]
                    bias_data_shape = self.models[lname].bias.data.shape[0]
                    bias_data = self.models[lname].bias.data.view(1, 1, 1, 1, bias_data_shape)
                    blobs.append(tensor2blob(bias_data))
            elif ltype == 'BatchNorm':
                if 'batch_norm_param' in layer and 'affine' in layer['batch_norm_param']:
                    affine = (layer['batch_norm_param'] == 'true')
                    assert not affine
                logger.debug('save bn params %s' % lname)
                blobs = []
                blobs.append(tensor2blob(self.models[lname].running_mean))
                blobs.append(tensor2blob(self.models[lname].running_var))
                blobs.append(tensor2blob(torch.FloatTensor([1.0])))
            elif ltype == 'Scale':
                if len(self.models[lname].bnames) == 1:
                    logger.debug('save scale weights %s' % lname)
                    blobs.append(tensor2blob(self.models[lname].weight.data))
                    blobs.append(tensor2blob(self.models[lname].bias.data))
            elif ltype == 'Normalize':
                logger.debug('save normalize weights %s' % lname)
                blobs.append(tensor2blob(self.models[lname].weight.data))
            elif ltype == 'InnerProduct':
                logger.debug('save inner_product weights %s' % lname)
                blobs.append(tensor2blob(self.models[lname].weight.data))
                blobs.append(tensor2blob(self.models[lname].bias.data))
            caffe_lmap[lname].blobs.extend(blobs)

        logger.info('save weights to %s' % caffemodel)
        with open(caffemodel, 'wb') as wf:
            wf.write(caffe_net.SerializeToString())

    def load_caffemodel(self, caffemodel):
        caffe_model = parse_caffemodel(caffemodel)
        caffe_layers = caffe_model.layer
        if len(caffe_layers) == 0:
            #logger.info('Using V1LayerParameter')
            caffe_layers = caffe_model.layers

        caffe_lmap = {}
        for l in caffe_layers:
            caffe_lmap[l.name] = l

        pytorch_layers = self.net_info['layers']
        layer_num = len(pytorch_layers)
        i = 0
        while i < layer_num:
            layer = pytorch_layers[i]
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
            ltype = layer['type']
            if ltype == 'Python':
                ltype = layer['python_param']['layer']
            if lname not in caffe_lmap:
                i = i + 1
                continue
            if ltype in ['Convolution', 'Deconvolution']:
                logger.debug('load conv weights %s' % lname)
                convolution_param = layer['convolution_param']
                bias = True
                if 'bias_term' in convolution_param and convolution_param['bias_term'] == 'false':
                    bias = False
                #weight_blob = caffe_lmap[lname].blobs[0]
                #print('caffe weight shape', weight_blob.num, weight_blob.channels, weight_blob.height, weight_blob.width)
                caffe_weight = np.array(caffe_lmap[lname].blobs[0].data)
                caffe_weight = torch.from_numpy(caffe_weight)
                if caffe_weight.numel() == self.models[lname].weight.data.numel():
                    caffe_weight = caffe_weight.view_as(self.models[lname].weight)
                    self.models[lname].weight.data.copy_(caffe_weight)
                else:
                    if cfg.ALLOW_MISMATCH_SIZE_WEIGHT_LOADING:
                        pass
                    else:
                        logger.warning("%s's weight size mismatch, please set ALLOW_MISMATCH_SIZE_WEIGHT_LOADING = True" % lname)
                        exit()

                if bias and len(caffe_lmap[lname].blobs) > 1:
                    caffe_bias = torch.from_numpy(np.array(caffe_lmap[lname].blobs[1].data))
                    if caffe_bias.numel() == self.models[lname].bias.data.numel():
                        self.models[lname].bias.data.copy_(caffe_bias)
                    else:
                        if cfg.ALLOW_MISMATCH_SIZE_WEIGHT_LOADING:
                            pass
                        else:
                            logger.warning("%s's bias size mismatch, please set ALLOW_MISMATCH_SIZE_WEIGHT_LOADING = True" % lname)
                            exit()

                    logger.debug("convlution %s has bias" % lname)
            elif ltype == 'Convolution3D':
                logger.debug('load conv weights %s' % lname)
                convolution_param = layer['convolution3d_param']
                bias = True
                if 'bias_term' in convolution_param and convolution_param['bias_term'] == 'false':
                    bias = False
                caffe_weight = np.array(caffe_lmap[lname].blobs[0].data)
                caffe_weight = torch.from_numpy(caffe_weight).view_as(self.models[lname].weight)
                self.models[lname].weight.data.copy_(caffe_weight)
                if bias and len(caffe_lmap[lname].blobs) > 1:
                    self.models[lname].bias.data.copy_(torch.from_numpy(np.array(caffe_lmap[lname].blobs[1].data)))
                    logger.debug("convlution3d %s has bias" % lname)
            elif ltype == 'BatchNorm':
                logger.debug('load bn params %s' % lname)
                mean = np.array(caffe_lmap[lname].blobs[0].data) / caffe_lmap[lname].blobs[2].data[0]
                var = np.array(caffe_lmap[lname].blobs[1].data) / caffe_lmap[lname].blobs[2].data[0]
                self.models[lname].running_mean.copy_(torch.from_numpy(mean))
                self.models[lname].running_var.copy_(torch.from_numpy(var))
            elif ltype == 'Scale':
                if len(self.models[lname].bnames) == 1:
                    logger.debug('load scale weights %s' % lname)
                    self.models[lname].weight.data.copy_(torch.from_numpy(np.array(caffe_lmap[lname].blobs[0].data)))
                    if self.models[lname].bias is not None:
                        self.models[lname].bias.data.copy_(torch.from_numpy(np.array(caffe_lmap[lname].blobs[1].data)))
            elif ltype == 'Normalize':
                logger.debug('load normalize weights %s' % lname)
                self.models[lname].weight.data.copy_(torch.from_numpy(np.array(caffe_lmap[lname].blobs[0].data)))
            elif ltype == 'InnerProduct':
                logger.debug('load inner_product weights %s' % lname)
                self.models[lname].weight.data.view(-1).copy_(torch.from_numpy(np.array(caffe_lmap[lname].blobs[0].data)).view(-1))
                if len(caffe_lmap[lname].blobs) > 1:
                    self.models[lname].bias.data.copy_(torch.from_numpy(np.array(caffe_lmap[lname].blobs[1].data)))
            i = i + 1

    def merge_models(self, models):
        for k,v in models.items():
            if self.models[k] is None:
                self.models[k] = v

    @staticmethod
    def create_network(net_info, phase, selector):
        # init
        display_RF = True

        models = OrderedDict()
        blob_shape = dict()
        if display_RF:
            blob_RF = OrderedDict()

        layers = net_info['layers']
        props = net_info['props']
        layer_num = len(layers)

        # step1: deal with props
        if 'input' in props and not isinstance(props['input'], list):
            input_name = props['input']
            if 'input_shape' in props:
                dims = props['input_shape']['dim']
            elif 'input_dim' in props:
                dims = props['input_dim']
            blob_shape[input_name] = [int(dim) for dim in dims]
            if display_RF:
                if len(blob_shape[input_name]) == 5:
                    blob_RF[input_name] = [1, 1, 1, 1, 1, 1]
                elif len(blob_shape[input_name]) == 4:
                    blob_RF[input_name] = [1, 1, 1, 1]
        elif 'input' in props and isinstance(props['input'], list):
            assert 'input_shape' in props and isinstance(props['input_shape'], list)
            assert len(props['input']) == len(props['input_shape'])
            for i in range(len(props['input'])):
                input_name = props['input'][i]
                dims = props['input_shape'][i]['dim']
                blob_shape[input_name] = [int(dim) for dim in dims]
                if display_RF:
                    if len(blob_shape[input_name]) == 5:
                        blob_RF[input_name] = [1, 1, 1, 1, 1, 1]
                    elif len(blob_shape[input_name]) == 4:
                        blob_RF[input_name] = [1, 1, 1, 1]

        # step2: create network layer by layer
        for layer in layers:
            # step2.1: prepare lname, ltype
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                lphase = layer['include']['phase']
                if lphase != phase: continue
                lname = lname + '@' + lphase
            if 'include' in layer and 'selector' in layer['include']:
                lselector = layer['include']['selector']
                if selector != "" and lselector !="" and selector !=lselector:
                    continue
            ltype = layer['type']

            # step2.2: prepare tnames, bnames, input_shapes, input_RFs (for forward_shape, forward_RF)
            #tname = layer.get('top', [])
            tname = get_layer_tnames(layer, phase)
            tnames = tname if isinstance(tname, list) else [tname]
            if 'bottom' in layer or ("train_bottom" in layer and "test_bottom" in layer):
                #bname = get_layer_bnames(layer,phase)
                bname = get_layer_bnames(layer, phase)
                bnames = bname if isinstance(bname, list) else [bname]
                input_shapes = [blob_shape[name] for name in bnames]
                if display_RF:
                    input_RFs = [blob_RF[name] for name in bnames]
            else:
                input_shapes = []
                input_RFs = []

            # step2.3: create layer
            if ltype == 'Python':
                assert lname not in models
                models[lname] = create_python_layer(layer, phase, *input_shapes)
            elif ltype in LAYER_DICT.keys():
                assert lname not in models, 'duplicated layer name {}'.format(lname)
                try:
                    models[lname] = LAYER_DICT[ltype](layer, *input_shapes)
                except Exception as e:
                    print("---------DEBUG INFO-----------")
                    print( "Fail as ****{}**** in create layer, ".format(str(e)) )
                    print( "in layer {},  top {}, phase {},".format(lname, tname, phase) )
                    print( "input_shape is {}".format(input_shapes) )
                    print("---------DEBUG INFO end-------")
                    raise(e)
            else:
                logger.error('create_network: unknown type #%s#' % ltype)
                exit()

            # step2.4: forward shapes
            if None in input_shapes:
                output_shapes = [None] * len(tnames) if len(tnames) > 0 else None
            else:
                output_shapes = models[lname].forward_shape(*input_shapes)
                if output_shapes:  # not empty
                    output_shapes = output_shapes if isinstance(output_shapes[0], list) else [output_shapes]

            try:
                if ltype in DATA_LAYERS:
                    for idx, tname in enumerate(tnames):
                        assert(tname not in blob_shape)
                        blob_shape[tname] = output_shapes[idx]
                else:
                    for idx, tname in enumerate(tnames):
                        blob_shape[tname] = output_shapes[idx]
            except Exception as e:
                print("---------DEBUG INFO-----------")
                print( "Fail as ****{}**** in create layer, ".format(str(e)) )
                print( "in layer {}, bottom{}, top {}, phase {}, ".format(lname, bname, tname, phase) )
                print( "other information are:" )
                print( "blob_shape {}, output_shapes {}, idx {}".format( blob_shape, output_shapes, idx) )
                print("---------DEBUG INFO end-------")
                raise(e)

            if selector == '':
                logger.debug('create %-12s %-30s %s -> %s' % (ltype, lname, str(input_shapes), str(output_shapes)))
            else:
                logger.debug('create %-12s %-30s %s -> %s' % (ltype, lname + '[' + selector + ']', str(input_shapes), str(output_shapes)))

            # optional step: forward receptive fileds
            if display_RF:
                if hasattr(models[lname], 'forward_RF'):
                    output_RFs = models[lname].forward_RF(*input_RFs)
                    output_RFs = output_RFs if isinstance(output_RFs[0], list) else [output_RFs]
                else:
                    if len(input_RFs) > 0:
                        output_RFs = [copy.copy(input_RFs[0])] *len(tnames)
                    else:
                        if len(output_shapes[0]) == 5:
                            output_RFs = [[1, 1, 1, 1, 1, 1]] * len(tnames)
                        else:
                            output_RFs = [[1, 1, 1, 1]] * len(tnames)
                for idx, tname in enumerate(tnames):
                    blob_RF[tname] = output_RFs[idx]

        # optional step: output receptive fileds
        if display_RF:
            max_key_len = max([len(key) for key in blob_RF.keys()]) + 2
            prefix_line = '-' * max_key_len
            prefix_blanks = ' ' * max_key_len
            logger.print('%s---------------------------------------------------' % prefix_line, level=logger.MORE_INFO)
            logger.print('%sReceptive Field                       Shape        ' % prefix_blanks, level=logger.MORE_INFO)
            for key in blob_RF.keys():
                rf = blob_RF[key]
                if len(rf) == 6:
                    format_str = '%' + str(max_key_len) + 's [%3d x %3d x %3d + %3d x %3d x %3d]\t%s'
                    logger.print(format_str % (key + " :", rf[0], rf[1], rf[2], rf[3], rf[4], rf[5], str(blob_shape[key])), level=logger.MORE_INFO)
                else:
                    format_str = '%' + str(max_key_len) + 's [%3d x %3d + %3d x %3d]\t%s'
                    logger.print(format_str % (key + " :", rf[0], rf[1], rf[2], rf[3], str(blob_shape[key])), level=logger.MORE_INFO)
            logger.print('%s---------------------------------------------------' % prefix_line, level=logger.MORE_INFO)

        return models

    def broadcast_apply(self, func_name, *args, **kwargs):
        layers = self.net_info['layers']
        for layer in layers:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
            if 'include' in layer and 'selector' in layer['include']:
                selector = layer['include']['selector']
                if self.selector is not "" and self.selector!=selector:continue
            _lname = lname.replace('.', 'DOT')
            model = self._modules[_lname]
            if hasattr(model, func_name):
                getattr(model, func_name)(*args, **kwargs)

    def get_metrics(self):
        layers = self.net_info['layers']
        metric_dict = dict()
        for layer in layers:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
            if 'include' in layer and 'selector' in layer['include']:
                selector = layer['include']['selector']
                if self.selector is not "" and self.selector!=selector:continue
            _lname = lname.replace('.', 'DOT')
            model = self._modules[_lname]
            if hasattr(model, 'get_metric'):
                metric_result = model.get_metric()
                for key, val in metric_result.items():
                    metric_dict[key] = val
        return metric_dict

    def reset_metrics(self):
        self.broadcast_apply('reset_metric')

    def broadcast_device_id(self, device_id):
        self.broadcast_apply('set_device', device_id)

    def broadcast_device_ids(self, device_ids):
        self.broadcast_apply('set_devices', device_ids)

    # return shape1, shape2, ...
    def get_input_shapes(self, phase='TEST'):
        props = self.net_info['props']
        layers = self.net_info['layers']
        if 'input' in props:
            if 'input_shape' in props:
                input_shape = props['input_shape']
                if isinstance(input_shape, OrderedDict):
                    shape = input_shape['dim']
                    shape = [int(s) for s in shape]
                    return shape
                else:
                    output_shapes = []
                    for shape in input_shape:
                        shape_dims = shape['dim']
                        shape_dims = [int(s) for s in shape_dims]
                        output_shapes.append(shape_dims)
                    return tuple(output_shapes)
            elif 'input_dim' in props:
                shape = props['input_dim']
                shape = [int(s) for s in shape]
                return shape
        else:
            output_shapes = []
            for layer in layers:
                lname = layer['name']
                if 'include' in layer and 'phase' in layer['include']:
                    phase = layer['include']['phase']
                    lname = lname + '@' + phase
                    if phase != self.phase:
                        continue
                _lname = lname.replace('.', 'DOT')
                ltype = layer['type']
                if ltype == 'Python':
                    ltype = layer['python_param']['layer']
                if ltype in DATA_LAYERS:
                    output_shape = self._modules[_lname].forward_shape()
                    output_shapes.extend(output_shape)
            return output_shapes

    @staticmethod
    def get_branch_infos(net_info):
        props = net_info['props']
        layers = net_info['layers']
        if "input" in props:
            return [['TEST', '']]

        else:
            states = []
            for layer in layers:
                ltype = layer['type']
                if ltype in DATA_LAYERS:
                    include_param = layer['include']
                    phase = include_param['phase']
                    selector = include_param.get('selector', '')
                    states.append([phase, selector])
            assert len(states) >= 1, "states is []"
            return states


    def get_input_names(self, phase='TEST'):
        props = self.net_info['props']
        layers = self.net_info['layers']
        if 'input' in props:
            return props['input']
        else:
            tnames = []
            for layer in layers:
                lname = layer['name']
                if 'include' in layer and 'phase' in layer['include']:
                    phase = layer['include']['phase']
                    lname = lname + '@' + phase
                    if phase != self.phase:
                        continue
                ltype = layer['type']
                if ltype == 'Python':
                    ltype = layer['python_param']['layer']
                if ltype in DATA_LAYERS:
                    #tname = layer['top']
                    tname = get_layer_tnames(layer, phase)
                    tnames.extend(tname if isinstance(tname, list) else [tname])
            return tnames

    def forward_shape(self, *input_shapes):
        props_input = make_list(self.get_input_names())
        blob_shape = dict()
        for idx, input_name in enumerate(props_input):
            blob_shape[input_name] = input_shapes[idx]

        layers = self.net_info['layers']
        for layer in layers:
            ltype = layer['type']
            if ltype in DATA_LAYERS: continue

            lname = layer['name']
            bnames = get_layer_bnames(layer,self.phase)
            bnames = bnames if isinstance(bnames, list) else [bnames]
            #tnames = layer['top']
            tnames = get_layer_tnames(layer, self.phase)
            tnames = tnames if isinstance(tnames, list) else [tnames]
            bottom_shapes = []
            for bname in bnames:
                bottom_shapes.append(blob_shape[bname])
            top_shapes = self.models[lname].forward_shape(*bottom_shapes)
            top_shapes = top_shapes if isinstance(top_shapes, tuple) else [top_shapes]
            for idx, tname in enumerate(tnames):
                blob_shape[tname] = top_shapes[idx]
        output_shapes = []
        if self.phase == 'TRAIN':
            assert self.training
            for out_name in self.train_outputs:
                output_shapes.append(blob_shape[out_name])
        else:
            for out_name in self.eval_outputs:
                output_shapes.append(blob_shape[out_name])
        return tuple(output_shapes)

    def has_data_layer(self, phase=''):
        layers = self.net_info['layers']
        for layer in layers:
            if 'include' in layer and 'phase' in layer['include']:
                if phase != '' and layer['include']['phase'] != phase:
                    continue
            ltype = layer['type']
            if ltype in DATA_LAYERS:
                return True
        return False

    def forward_data(self, *inputs):
        props = self.net_info['props']
        layers = self.net_info['layers']
        layer_num = len(layers)
        blobs = OrderedDict()
        for layer in layers:
            start_time = time.time()
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
                if phase != self.phase:
                    continue
            _lname = lname.replace('.', 'DOT')
            if 'include' in layer and 'selector' in layer['include']:
                selector = layer['include']['selector']
                if self.selector != '' and selector != self.selector:
                    continue
            ltype = layer['type']
            if ltype == 'Python':
                ltype = layer['python_param']['layer']
            tname = layer['top']
            tnames = tname if isinstance(tname, list) else [tname]
            if ltype in DATA_LAYERS:
                if len(inputs) == 0:
                    output = self._modules[_lname]()
                    end_time = time.time()
                    assert lname in self.fwd_time_sum
                    self.fwd_time_sum[lname] += end_time - start_time
                    self.fwd_count[lname] += 1
                    self.fwd_time_sum['network'] += end_time - start_time
                    return output
                else:
                    tdatas = inputs
                    assert len(tdatas) == len(tnames)
                    for index, tdata in enumerate(tdatas):
                        blobs[tnames[index]] = tdata
                    end_time = time.time()
                    assert lname in self.fwd_time_sum
                    self.fwd_time_sum[lname] += end_time - start_time
                    self.fwd_count[lname] += 1
                    return blobs

    def get_parameters(self, base_lr, base_decay):
        params_dict = dict(self.named_parameters())
        param_groups = []
        layer_dict = dict()
        layers = self.net_info['layers']
        for layer in layers:
            lname = layer['name']
            assert lname.find('@') == -1
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
            layer_dict[lname] = layer

        for key, value in params_dict.items():
            items = key.split('.')
            if True:  # len(items) == 2:
                lname = items[0].replace('DOT', '.')
                ptype = items[-1]
                layer = layer_dict[lname]
                ltype = layer['type']
                params = []
                if 'param' in layer:
                    params = layer['param']
                    params = params if isinstance(params, list) else [params]
                if ptype == 'weight' and len(params) >= 1:
                    if ltype in ['BatchNorm', 'Scale']:
                        lr_mult = float(params[0].get('lr_mult', cfg.DEFAULT_BN_WEIGHT_LR_MULT))
                        decay_mult = float(params[0].get('decay_mult', cfg.DEFAULT_BN_WEIGHT_DECAY_MULT))
                    else:
                        lr_mult = float(params[0].get('lr_mult', cfg.DEFAULT_WEIGHT_LR_MULT))
                        decay_mult = float(params[0].get('decay_mult', cfg.DEFAULT_WEIGHT_DECAY_MULT))
                elif ptype == 'bias' and len(params) == 2:
                    if ltype in ['BatchNorm', 'Scale']:
                        lr_mult = float(params[1].get('lr_mult', cfg.DEFAULT_BN_BIAS_LR_MULT))
                        decay_mult = float(params[1].get('decay_mult', cfg.DEFAULT_BN_BIAS_DECAY_MULT))
                    else:
                        lr_mult = float(params[1].get('lr_mult', cfg.DEFAULT_BIAS_LR_MULT))
                        decay_mult = float(params[1].get('decay_mult', cfg.DEFAULT_BIAS_DECAY_MULT))
                else:
                    lr_mult = cfg.DEFAULT_LR_MULT
                    decay_mult = cfg.DEFAULT_DECAY_MULT
            param_groups.append(dict(params=[value], lr_mult=lr_mult, lr=lr_mult * base_lr,
                                     decay_mult=decay_mult, weight_decay=decay_mult * base_decay))
        return param_groups

    def get_batch_size(self, _phase):
        layers = self.net_info['layers']
        for layer in layers:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
                if phase != _phase:
                    continue
            ltype = layer['type']
            if ltype in DATA_LAYERS:
                if hasattr(self.models[lname], 'get_batch_size'):
                    batch_size = self.models[lname].get_batch_size()
                    return batch_size
                elif hasattr(self.models[lname], 'batch_size'):
                    batch_size = self.models[lname].batch_size
                    return batch_size
                else:
                    return None

    def get_batch_num(self, _phase):
        layers = self.net_info['layers']
        for layer in layers:
            lname = layer['name']
            if 'include' in layer and 'phase' in layer['include']:
                phase = layer['include']['phase']
                lname = lname + '@' + phase
                if phase != _phase:
                    continue
            ltype = layer['type']
            if ltype in DATA_LAYERS:
                if hasattr(self.models[lname], 'get_batch_num'):
                    batch_num = self.models[lname].get_batch_num()
                    return batch_num
                elif hasattr(self.models[lname], 'batch_num'):
                    batch_num = self.models[lname].batch_num
                    return batch_num
                else:
                    return None

# -------------tools functions
def create_python_layer( layer, phase, *input_shapes):
    python_param = layer.get('python_param', OrderedDict())
    layer_type = python_param['layer']
    param_str = python_param['param_str']

    layer2 = OrderedDict()
    layer2['name'] = layer['name']
    layer2['type'] = layer_type
    if 'bottom' in layer:
        layer2['bottom'] = get_layer_bnames(layer, phase=phase)
    layer2['top'] = layer['top']
    layer2['python_param'] = param_str
    return LAYER_DICT[layer_type](layer2, *input_shapes)


