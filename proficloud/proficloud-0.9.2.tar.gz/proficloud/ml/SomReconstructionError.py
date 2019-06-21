from .AbstractModel import AbstractModelClass
import pandas as pd
import numpy as np
import somoclu
from sklearn.preprocessing import MinMaxScaler

class SomReconstructionErrorModel(AbstractModelClass):
    """
    Self-Organizing Map model with reconstruction error anomaly detection.
    https://www.sciencedirect.com/science/article/pii/S221282711830307X
    """
    
    def __init__(self):
        self.scaler = None
        """Data scaling, created during training. Used to scale data to range [0,1]. """

        self.som = None
        """Self-Organizing Map neural network"""

        self.threshold = None
        """Threshold for anomaly detection. Calculated from training data."""

        self.signal_names = None
        """Signal names"""

        self.training_side_length = 30
        """Hyperparameter, side length of SOM (x and y are equal)"""

        self.training_epochs = 100
        """Hyperparameter, number of training epochs"""

        self.training_learning_rate = 0.1
        """Hyperparameter, Initial learning rate"""
        
        self.predict_raw=False
        """Parameter for prediction. if True reconstruction error is returned. 
        If false, output > 0 marks an anomaly."""

        super(AbstractModelClass, self).__init__()


    def train(self, data):
        
        data = data.dropna()
        variance = data.var(axis=0)
        zero_variance = variance == 0.0
        zero_variance = np.insert(zero_variance.values, 0, False)
        if sum(zero_variance) > 0:
            data = data.loc[:,~zero_variance]
        
        self.scaler = MinMaxScaler(feature_range=[0,1], copy=True)
        self.scaler.fit(data.values)
        
        self.signal_names = data.columns.values.tolist()
        
        transformed_data = self.scaler.transform(data)
        data = pd.DataFrame(transformed_data, columns=self.signal_names)
        
        self.som = somoclu.Somoclu(self.training_side_length, self.training_side_length, compactsupport=False, initialization="pca")
        self.som.train(data.values, scale0=self.training_learning_rate, epochs=self.training_epochs)
        
        self.threshold = self.som.get_surface_state().min(axis=1).max()
        del self.som.activation_map
        
    def predict(self, data):
        resultList = []
        for index,row in data.iterrows():
                result = self.predict_sample(row)
                resultList.append(result)
        return resultList

    def predict_sample(self, sample):
        scaled = self.scaler.transform(sample.values.reshape(1,-1))
        prediction = self.som.get_surface_state(scaled).min(axis=1)
        
        if not self.predict_raw:
            anomaly = prediction - self.threshold
            if anomaly < 0:
                anomaly = 0
            else:
                anomaly = anomaly[0]
            return anomaly
        else:
            return prediction[0]
        
    def summary(self):
        return "Non-Linear, Multivariate Time Series Anomaly Detection\n"
        +"Based on Self-Organizing Map neural network."
        +"Side length: "+str(self.som._n_columns)+"x"+str(self.som._n_rows)
        +"Detection threshold: "+str(self.threshold)
        +"Signals: "+str(list(self.signal_names))
    