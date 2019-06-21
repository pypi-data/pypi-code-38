#!/usr/bin/env python
"""
    Keras integration in Xarray for rapid NN model builds

    TODO Implement padding

        https://machinelearningmastery.com/data-preparation-variable-length-input-sequences-sequence-prediction/
        https://datascience.stackexchange.com/questions/26366/training-an-rnn-with-examples-of-different-lengths-in-keras
        https://github.com/farizrahman4u/recurrentshop


        https://github.com/keras-team/keras/issues/40
        https://github.com/keras-team/keras/issues/10017
    Todo Ensure continuity
"""


import xarray as xr
import pickle
import os
import numpy as np
import pandas as pd
import warnings
import copy

from sklearn.model_selection import train_test_split

from keras.layers import Dense, Dropout, GRU, Input, Flatten, Reshape
from keras import metrics
from keras.callbacks import ModelCheckpoint
from keras.models import Model

conf_seq = {
    'epochs':2,
    'test_size':0.2,
    'batch_size':30}

def _common_index(list1, list2):
    return [element for element in list1 if element in list2]

def load_xrk(xrk_dir_path):
    file = open(xrk_dir_path, 'rb')
    xrk = pickle.load(file)

    return xrk

class Xrk_Seq_Model():
    """
    Integration between Xarray and Keras
    for Generic Sequence Prediction
    """

    def __init__(self, common_sample_dim, idx_seq_x, idx_seq_y, conf_seq=None):
        self.common_sample_dim = common_sample_dim
        self.idx_seq_x =  idx_seq_x
        self.idx_seq_y = idx_seq_y

        self.model = None
        self.history = None

        cwd = os.getcwd()
        # dir_model = '/.xrk_models'
        # os.makedirs(cwd+dir_model)
        self.model_path = cwd + '/.xrk_model.h5'

        if conf_seq == None:
            self.conf_seq = conf_seq


    def fit(self, ds_x, ds_y):

        common_sample_dim = self.common_sample_dim
        idx_seq_x =  self.idx_seq_x
        idx_seq_y = self.idx_seq_y

        ds_x, ds_y = self._get_attributes_and_assert_arguments_for_xrk_fit(ds_x, ds_y, common_sample_dim, idx_seq_x, idx_seq_y)

        ds_x_seq = self._to_xrk_format(ds_x, idx_seq_x)
        ds_y_seq = self._to_xrk_format(ds_y, idx_seq_y)


        if (len(ds_x_seq) ==0) or len(ds_y_seq) ==0:
            warnings.warn('XRK No data to train the model')

        # Get same sample indexes
        cidx = _common_index(ds_x_seq.coords[self.common_sample_dim].values, ds_y_seq.coords[self.common_sample_dim].values)
        ds_x_seq = ds_x_seq.sel({self.common_sample_dim:cidx})
        ds_y_seq = ds_y_seq.sel({self.common_sample_dim:cidx})

        self.coords_x_seq = ds_x_seq.coords
        self.coords_y_seq = ds_y_seq.coords
        self.dims_x_seq = ds_x_seq.dims
        self.dims_y_seq = ds_y_seq.dims

        # Sequence model
        model, history = self._NN_sequence(ds_x_seq, ds_y_seq)

        self.model = model
        self.history = history

        return self

    def predict(self, ds_x):
        # The dim 'sample'of ds_x of length N is assumed to represent the sequence
        # of length N.
        ds_x_seq = self._to_xrk_format(ds_x, range(len(ds_x.coords[self.common_sample_dim])))
        y_pred = self.model.predict(ds_x_seq) # Nmpy array prediction

        # Reconstruct original Y array
        # Note: reconstruction works only homogeneous sample index # TODO Implement for none date sample index
        if self.sample_dim_is_date:
            date_at_t0 = pd.to_datetime(ds_x_seq.coords[self.common_sample_dim].values[0]) - pd.Timedelta(self.idx_seq_x[0], unit=self.freq_sample_x)
            sample_index_y = [ date_at_t0 + pd.Timedelta(idx_y, unit=self.freq_sample_y) for idx_y in self.idx_seq_y]

        coords_pred = self.coords_y_seq
        coords_pred = coords_pred.to_dataset().isel({self.common_sample_dim:[1]})
        coords_pred['seq'] = sample_index_y
        coords_pred = coords_pred.squeeze(dim=self.common_sample_dim,drop=True)
        coords_pred = coords_pred.rename({'seq': self.common_sample_dim})

        ds_y_pred = xr.DataArray(y_pred[0,:,:],coords=coords_pred.coords, dims=[self.common_sample_dim,'feature'])
        ds_y_pred = ds_y_pred.unstack('feature')

        return ds_y_pred


    def save(self, xrk_dir_path):

        file = open(xrk_dir_path,'wb')
        pickle.dump(self, file) # save current object

    def _get_attributes_and_assert_arguments_for_xrk_fit(self, ds_x, ds_y, common_sample_dim, idx_seq_x, idx_seq_y):
        self.common_sample_dim = common_sample_dim
        self.idx_seq_x = idx_seq_x
        self.idx_seq_y = idx_seq_y

        self.coords_x = ds_x.coords
        self.coords_y = ds_y.coords
        self.dims_x = ds_x.dims
        self.dims_y = ds_y.dims

        self.sample_dim_is_date = isinstance(self.coords_x[self.common_sample_dim].values[0], np.datetime64) # get type of sample axis
        if self.sample_dim_is_date: # TODO to inplement for none date sample index
            self.freq_sample_x = pd.infer_freq(pd.DatetimeIndex(ds_x.coords[common_sample_dim].values[idx_seq_x]), warn=True)
            self.freq_sample_y = pd.infer_freq(pd.DatetimeIndex(ds_y.coords[common_sample_dim].values[idx_seq_x]), warn=True)

            full_x_index = pd.date_range(ds_x.coords[common_sample_dim].values[0],ds_x.coords[common_sample_dim].values[-1])
            full_y_index = pd.date_range(ds_y.coords[common_sample_dim].values[0],ds_y.coords[common_sample_dim].values[-1])

            if not len(full_x_index) == len(ds_x.coords[common_sample_dim].values):
                warnings.warn('Xrk Warning X index is not continuous. Sample index is being reindexed')
                ds_x = ds_x.reindex({common_sample_dim:full_x_index})

            if not len(full_y_index) == len(ds_y.coords[common_sample_dim].values):
                warnings.warn('Xrk Warning Y index is not continuous. Sample index is being reindexed')
                ds_y = ds_y.reindex({common_sample_dim: full_y_index})

            assert self.freq_sample_x != None, 'Could not infer X sample date frequency'
            assert self.freq_sample_y != None, 'Could not infer Y sampldate frequency'
            # assert self.freq_sample_x == self.freq_sample_y, 'Date frequency between X and Y must be equal'

        return ds_x, ds_y


    def _to_xrk_format(self, ds, idx_seq):
        # ds = ds.rename({self.common_sample_dim: 'sample'}) # TODO remove 'sample' use directly self.common_sample_dim
        features_dims = list(ds.dims)
        features_dims.remove(self.common_sample_dim)
        print(ds)
        ds = ds.stack({'feature': features_dims})
        ds = ds.dropna(dim='feature', how='all')
        ds = ds.dropna(dim=self.common_sample_dim, how='all')
        ds = ds.dropna(dim=self.common_sample_dim, how='any')  # Todo to remove, Y must have not NAN at start
        # ds = ds.dropna(dim='feature', how='any')
        ds_seq = self._get_xr_seq(ds, commun_sample_dim=self.common_sample_dim, idx_seq=idx_seq)
        ds_seq = ds_seq.dropna(dim=self.common_sample_dim,how='any')  # To remove the new NAN formed by the sequence formation in the sample axis
        ds_seq = ds_seq.transpose(self.common_sample_dim, 'seq', 'feature')

        return ds_seq


    def _get_xr_seq(self, ds, commun_sample_dim, idx_seq):
        dss = []
        for idx in idx_seq:
            dss.append(ds.shift({commun_sample_dim: -idx}))

        dss = xr.concat(dss, dim='seq')
        dss = dss.assign_coords(seq=idx_seq)

        return dss

    def _NN_sequence(self, x, y):
        """
        For reminder:
            GRU input data
            Samples. One sequence is one sample. A batch is comprised of one or more samples.
            Time Steps. One time step is one point of observation in the sample.
            Features. One feature is one observation at a time step.

        :param x: numpy array, exploratory input data with the shape Samples/Time Steps/ Features
        :param x2: numpy array, auxilary input
        :param y: numpy array, response data
        :param model_path: model outpath
        :return: model history
        """

        model_path = self.model_path

        # NN
        main_input = Input(shape=x.shape[1:], name='main_input')
        gru = GRU(20, return_sequences=True)(main_input)
        flatten_1 = Flatten()(gru)
        dp1 = Dropout(0.3)(flatten_1)
        dense1 = Dense(y.shape[1]*y.shape[2],activation='relu')(dp1)

        out = Reshape(y.shape[1:], name='predictions')(dense1)
        # dp = Dropout(0.3)(flatten_1)
        # out = Dense(1, activation='linear')(dp)

        callbacks = [ModelCheckpoint(filepath=model_path, monitor="val_mean_squared_error", save_best_only=True)]  # TODO save best model base on validation test
        model = Model(inputs=[main_input], outputs=out)

        model.compile(loss='mean_squared_error',metrics=[metrics.mae, metrics.mse], optimizer='adam')
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=conf_seq['test_size'])
        history = model.fit(X_train, y_train, validation_data=(X_test,y_test),  epochs=conf_seq['epochs'],
                            verbose=2, batch_size=conf_seq['batch_size'], callbacks=callbacks)

        # Remove model
        os.remove(model_path)

        return model, history

class Xrk_Grid():
    """
    Train Keras model on multiple dimensions
    """

    def __init__(self, xrk_seq_model, dim_x_grid_models, dim_y_grid_models, windows_size_x):
        self.xrk_seq_model = xrk_seq_model
        self.dim_x_grid_models = dim_x_grid_models
        self.dim_y_grid_models = dim_y_grid_models
        self.windows_size_x = windows_size_x

    def _get_idxs_windows(self, X, window_size, window_dims):
        """
        Method to retrieve the indices of fixed sized windows (N-D cube)
        Boundary condition: remove outside values
        """
        idxs_l = [np.arange(len(X[coord])) for coord in window_dims] # list of arrays containing the indices of each coord in the window dim
        coord_l = [X[coord] for coord in window_dims] # list of the actual coord values
        grid_idxs = np.meshgrid(*tuple(idxs_l))  # grid of coord indexes [[0,1,2...],[0,1,2...]
        grid_coords = np.meshgrid(*tuple(coord_l))   # grid of coord values [[14.5,12.1,....],[1.3,3.5,...]]
        idxs_list = []
        wdw_centers = []
        grid_idxs = [g.T for g in grid_idxs] #what a beauty!
        grid_coords = [g.T for g in grid_coords]

        for i,j in zip(np.nditer(grid_idxs),np.nditer(grid_coords)):
            idx = []
            wdw_coords = {}
            for idim, x in enumerate(list(i)):
                idx.append(self._window_idxs(x, grid_idxs, idim, window_size))
                wdw_coords[window_dims[idim]] = j[idim].tolist()

            idxs_list.append(idx)
            wdw_centers.append(wdw_coords)
        dic_wdw = dict([(tuple(wdw.values()),idx) for wdw, idx in zip(wdw_centers,idxs_list)])

        return dic_wdw

    def _window_idxs(self,x,grid,idim, window_size):
        grid_shape = np.array(grid).shape
        idxs = np.arange(x-window_size,x+window_size)
        idxs = idxs[idxs>=0]
        idxs = idxs[idxs<=(grid_shape[idim+1]-1)]
        return idxs.tolist()

    def save(self, xrk_dir_path):

        file = open(xrk_dir_path, 'wb')
        pickle.dump(self, file)  # save current object

    def fit(self, ds_x, ds_y):

        ds_y = ds_y.stack({'model_id': self.dim_y_grid_models})
        ds_y = ds_y.dropna('model_id')
        dic_wdw = self._get_idxs_windows(ds_x, window_size=self.windows_size_x, window_dims=self.dim_x_grid_models)

        self.dic_wdw = dic_wdw
        self.model_idx = list(ds_y.model_id.values)
        self.model_idx_coords = ds_y.coords['model_id']

        xrk_seq_models = {}
        for model_id in self.model_idx:
            xrk_seq_model_id = copy.deepcopy(self.xrk_seq_model) # Create a new instance with a new pointer

            X = ds_x.isel( dict([(dim,idxs)  for dim, idxs  in zip(self.dim_x_grid_models, dic_wdw[model_id])]) )
            xrk_seq_model_fitted  = xrk_seq_model_id.fit(X, ds_y.sel(model_id=model_id))
            xrk_seq_models[str(model_id)] = xrk_seq_model_fitted

        self.xrk_seq_models = xrk_seq_models # Save fitted model in dictionary - It could be save in a xarray.
        return self


    def predict(self, ds_x):

        # ds_x = ds_x.stack({'model_id': self.dim_x_grid_models})

        ds_y_preds = []
        for model_id in self.model_idx:
            xrk_seq_model = self.xrk_seq_models[str(model_id)]
            X = ds_x.isel( dict([(dim,idxs)  for dim, idxs  in zip(self.dim_x_grid_models, self.dic_wdw[model_id])]) )

            ds_y_pred = xrk_seq_model.predict(X)
            ds_y_preds.append(ds_y_pred)

        ds_y_preds = xr.concat(ds_y_preds, dim='model_id')
        ds_y_preds = ds_y_preds.assign_coords(model_id =self.model_idx_coords)
        ds_y_preds = ds_y_preds.unstack('model_id')
        return ds_y_preds

if __name__ == '__main__':

    # Minimal example
    # Read data
    nc_file_path = "/home/thomas/database_outdropbox/sib2/out_nc/sib2_ribdata1_2048.nc"
    #
    # nc_file_path = "/home/thomas/database_outdropbox/sib2/ds_sib2_springs.nc"
    ds = xr.open_dataset(nc_file_path)


    ds_x = ds[['Evpt']] # Temperature

    ds_x = ds_x.to_array() # Transform to Dataarray
    ds_x = ds_x.isel(lat=slice(15,17), lon=slice(15,17))
    ds_x =ds_x.drop('variable')

    ds_y = ds[['Evpt']].to_array() # Productivity
    ds_y = ds_y.isel(lat=slice(15, 17), lon=slice(15, 17))
    ds_y = ds_y.drop('variable')

    # Sequence
    idx_seq_x =[-3,-2,-1] # Predictors index sequence
    idx_seq_y =[0,1,2]# Response index sequence

    # #################
    # # Simple unit model
    # #################
    # # XrKeras Model
    # xrk_seq_model = Xrk_Seq_Model(common_sample_dim='time', idx_seq_x= idx_seq_x, idx_seq_y= idx_seq_y)
    # xrk_seq_model.fit(ds_x, ds_y)
    #
    # # Save Xrk model
    # cwd = os.getcwd()
    # xrk_seq_model.save(cwd + 'xrk.model')
    #
    # # load existing xrk model
    # xrk_oper = load_xrk(cwd + 'xrk.model')
    #
    # # Predict
    # ds_y_pred = xrk_oper.predict(ds_x.isel(time=idx_seq_x)) # Note: Index must be a list


    #################
    # Xrk model Grid
    #################

    ds_x = ds_x.dropna(dim='lat', how='all')
    ds_x = ds_x.dropna(dim='lon', how='all')
    ds_y = ds_y.dropna(dim='lat', how='all')
    ds_y = ds_y.dropna(dim='lon', how='all')

    dim_y_grid_models = ['lat','lon']
    dim_x_grid_models = ['lat','lon']
    window_size_x = 3

    # create instance of unit xrk model
    xrk_seq_model = Xrk_Seq_Model(common_sample_dim='time', idx_seq_x= idx_seq_x, idx_seq_y= idx_seq_y)

    # Apply xrk unit to grid
    xrk_grid = Xrk_Grid(xrk_seq_model, dim_x_grid_models , dim_y_grid_models, window_size_x)

    # Fit xrk grid
    xrk_grid.fit(ds_x, ds_y)

    # Save
    cwd = os.getcwd()
    xrk_grid.save(cwd + 'xrk_grid.model')

    # load existing xrk model
    xrk_grid_oper = load_xrk(cwd + 'xrk_grid.model')

    # Predict
    ds_y = xrk_grid.predict(ds_x.isel(time=idx_seq_x))

    print('done')

