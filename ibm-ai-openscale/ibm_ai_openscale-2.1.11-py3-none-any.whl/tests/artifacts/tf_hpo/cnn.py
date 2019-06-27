from __future__ import print_function
import sys
import os
import json
import input_data
import tensorflow as tf

from emetrics import EMetrics

model_path = os.environ["RESULT_DIR"]+"/output_model_dir"

# Parameters
num_steps = 20 
learning_rate = 0.001
batch_size = 512
display_step = 5

# Network Parameters
num_input = 784 # MNIST data input (img shape: 28*28)
num_classes = 10 # MNIST total classes (0-9 digits)

x = tf.placeholder(tf.float32, [None, num_input])
y_ = tf.placeholder(tf.float32, [None, num_classes])


def define_variable(name, shape, initializer):
    return tf.get_variable(name,
                           shape=shape,
                           initializer=initializer)

def tensor_shape(x):
    return list(map(lambda x: x.value, x.shape[1:]))

def conv2d(x, num_filters, filter_size , index):
    height, width, depth  = tensor_shape(x)
    
    W = define_variable("w_conv" + str(index),
                             (filter_size, filter_size,
                              depth, num_filters),
                             initializer=tf.contrib.layers.xavier_initializer())
    stride = 1
        
    conv_layer = tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding='SAME')
    b = define_variable("b_conv" + str(index), num_filters,
                             tf.constant_initializer(0))
    return tf.nn.relu(tf.nn.bias_add(conv_layer, b))

def max_pool_2x2(x, filter_size):
    stride = 1
    return tf.nn.max_pool(x, ksize=[1, filter_size, filter_size, 1],
                              strides=[1, stride, stride, 1], padding='SAME')

def fully_conn(x, size, index, first_fc, is_last):
    if first_fc:
        height, width, depth  = tensor_shape(x)
        first_dim = height * width * depth
        first_dim = int(first_dim)
        x = tf.reshape(x, [-1, first_dim])
        first_fc = False
        
    else:
        depth = x.shape[1].value
        first_dim = depth
    W = define_variable("W_fc" + str(index), (first_dim, size),
                        initializer=tf.contrib.layers.xavier_initializer())

    b = define_variable("h_fc" + str(index), size,
                        initializer=tf.constant_initializer(0))
    temp = tf.add(tf.matmul(x, W),  b)
    if (not is_last):
        temp = tf.nn.relu(temp)
    return temp

# Build a convolutional neural network
def conv_net(nn, conv_filter_size1, conv_filter_size2, pool_filter_size, fc):
    nn = tf.reshape(nn, shape=[-1, 28, 28, 1])
    nn = conv2d(nn, 64, conv_filter_size1, 1)
    nn = max_pool_2x2(nn, pool_filter_size)
    nn = conv2d(nn, 256, conv_filter_size2, 2)
    nn = fully_conn(nn, fc, 1, True, False)
    nn = fully_conn(nn, num_classes, 2, False, True)
    return nn

def getCurrentSubID():
    if "SUBID" in os.environ:
        return os.environ["SUBID"]
    else:
        return None


def run_cnn(data_dir):
    curr_iter = 0
    mnist = input_data.read_data_sets(data_dir + "/train-images-idx3-ubyte.gz", data_dir + "/train-labels-idx1-ubyte.gz", data_dir + "/t10k-images-idx3-ubyte.gz", data_dir +"/t10k-labels-idx1-ubyte.gz",  one_hot=True)

    with open("config.json", 'r') as f:
        json_obj = json.load(f)
    learning_rate = json_obj["learning_rate"]
    #conv_filter_size1 = json_obj["conv_filter_size1"]
    conv_filter_size1 = 8
    conv_filter_size2 = 8
    pool_filter_size = 2
    fc = 2

    print("learning rate is ", learning_rate)
    print("conv_filter_size1 is ", conv_filter_size1)
    print("conv_filter_size2 is ", conv_filter_size2)
    print("pool_filter_size is ", pool_filter_size)
    print("fully connected is ", fc)

    y_conv  = conv_net(x, conv_filter_size1, conv_filter_size2, pool_filter_size, fc)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
    predictor = tf.argmax(y_conv, 1, name="predictor")
    correct_prediction = tf.equal(predictor, tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    subid = getCurrentSubID()

    print("Current subid: %s" % subid)

    with tf.Session() as sess:

        sess.run(tf.global_variables_initializer())
        # saver = tf.train.Saver(max_to_keep=1)
        print("initialized all vars")
        with EMetrics.open(subid) as em:
            while curr_iter < num_steps:
                curr_iter += 1
                print(curr_iter)
                batch_x, batch_y = mnist.train.next_batch(batch_size)
                feed_dict = {x: batch_x, y_: batch_y}
                _, cost_val = sess.run([optimizer, cost],
                                             feed_dict=feed_dict)
                sys.stdout.flush()

                if (curr_iter+1) % display_step == 0:
                    train_acc = compute_accuracy(sess, accuracy, mnist.train, batch_size)
                    em.record("train", curr_iter, {"accuracy": train_acc})
                    val_acc = compute_accuracy(sess, accuracy, mnist.validation, batch_size)
                    em.record(EMetrics.TEST_GROUP,curr_iter,{"accuracy":val_acc})

        # save model
        classification_inputs = tf.saved_model.utils.build_tensor_info(x)
        classification_outputs_classes = tf.saved_model.utils.build_tensor_info(predictor)

        classification_signature = (
            tf.saved_model.signature_def_utils.build_signature_def(
                inputs={
                    tf.saved_model.signature_constants.CLASSIFY_INPUTS:
                        classification_inputs
                },
                outputs={
                    tf.saved_model.signature_constants.CLASSIFY_OUTPUT_CLASSES:
                        classification_outputs_classes
                },
                method_name=tf.saved_model.signature_constants.CLASSIFY_METHOD_NAME))

        print("classification_signature content:")
        print(classification_signature)

        builder = tf.saved_model.builder.SavedModelBuilder(model_path)
        legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
        builder.add_meta_graph_and_variables(
            sess, [tf.saved_model.tag_constants.SERVING],
            signature_def_map={
                'predict_images': classification_signature,
            },
            legacy_init_op=legacy_init_op)

        builder.save()

def compute_accuracy(sess, accuracy, dataset, batch_size):
    num_batches = int(dataset.num_examples // batch_size)
    sum_acc = 0
    for i in range(num_batches):
        batch_x, batch_y = dataset.next_batch(batch_size)
        feed_dict = {x: batch_x, y_: batch_y}
        acc = sess.run(accuracy, feed_dict=feed_dict)
        sum_acc += acc
    return sum_acc / num_batches

def main(argv):
    data_dir = argv[2]
    run_cnn(data_dir)

if __name__ == "__main__":
    main(sys.argv)
