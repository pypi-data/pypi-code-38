import numpy as np, logging, sys
import mautil
import tensorflow as tf
from mautil.tf_models import TF, InputFeature
from mautil.tf_layers import Dense
from mautil.training import Trainer
from sklearn.model_selection import train_test_split
from mautil import TrainArgParser


class Model(TF):
    def _init_input_features(self):
        features = []
        features.append(InputFeature('inputs', [None, 2],tf.float32)) 
        features.append(InputFeature('tgt', [None],tf.float32))
        return features
        
    def _add_main_graph(self):
        outs = self.inputs
        for dim in [16,16,1]:
            outs = Dense(dim, activation=tf.nn.relu)(outs)
        outs = tf.squeeze(outs, -1)
        self._loss = tf.losses.mean_squared_error(outs, self.tgt)

def gen_data():
    x = np.random.rand(1000,2)
    y = x[:,0] * 2 + x[:,1] * 3 + 1 
    x, xV, y, yV = train_test_split(x, y, test_size = 0.1, shuffle=False)

    x = {'inputs':x}
    xV = {'inputs':xV}
    y = {'tgt':y}
    yV = {'tgt':yV}
    data = {'train':(x, y), 'validate':(xV, yV)}
    return data



if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s:%(threadName)s %(message)s')
    trainer = Trainer('test_model', 9527)
    args = TrainArgParser.load_args()
    if not args.method_or_model:
        args.model_names='Model'
    data = gen_data()
    trainer.train_model(data, args, globals(), process_data=False)
