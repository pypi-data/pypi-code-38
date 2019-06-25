
def caffemodel2prototxt(model_name, deploy_name):
    from ptcaffe.proto import caffe_pb2
    with open(model_name, 'rb') as f:
        caffemodel = caffe_pb2.NetParameter()
        caffemodel.ParseFromString(f.read())

    for item in caffemodel.layers:
        item.ClearField('blobs')
    for item in caffemodel.layer:
        item.ClearField('blobs')

    with open(deploy_name, 'w') as f:
        f.write(str(caffemodel))

def ptcmodel2prototxt(model_name, deploy_name):
    import torch
    from ptcaffe.utils.prototxt import save_prototxt
    ptcmodel = torch.load(model_name)
    net_info = ptcmodel['net_info']
    save_prototxt(net_info,deploy_name)

def main():
    import sys
    if len(sys.argv) != 3:
        print('Usage: model2prototxt weight_file prototxt_file')

    weight_file = sys.argv[1]
    proto_file = sys.argv[2]
    if weight_file.find('.caffemodel') >= 0:
        caffemodel2prototxt(weight_file, proto_file)
    elif weight_file.find('.ptcmodel') >= 0:
        ptcmodel2prototxt(weight_file, proto_file)
