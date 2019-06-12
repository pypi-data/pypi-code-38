# import the necessary packages
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Lambda
from tensorflow.keras.layers import concatenate
from tensorflow.keras.optimizers import Adam

class SiameseTripletLoss:
    
    @staticmethod        
    def triplet_loss(y_true, y_pred):

        dim = y_pred.shape[1] / 3
        anchor, positive, negative = y_pred[ : , 0 : dim ], y_pred[ : , dim : 2 * dim], y_pred[ : , 2 * dim :]
        pos_dist = K.sum(K.square(anchor - positive), axis=-1)
        neg_dist = K.sum(K.square(anchor - negative), axis=-1)
        basic_loss = pos_dist - neg_dist + 0.2
        loss = K.sum(K.maximum(basic_loss, 0.0))
      
        return loss

    @staticmethod
    def build(input_a, input_b, input_c, base_network):
        
        feat_vecs_a = base_network(input_a)
        feat_vecs_b = base_network(input_b)
        feat_vecs_c = base_network(input_c)

        stacked_dists = concatenate([feat_vecs_a, feat_vecs_b, feat_vecs_c], axis=-1)
        outputs = Lambda(lambda x: K.l2_normalize(x, axis=-1))(stacked_dists)
        model = Model(inputs=[input_a, input_b, input_c], outputs=outputs)

        rms = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        model.compile(loss=SiameseTripletLoss.triplet_loss, optimizer=rms)
