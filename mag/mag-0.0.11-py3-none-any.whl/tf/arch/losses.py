import tensorflow as tf

def multilabel_loss(inputs, labels):
    with tf.variable_scope('multilabel_loss'):
        return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=inputs))
