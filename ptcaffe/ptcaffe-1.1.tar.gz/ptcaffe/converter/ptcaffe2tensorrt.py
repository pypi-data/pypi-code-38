import tensorrt as trt

input_size = 224
input_channels = 3

def ptcaffe2tensorrt(input_prototfile, input_weightfile, output_engine):
    cf_net = CaffeNet(input_protofile, phase='TEST')
    cf_net.set_automatic_outputs()
    cf_net.load_weights(input_weightfile)

    G_LOGGER = trt.infer.ConsoleLogger(trt.infer.LogServerity.ERROR)
    builder = trt.infer.create_infer_builder(G_LOGGER)
    
    trt_net = builder.create_network()
    
    data = trt_net.add_input("data", trt.infer.DataType.FLOAT, (input_channels, input_size, input_size))
    assert(data)

    layers = cf_net.net_info['layers']
    cf_models = cf_net.models
    trt_models = dict()
    blob_from = dict()
    for layer in layers:
        ltype = layer['type']
        lname = layer['name']
        if ltype == 'Convolution':
            conv_w = models[lname].weight.numpy().reshape(-1)
            conv_b = models[lname].bias.numpy().reshape(-1)
            conv_l = trt_net.add_convolution(data, 

