# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

#===============================================
# main commands
#===============================================
def time_net(args):
    import torch
    from ..caffenet import CaffeNet
    if args.phase == 'TRAIN':
        net = CaffeNet(args.model, phase='TRAIN')
        net.train()
        if args.gpu:
            assert(args.gpu.find(',') == -1)
            print('set gpu device %s' % args.gpu)
            device_id = int(args.gpu)
            net.cuda(device_id)
        for i in range(args.iterations+1):
            output = net()
            if i == 0:
                net.reset_forward_time() # the initial time should be excluded
        net.print_forward_time(auto_format=True)
    else:
        net = CaffeNet(args.model, phase='TEST')
        net.eval()
        if args.gpu:
            assert(args.gpu.find(',') == -1)
            print('set gpu device %s' % args.gpu)
            net.cuda(int(args.gpu))
        assert(not isinstance(net.net_info['props']['input'], list))
        if 'input_dim' in net.net_info['props']:
            input_shape = net.net_info['props']['input_dim']
            input_shape = [int(dim) for dim in input_shape]
        elif 'input_shape' in net.net_info['props']:
            input_shape =  net.net_info['props']['input_shape']['dim']
            input_shape = [int(dim) for dim in input_shape]
            
        print('data_shape: %s' % input_shape)
        for i in range(args.iterations+1):
            data = torch.rand(input_shape)
            if args.gpu:
                data = data.cuda(int(args.gpu))
            with torch.no_grad():
                output = net(data)
            if i == 0:
                net.reset_forward_time() # the initial time should be excluded
        net.print_forward_time(auto_format=True)

        from torchstat import stat
        input_shapes = net.get_input_shapes(phase='TEST')
        if len(input_shapes) == 1:
            input_shape = input_shapes[0][1:]
            stat(net, input_shape)

def run_net(args):
    import torch
    from ..caffenet import CaffeNet
    from ..trainers.data_parallel import ParallelCaffeNet
    from ..utils.config import cfg
    from ..utils.logger import logger
    phase = args.phase if args.phase else 'TEST'
    print('set phase %s' % phase)

    if args.verbose is not None:
        cfg.VERBOSE_LEVEL = args.verbose
        if args.verbose == 0:
            logger.set_level(logger.INFO)
        elif args.verbose == 1:
            logger.set_level(logger.MORE_INFO)
        elif args.verbose >= 2:
            logger.set_level(logger.DEBUG)

    net = CaffeNet(args.model, phase=phase)
    if args.weights:
        net.load_model(args.weights)
    if phase == 'TRAIN': 
        net.train()
    else:
        net.eval()

    # GPU
    if args.gpu:
        if args.gpu.find(',') == -1:
            print('single gpu device %s' % args.gpu)
            device_id = int(args.gpu)
            net.cuda(device_id)
            net.broadcast_device_ids([device_id])
        else:
            device_ids = args.gpu.split(',')
            print('multi gpu devices %s' % args.gpu)
            device_ids = [int(i) for i in device_ids]
            net = ParallelCaffeNet(net.cuda(device_ids[0]), device_ids=device_ids)

    # forward
    if args.iterations is None:
        args.iterations = 1

    for i in range(args.iterations):
        print("iter %d" % i)
        if net.has_data_layer(phase=phase):
            output = net()
        else:
            assert((not args.gpu) or args.gpu.find(',') == -1)
            input_shapes = net.get_input_shapes()
            if not isinstance(input_shapes[0], list): input_shapes = [input_shapes]
            if not args.gpu:
                inputs = [torch.randn(*input_shape) for input_shape in input_shapes]
            else:
                device_id = int(args.gpu)
                inputs = [torch.randn(*input_shape).cuda(device_id) for input_shape in input_shapes]
            if phase == 'TEST':
                with torch.no_grad():
                    output = net(*inputs)
            else:
                output = net(*inputs)

    metric_dict = net.get_metrics()
    net.reset_metrics()
    for key, value in metric_dict.items():
        logger.info('test %s: %f' % (key, float(value)))
            
#===============================================
# other commands
#===============================================
def get_model_main(argv):
    if len(argv) != 3:
        print('Usage: ptcaffe get_model model_name')
        print('model_name is e.g. gluon:resnet50_v1, gluon:mobilenet0.5, pytorch:resnet50')
        exit()
    model_name = argv[2] # 'resnet50_v1'

    source, name = model_name.split(':')
    if source == 'gluon':
        from .gluon2ptcaffe.gluon_model import get_gluon_model 
        return get_gluon_model(name)
    elif source == 'pytorch':
        from .pytorch2ptcaffe.pytorch_model import get_pytorch_model
        from ptcaffe.utils.config import cfg
        return get_pytorch_model(name)

def export_qmodel_main(argv):
    if len(argv) != 7:
        print('Usage: ptcaffe export_qmodel input_protofile input_ptmodel output_protofile output_caffemodel output_qfile')
        exit()
    input_protofile   = argv[2]
    input_ptmodel     = argv[3]
    output_protofile  = argv[4]
    output_caffemodel = argv[5]
    output_qfile      = argv[6]
    from .export_quantization import export_quantization_model
    export_quantization_model(input_protofile, input_ptmodel, output_protofile, output_caffemodel, output_qfile)


def quantize_weight_main(argv):
    if len(argv) != 5:
        print('Usage: ptcaffe quantize_weight protofile in_ptcmodel out_ptcmodel')
        exit()
    protofile    = argv[2]
    ptcmodel     = argv[3]
    out_ptcmodel = argv[4]
    from .quantize_weight import quantize_weight
    quantize_weight(protofile, ptcmodel, out_ptcmodel)


def rename_model_main(argv):
    if len(argv) != 6:
        print('Usage: ptcaffe rename_model orig_protofile orig_ptmodel new_protofile new_ptmodel')
        print('rename layer name and get correct model')
        exit()
    from ptcaffe.caffenet import CaffeNet
    orig_protofile = argv[2]
    orig_ptmodel   = argv[3]
    new_protofile  = argv[4]
    new_ptmodel    = argv[5]
    new_net = CaffeNet(new_protofile, phase='TEST')
    new_net.load_renamed_model(orig_ptmodel)
    new_net.save_model(new_ptmodel)

    # verify correctness
    import torch
    input_shape = new_net.get_input_shapes()
    if not isinstance(input_shape[0], list): # only one data
        orig_net = CaffeNet(orig_protofile, phase='TEST')
        orig_net.load_model(orig_ptmodel)
        orig_net.set_automatic_outputs()

        new_net.set_automatic_outputs()
        input = torch.randn(*input_shape)
        output1 = orig_net(input)
        output2 = new_net(input)
        assert (type(output1) == type(output2)), "output1 and output2 are different types"
        if isinstance(output1, tuple):
            assert (len(output1) == len(output2))
            for idx in range(len(output1)):
                diff = (output1[idx].data - output2[idx].data).abs().mean()
                print("difference[%d] = %f" % (idx, diff))
        else:
            diff = (output1.data - output2.data).abs().mean()
            print("difference = %f" % diff)


def other_cmds(argv):
    if argv[1] == 'get_model':
        return get_model_main(argv)
    elif argv[1] == 'export_qmodel':
        return export_qmodel_main(argv)
    elif argv[1] == 'quantize_weight':
        return quantize_weight_main(argv)
    elif argv[1] == 'rename_model':
        return rename_model_main(argv)
