#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


import tensorflow as tf
slim = tf.contrib.slim


def build_transfer_graph(inputs, reuse=False, bottleneck_layers=[64], outputs=128):
    """
    Build a simple graph used for transfer learning transfer graph with an arbitrary size in the
    output
    
    Parameters
    ----------
    
      inputs:
         The input tensor
         
      reuse: optional
         Reuse Variables?
       
      bottleneck_layers: list, optional
         Number of layers in the bottleneck. So far all will be RELY
      
      outputs:
         Number of neurons in the output
       
    Returns
    -------
      
      prelogits:
         Output tensor
      
      end_points: dict
         Dictionary containing the tensors for each endpoint
    
    """

    with tf.variable_scope('Transfer', reuse=reuse):
        end_points={}
        
        for n_outputs, i in zip(bottleneck_layers, range(len(bottleneck_layers))):
            scope = "NonLinearity_{0}".format(i)
            prelogits = slim.fully_connected(inputs, n_outputs, activation_fn=tf.nn.relu, 
                                             weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                             weights_regularizer=slim.l2_regularizer(0.001),
                                             scope=scope)
            end_points[scope] = prelogits

        prelogits = slim.fully_connected(prelogits, outputs, activation_fn=None, 
                                         weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                         scope='Bottleneck')
        end_points['Bottleneck2'] = prelogits

    return prelogits, end_points

