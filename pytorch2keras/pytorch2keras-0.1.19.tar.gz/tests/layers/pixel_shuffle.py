import numpy as np
import torch
import torch.nn as nn

# import tensorflow as tf
# import keras
# config = tf.ConfigProto(intra_op_parallelism_threads=1, 
#                         inter_op_parallelism_threads=1, 
#                         allow_soft_placement=False, 
#                         device_count = {'CPU': 1})
# session = tf.Session(config=config)
# keras.backend.set_session(session)

from torch.autograd import Variable
from pytorch2keras.converter import pytorch_to_keras


class pixel_shuffle(nn.Module):
    def __init__(self, scale_factor):
        super(pixel_shuffle, self).__init__()
        self.scale_factor = scale_factor

    def forward(self, input):
        scale_factor = self.scale_factor
        _, in_channels, in_height, in_width = input.shape

        in_channels = int(in_channels)
        in_height = int(in_height)
        in_width = int(in_width)

        out_channels = in_channels // (scale_factor * scale_factor)
        out_height = in_height * scale_factor
        out_width = in_width * scale_factor

        if scale_factor >= 1:
            input_view = input.view([-1, out_channels, scale_factor, scale_factor, in_height, in_width])
            shuffle_out = input_view#.permute(0, 1, 4, 2, 5, 3)

        return shuffle_out.contiguous() #.view([-1, out_channels, out_height, out_width])

# graph(%0 : Float(1, 4, 64, 64)) {
#   %2 : Tensor = onnx::Constant[value= -1   4   1   1  64  64 [ CPULongType{6} ]](), scope: LayerTest/pixel_shuffle[psh]
#   %3 : Float(1, 4, 1, 1, 64, 64) = onnx::Reshape(%0, %2), scope: LayerTest/pixel_shuffle[psh]
#   %5 : Float(1, 4, 64!, 1!, 64!, 1!) = onnx::Transpose[perm=[0, 1, 4, 2, 5, 3]](%3), scope: LayerTest/pixel_shuffle[psh]
#   %7 : Tensor = onnx::Constant[value= -1   4  64  64 [ CPULongType{4} ]](), scope: LayerTest/pixel_shuffle[psh]
#   %8 : Float(1, 4, 64, 64) = onnx::Reshape(%5, %7), scope: LayerTest/pixel_shuffle[psh]
#   return (%8);
# }

# graph(%0 : Float(1, 4, 64, 64)) {
#   %2 : Tensor = onnx::Constant[value= -1   1   1   4  64  64 [ CPULongType{6} ]](), scope: LayerTest/PixelShuffle[psh]
#   %3 : Tensor = onnx::Reshape(%0, %2), scope: LayerTest/PixelShuffle[psh]
#   %4 : Tensor = onnx::Transpose[perm=[0, 1, 4, 2, 5, 3]](%3), scope: LayerTest/PixelShuffle[psh]
#   %5 : Tensor = onnx::Constant[value= -1   4  64  64 [ CPULongType{4} ]](), scope: LayerTest/PixelShuffle[psh]
#   %6 : Float(1, 4, 64, 64) = onnx::Reshape(%4, %5), scope: LayerTest/PixelShuffle[psh]
#   return (%6);
# }



class LayerTest(nn.Module):
    def __init__(self):
        super(LayerTest, self).__init__()
        self.psh = pixel_shuffle(1)

    def forward(self, x):
        x = self.psh(x.contiguous())
        return x


def check_error(output, k_model, input_np, epsilon=1e-5):
    pytorch_output = output.data.numpy()
    keras_output = k_model.predict(input_np)

    error = np.max(pytorch_output - keras_output)
    print('Error:', error)

    assert error < epsilon
    return error


def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
    from tensorflow.python.framework.graph_util import convert_variables_to_constants
    graph = session.graph
    with graph.as_default():
        freeze_var_names = \
            list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = convert_variables_to_constants(session, input_graph_def,
                                                      output_names, freeze_var_names)
        return frozen_graph




if __name__ == '__main__':
    max_error = 0
    for i in range(10):
        psh_1 = pixel_shuffle(2)
        # psh_2 = nn.PixelShuffle(2)

        model = LayerTest()
        model.eval()

        input_np = np.random.uniform(0, 1, (1, 4, 64, 64))
        input_var = Variable(torch.FloatTensor(input_np))
        
        # print(psh_1(input_var) - psh_2(input_var))

        output = model(input_var)

        k_model = pytorch_to_keras(model, input_var, (4, 64, 64,), verbose=True)
        k_model.summary()

        from keras import backend as K
        import tensorflow as tf
        frozen_graph = freeze_session(K.get_session(),
                                      output_names=[out.op.name for out in k_model.outputs])

        tf.train.write_graph(frozen_graph, ".", "my_model.pb", as_text=False)
        print([i for i in k_model.outputs])


        print(k_model.to_json())
        k_model.save_weights('test.h5')
        error = check_error(output, k_model, input_np)
        if max_error < error:
            max_error = error

    print('Max error: {0}'.format(max_error))
