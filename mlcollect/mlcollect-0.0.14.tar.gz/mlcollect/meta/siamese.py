# import the necessary packages
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Lambda
from tensorflow.keras.optimizers import RMSprop

class Siamese:

    @staticmethod
    def euclidean_distance(vects):
        x, y = vects
        return K.sqrt(K.sum(K.square(x - y), axis=1, keepdims=True) + 1e-6)
    
    @staticmethod    
    def eucl_dist_output_shape(shapes):
        shape1, shape2 = shapes
        return (shape1[0], 1)
    
    @staticmethod        
    def contrastive_loss(y_true, y_pred):
        margin = 1
        return K.mean(y_true * K.square(y_pred) + (1 - y_true) * K.square(K.maximum(margin - y_pred, 0)))

    @staticmethod
    def build(input_a, input_b, base_network):

        feat_vecs_a = base_network(input_a)
        feat_vecs_b = base_network(input_b)
        distance = Lambda(Siamese.euclidean_distance, output_shape=Siamese.eucl_dist_output_shape)([feat_vecs_a, feat_vecs_b])
        
        rms = RMSprop()
        model = Model(inputs=[input_a, input_b], outputs=[distance])
        model.compile(loss=Siamese.contrastive_loss, optimizer=rms)
        
        return model