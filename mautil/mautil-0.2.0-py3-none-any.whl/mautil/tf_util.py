import numpy as np
import tensorflow as tf
from . import util


def get_vars(scopes):
    vars = []
    for scope in scopes:
        vars += tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope)
    return vars


def gumbel_softmax(logits, gamma, eps=1e-20):
    U = tf.random_uniform(tf.shape(logits))
    G = -tf.log(-tf.log(U + eps) + eps)
    return tf.nn.softmax((logits + G) / gamma)
    #return tf.nn.softmax((logits+eps) / gamma)


def rnn_decode(cell, inputs, loop_func, max_len, initial_state=None):
    outs = []; hs = []
    h = initial_state
    for t in range(max_len):
        cell_out, h = cell(inputs, h)
        hs.append(h)
        inputs, out = loop_func(cell_out)
        outs.append(out)
    hs = tf.stack(hs, 1)
    if isinstance(initial_state, tuple):
        if len(initial_state) == 1:
            hs = tf.squeeze(hs, 0)  # [time, batch_size,::]
            hs = transpose(hs, 0, 1)  # [batch_size, time, ::]

    return hs, tf.stack(outs, 1)

def restore_vars(sess, checkpoint_path, meta_path):
    saver = tf.train.import_meta_graph(meta_path)
    saver.restore(sess, checkpoint_path)

def tensor_to_feature(tensor):

    return tf.train.Feature(bytes_list=bytes_list)


def _int64_feature(values):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=values))

def _float_feature(values):
  return tf.train.Feature(float_list=tf.train.FloatList(value=values))

def ds2tfrecord(ds, input_features, filepath):
    convert_funcs = {}
    for fea in input_features:
        if fea.dtype  in [tf.int32, tf.int16, tf.int64]:
            convert_funcs[fea.name] = _int64_feature
        elif fea.dtype in [tf.float32, tf.float64]:
            convert_funcs[fea.name] = _float_feature
        else:
            raise NotImplemented

    with tf.python_io.TFRecordWriter(filepath) as writer:
        feat_dict = ds.make_one_shot_iterator().get_next()
        num = 0
        with tf.Session() as sess:
            try:
                while True:
                    features = {}
                    feat_npy = sess.run(feat_dict)
                    for name, npy in feat_npy.items():
                        features[name] = convert_funcs[name](npy.flatten())
                    # Create a Features message using tf.train.Example.
                    example_proto = tf.train.Example(features=tf.train.Features(feature=features))
                    example_string = example_proto.SerializeToString()
                    # Write to TFRecord
                    writer.write(example_string)
                    num += 1
            except tf.errors.OutOfRangeError:
                pass
    return num

def set_tfloglevel(level=1):
    tf_loglevel = {0: tf.logging.DEBUG, 1: tf.logging.INFO, 2: tf.logging.WARN, 3: tf.logging.ERROR}
    tf.logging.set_verbosity(tf_loglevel[level])

def gather_seqs(seqs, gather_inds):
    n = len(gather_inds.get_shape())
    shape = tf.shape(gather_inds)
    r_shape = [shape[0]]
    inds=tf.range(shape[0]); tile=[1]
    inds = tf.expand_dims(inds, -1)
    for i in range(1, n-1):
        inds=tf.expand_dims(inds, i)
        inds = tf.tile(inds, tile+[shape[i]] +[1])
        r_shape.append(shape[i])
        r_inds = tf.range(shape[i])
        r_inds = tf.expand_dims(r_inds, -1)
        for j in tile[::-1]:
            r_inds = tf.expand_dims(r_inds, 0)
        r_inds = r_inds * tf.ones(r_shape+[1], tf.int32)
        inds = tf.concat([inds, r_inds], -1)
        tile += [1]
    inds = tf.tile(tf.expand_dims(inds, -2), tile + [shape[-1]] + [1])
    gather_inds = tf.expand_dims(gather_inds, -1)
    gather_inds = tf.concat([inds, gather_inds], -1)
    rst = tf.gather_nd(seqs, gather_inds)
    return rst


def transpose_nd(tensor, dims1, dims2):
    assert len(dims1) == len(dims2), 'num of dims must be same'
    assert len(dims1+dims2) == len(set(dims1+dims2)), 'there must have no dup of dim'
    ndims = tensor.shape.ndims
    shape = np.arange(ndims)
    for dim1, dim2 in zip(dims1, dims2):
        dim = shape[dim1]
        shape[dim1] = shape[dim2]
        shape[dim2] = dim
    return tf.transpose(tensor, shape)


def transpose(tensor, dim1, dim2):
    return transpose_nd(tensor, [dim1], [dim2])


def create_rnn_cell(dims, cell_cls='tf.nn.rnn_cell.GRUCell', dropout=None):
    """
     
    :param dims: list of cell dim [128, 128]
    :param cell_cls:
    :return:
    """
    cell_cls = util.get_class(cell_cls)
    cells = []
    for dim in dims:
        cell = cell_cls(dim)
        if dropout is not None:
            cell = tf.nn.rnn_cell.DropoutWrapper(cell, input_keep_prob=dropout)
        cells.append(cell)
    multi_cell = tf.nn.rnn_cell.MultiRNNCell(cells, state_is_tuple=True)
    return multi_cell
