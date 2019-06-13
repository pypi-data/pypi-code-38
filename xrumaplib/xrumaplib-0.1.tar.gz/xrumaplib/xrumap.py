import xarray as xr
import umap
from keras.models import Model
from keras.layers import Dense, Input, ReLU
from keras import metrics

class autoencoder():
    '''
    Class to train and run a non-linear dimensionality reduction in a
    xarray.Dataset.  The encoding is performed thorugh uniform manifold
    projection (UMAP, https://github.com/lmcinnes/umap) and the decoding
    is performed with a 2-layer fully-connected network.

    '''

    def __init__(self, n_components=5, n_neighbors=3):
        '''
        Initializing the UMAP instance. TODO: Include all umap parameters
        '''
        self.n_components = n_components
        self.reducer = umap.UMAP(
        n_components=n_components,n_neighbors = n_neighbors
        )

    def train_encoder(self, ds, dims_to_reduce, alongwith):
        '''
        Method to train a umap encoder

        :ds: xarray dataset or dataarray
        :dims_to_reduce: list of dims to reduce
        :alongwith: str dim of samples (e.g. 'time')

        :return: trained umap model

        '''
        if isinstance(ds,xr.DataArray):
            array = ds
        elif isinstance(ds, xr.Dataset):
            array = ds.to_array(dim='var')
            dims_to_reduce.append('var')
            
        self.dims_to_reduce = dims_to_reduce
        self.alongwith = alongwith
        array = array.stack({'dim_to_reduce':dims_to_reduce})
        array = array.dropna(dim = alongwith, how = 'all')
        array = array.dropna(dim = 'dim_to_reduce', how = 'any')
        self.fitted_umap = self.reducer.fit(array.values)
        return self.fitted_umap

    def encode(self,ds):
        '''
        Method to run the umap encoder on new data
        :ds: xarray dataset or dataarray
        :dims_to_reduce: list of dims to reduce
        :alongwith: str dim of samples (e.g. 'time')

        :return: xarray.Dataset with encoded dimensions
        '''

        if isinstance(ds,xr.DataArray):
            array = ds
        elif isinstance(ds, xr.Dataset):
            array = ds.to_array(dim='var')

        if not isinstance(self.fitted_umap , type(None)):
            array = array.stack({'dim_to_reduce':self.dims_to_reduce})
            array = array.dropna(dim = self.alongwith, how = 'all')
            array = array.dropna(dim = 'dim_to_reduce', how = 'any')
            self._array = array
            encoded = self.reducer.transform(array.values)
            self.encoded  = xr.DataArray(encoded,
                                coords=[array[self.alongwith].values,range(self.n_components)],
                                dims=[self.alongwith,'encoded_dims'])
            self.encoded = encoded_array
            return self.encoded

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
            y = y.stack({'dim_to_reduce':self.dims_to_reduce})
            y = y.dropna(dim = self.alongwith, how = 'all')
            y = y.dropna(dim = 'dim_to_reduce', how = 'any')

        self._decoder_nn(x.values,y.values)

        print(None)
    def _decoder_nn(self,x,y):
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
        out = Dense(y.shape[1], activation="linear")(dense2)
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
            else:
                raise Exception('Not implemented yet')

            decoded = self.decoder.predict(x.values)

            new_ds = xr.DataArray(decoded,
                                coords=self._array.coords,
                                dims=self._array.dims)


            self.decoded = new_ds.unstack('dim_to_reduce')

        else:
            raise Exception("Run train_decoder first")

if __name__ == '__main__':

    cpc = xr.open_dataarray(conf.cpc_path)
    model = autoencoder(n_components=100, n_neighbors=2)
    model.train_encoder(cpc,dims_to_reduce=['lat','lon'],alongwith='time')
    model.encode(cpc)
    model.train_decoder()
    model.decode()
