import xarray as xr
import umap
from keras.models import Model
from keras.layers import Dense, Input, ReLU
from keras import metrics
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import pickle

def load_xru(path):
    file = open(path, 'rb')
    xru = pickle.load(file)

    return xru

class autoencoder():
    '''
    Class to train and run a non-linear dimensionality reduction in a
    xarray.Dataset.  The encoding is performed thorugh uniform manifold
    projection (UMAP, https://github.com/lmcinnes/umap) and the decoding
    is performed with a 2-layer fully-connected network.

    '''

    def __init__(
        self, dims_to_reduce, alongwith,n_components=5, n_neighbors=3):
        '''
        Initializing the UMAP instance. TODO: Include all umap parameters
        '''
        self.n_components = n_components
        self.reducer = umap.UMAP(
        n_components=n_components,n_neighbors = n_neighbors
        )
        self.dims_to_reduce = dims_to_reduce
        self.alongwith = alongwith

    def save(self, path):
        file = open(path,'wb')
        pickle.dump(self, file) # save current object

    def _xarray_to_2D(self,array):
        array = array.stack({'dim_to_reduce':self.dims_to_reduce})
        array = array.stack({'alongwith':self.alongwith})
        array = array.dropna(dim = 'alongwith', how = 'all')
        array = array.dropna(dim = 'dim_to_reduce', how = 'any')
        array = array.transpose('alongwith','dim_to_reduce')
        return array

    def plot_embedding(self, path,cmap='rainbow'):
        if not isinstance(self.encoded,type(None)):
            print(self.encoded)
            x = self.encoded.encoded_dims.values
            y = self.encoded.alongwith.values
            z = self.encoded.values
            plt.contourf([x,y],z, cmap=cmap)
            plt.savefig(path)
            plt.close()
        else:
            raise Exception("Encode the array first")

    def fit(self, X, y=None):
        '''
        Method to train a umap encoder

        :X: xarray dataset or dataarray
        :dims_to_reduce: list of dims to reduce
        :alongwith: str dim of samples (e.g. 'time')

        :return: trained umap model

        '''
        if isinstance(X, xr.Dataset):
            X = X.to_array(dim='var')
            dims_to_reduce.append('var')

        X = self._xarray_to_2D(X)
        self.fitted_umap = self.reducer.fit(X.values)
        return self

    def transform(self,X):
        '''
        Method to run the umap encoder on new data
        :X: xarray dataset or dataarray
        :dims_to_reduce: list of dims to reduce
        :alongwith: str dim of samples (e.g. 'time')

        :return: xarray.Dataset with encoded dimensions
        '''
        if isinstance(X, xr.Dataset):
            X = X.to_array(dim='var')

        if not isinstance(self.fitted_umap , type(None)):
            X = self._xarray_to_2D(X)
            self._array = X
            encoded = self.reducer.transform(X.values)
            encoded  = xr.DataArray(encoded,
                                coords=[X['alongwith'],range(self.n_components)],
                                dims=['alongwith','encoded_dims'])

            return encoded.unstack('alongwith')

        else:
            raise Exception("Run train_encoder first")

    def train_decoder(self, x = None, y = None):
        '''
        Method to train the decoder neural network
        :x: encoded dataset
        :y: original dataset

        :return: xarray.Dataset with encoded dimensions
        '''

        if isinstance(x,type(None)):
            x = self.encoded
        else:
            raise Exception('Not implemented yet')
        if isinstance(y, type(None)):
            y = self._array
        else:
            self._array = y

        self._decoder_nn(x.values,y.values)
        return self

    def _decoder_nn(self,x,y,out_activation='linear'):
        '''
        Vanilla configuration for the decoder. TODO: allow user define
        architecture.
        '''

        epochs=30
        main_input = Input(shape=x.shape[1:], name="main_input")
        dense1 = Dense(
        100, bias_initializer="zeros", use_bias=True, activation="relu")(main_input)
        dense2 = Dense(
        100, bias_initializer="zeros", use_bias=True, activation="relu")(dense1)
        out = Dense(y.shape[1], activation=out_activation)(dense2)
        model = Model(main_input, out)
        model.compile(
            loss="mean_squared_error",
            metrics=[metrics.mae, metrics.mse],
            optimizer="adam",
        )
        history = model.fit(
            x,
            y,
            epochs=epochs,
            validation_split=0.2,
            shuffle=True,
            verbose=2,
            batch_size=28,
        )
        self.decoder=model

    def decode(self,x=None):
        '''
        Method to run the decoder NN on new data
        :x: xarray dataset or dataarray
        '''
        if not isinstance(self.decoder , type(None)):
            if isinstance(x,type(None)):
                x = self.encoded

            decoded = self.decoder.predict(x.values)

            new_ds = xr.DataArray(decoded,
                                coords=self._array.coords,
                                dims=self._array.dims)


            self.decoded = new_ds.unstack(['dim_to_reduce','alongwith'])
            return self.decoded

        else:
            raise Exception("Run train_decoder first")

class normalizer():
    '''
    Normalizer for xarray datasets
    '''

    def __init__(self, alongwith):
        self._alongwith = alongwith
    def fit(self, X, y=None):
        '''
        :ds: xarray  dataset
        :alongwith: list of sample dimensions
        '''
        if isinstance(X, xr.Dataset):
            X = X.to_array(dim='var')

        X = X.stack({'alongwith': self._alongwith})
        self._mean = X.mean('alongwith')
        self._stdv = X.var('alongwith')**0.5
        return self

    def transform(self, X):
        if isinstance(X, xr.Dataset):
            X = X.to_array(dim='var')
        X = X.stack({'alongwith': self._alongwith})
        X = (X - self._mean)/self._stdv
        return X.unstack('alongwith')
    def inverse_transform(self, X):
        if isinstance(X, xr.Dataset):
            X = X.to_array(dim='var')
        X = X.stack({'alongwith': self._alongwith})
        X = X * self._stdv + self._mean

        return X.unstack('alongwith')

if __name__ == '__main__':

    input_array = xr.open_dataarray('/path/to/ncdf')
    normalizer = xr.normalizer(alongwith=['time'])
    normalizer = normalizer.fit(input_array)
    input_array = normalizer.transform(input_array)
    model = autoencoder(n_components=100, n_neighbors=2,
                        dims_to_reduce=['lat','lon'],alongwith=['time'])
    model = model.fit(input_array)
    encoded_array = model.transform(input_array)
    model = model.train_decoder(encoded_array)
    decoded_array = model.decode()
