# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" Data feeding module within the ketos library

    This module provides utilities to load data and feed it to models.

    Contents:
        BatchGenerator class
        TrainiDataProvider class
"""

import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from ketos.data_handling.database_interface import parse_labels


class BatchGenerator():
    """ Creates batches to be fed to a model

        Instances of this class are python generators. They will load one batch at a time from a HDF5 database, which is particularly useful when working with larger than memory datasets.
        Yield (X,Y) or (ids,X,Y) if 'return_batch_ids' is True. X is a batch of data as a np.array of shape (batch_size,mx,nx) where mx,nx are the shape of on instance of X in the database. Similarly, Y is an np.array of shape[0]=batch_size with the corresponding labels.

        Args:
            hdf5_table: pytables table (instance of table.Table()) 
                The HDF5 table containing the data
            batch_size: int
                The number of instances in each batch. The last batch of an epoch might have fewer examples, depending on the number of instances in the hdf5_table.
            instance_function: function
                A function to be applied to the batch, transforming the instances. Must accept 'X' and 'Y' and, after processing, also return  'X' and 'Y' in a tuple.
            x_field: str
                The name of the column containing the X data in the hdf5_table
            y_field: str
                The name of the column containing the Y labels in the hdf5_table
            shuffle: bool
                If True, instances are selected randomly (without replacement). If False, instances are selected in the order the appear in the database
            refresh_on_epoch: bool
                If True, and shuffle is also True, resampling is performed at the end of each epoch resulting in different batches for every epoch. If False, the same batches are used in all epochs.
                Has no effect if shuffle is False.
            return_batch_ids: bool
                If False, each batch will consist of X and Y. If True, the instance indices (as they are in the hdf5_table) will be included ((ids, X, Y)).

            Attr:
                n_instances: int
                    The number of intances (rows) in the hdf5_table
                n_batches: int
                    The number of batches of size 'batch_size' for each epoch
                entry_indices:list of ints
                    A list of all intance indices, in the order used to generate batches for this epoch
                batch_indices: list of tuples (int,int)
                    A list of (start,end) indices for each batch. These indices refer to the 'entry_indices' attribute.
                batch_count: int
                    The current batch within the epoch
        
            Examples:
                >>> from tables import open_file
                >>> from ketos.data_handling.database_interface import open_table
                >>> h5 = open_file("ketos/tests/assets/15x_same_spec.h5", 'r') # create the database handle  
                >>> train_data = open_table(h5, "/train/species1")
                >>> train_generator = BatchGenerator(hdf5_table=train_data, batch_size=3, return_batch_ids=True) #create a batch generator 
                >>> #Run 2 epochs. 
                >>> n_epochs = 2    
                >>> for e in range(n_epochs):
                ...    for batch_num in range(train_generator.n_batches):
                ...        ids, batch_X, batch_Y = next(train_generator)   
                ...        print("epoch:{0}, batch {1} | instance ids:{2}, X batch shape: {3}, Y batch shape: {4}".format(e, batch_num, ids, batch_X.shape, batch_Y.shape))
                epoch:0, batch 0 | instance ids:[0, 1, 2], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:0, batch 1 | instance ids:[3, 4, 5], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:0, batch 2 | instance ids:[6, 7, 8], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:0, batch 3 | instance ids:[9, 10, 11], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:0, batch 4 | instance ids:[12, 13, 14], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:1, batch 0 | instance ids:[0, 1, 2], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:1, batch 1 | instance ids:[3, 4, 5], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:1, batch 2 | instance ids:[6, 7, 8], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:1, batch 3 | instance ids:[9, 10, 11], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                epoch:1, batch 4 | instance ids:[12, 13, 14], X batch shape: (3, 2413, 201), Y batch shape: (3,)
                >>> #Applying a custom function to the batch
                >>> #Takes the mean of each instance in X; leaves Y untouched
                >>> def apply_to_batch(X,Y):
                ...    X = np.mean(X, axis=(1,2)) #since X is a 3d array
                ...    return (X,Y)
                >>> train_generator = BatchGenerator(hdf5_table=train_data, batch_size=3, return_batch_ids=False, instance_function=apply_to_batch) 
                >>> X,Y = next(train_generator)                
                >>> #Now each X instance is one single number, instead of a (2413,201) matrix
                >>> #A batch of size 3 is an array of the 3 means
                >>> X.shape
                (3,)
                >>> #Here is how one X instance looks like
                >>> X[0]
                7694.1147
                >>> #Y is the same as before 
                >>> Y.shape
                (3,)
                >>> h5.close()

    """
    def __init__(self, hdf5_table, batch_size, indices=None, instance_function=None, x_field='data', y_field='boxes',\
                    shuffle=False, refresh_on_epoch_end=False, return_batch_ids=False):
        self.data = hdf5_table
        self.batch_size = batch_size
        self.x_field = x_field
        self.y_field = y_field
        self.shuffle = shuffle
        self.instance_function = instance_function
        self.batch_count = 0
        self.refresh_on_epoch_end = refresh_on_epoch_end
        self.return_batch_ids = return_batch_ids
        self.indices = indices

        if self.indices is None:
            self.n_instances = self.data.nrows
        else:
            self.n_instances = len(self.indices)

        self.n_batches = int(np.ceil(self.n_instances / self.batch_size))

        self.entry_indices = self.__update_indices__()

        self.batch_indices = self.__get_batch_indices__()

    
    def __update_indices__(self):
        """Updates the indices used to divide the instances into batches.

            A list of indices is kept in the self.entry_indices attribute.
            The order of the indices determines which instances will be placed in each batch.
            If the self.shuffle is True, the indices are randomly reorganized, resulting in batches with randomly selected instances.

            Returns
                indices: list of ints
                    The list of instance indices
        """
        if self.indices is None:
            indices = np.arange(self.n_instances)        
        else:
            indices = self.indices

        if self.shuffle:
            np.random.shuffle(indices)

        return indices

    def __get_batch_indices__(self):
        """Selects the indices for each batch

            Divides the instances into batchs of self.batch_size, based on the list generated by __update_indices__()

            Returns:
                list_of_indices: list of tuples
                    A list of tuple, each containing two integer values: the start and end of the batch. These positions refer to the list stored in self.entry_indices.                
        
        """
        ids = self.entry_indices
        n_complete_batches = int( self.n_instances // self.batch_size) # number of batches that can accomodate self.batch_size intances
        last_batch_size = self.n_instances % n_complete_batches
    
        list_of_indices = [list(ids[(i*self.batch_size):(i*self.batch_size)+self.batch_size]) for i in range(self.n_batches)]
        if last_batch_size > 0:
            last_batch_ids = list(ids[-last_batch_size:])
            list_of_indices.append(last_batch_ids)

        return list_of_indices

    def __iter__(self):
        return self

    def __next__(self):
        """         
            Return: tuple
            A batch of instances (X,Y) or, if 'returns_batch_ids" is True, a batch of instances accompanied by their indices (ids, X, Y) 
        """

        batch_ids = self.batch_indices[self.batch_count]
        X = self.data[batch_ids][self.x_field]
        Y = self.data[batch_ids][self.y_field]

        self.batch_count += 1
        if self.batch_count > (self.n_batches - 1):
            self.batch_count = 0
            if self.refresh_on_epoch_end:
                self.entry_indices = self.__update_indices__()
                self.batch_indices = self.__get_batch_indices__()

        if self.instance_function is not None:
            X,Y = self.instance_function(X,Y)

        if self.return_batch_ids:
            return (batch_ids,X,Y)
        else:
            return (X, Y)

class ActiveLearningBatchGenerator():
    """Creates batches of data to be used in active learning.


        Instances of this class are used in conjuntion with a neural network, keeping track of the models confidence when precessing each training input.

        Note: Expected to be used only with binary classification models

        Warnings: This class will be deprecate in future releases. It's book keeping functionalities will either be incorporated in the the BatchGenerator class or a simpler class that delegates the batch creation process to BatchGenerator will be available.


        Args:
            x: pandas DataFrame
                Training data
            y: pandas DataFrame
                Labels for training data
            randomize: bool
                Randomize order of training data
            num_samples: int
                Number of samples that will be returned by the generator at each iteration
            max_keep: float
                Maximum number of samples that are kept from the previous iteration, expressed as a fraction of num_samples
            conf_cut: float
                Correct predictions with confidence below conf_cut will be kept for next iteration (all wrong predictions are also kept)
            seed: int
                Seed for random number generator
            equal_rep: bool
                Ensure that new samples drawn at each iteration have equal representation of 0s and 1s
            verbosity: bool
                Print information and warnings

        Example:
            >>> import numpy as np
            >>> from ketos.neural_networks.neural_networks import class_confidences, predictions
            >>> x = np.array([1, 2, 3, 4, 5, 6]) # input data
            >>> y = np.array([0, 1, 0, 1, 0, 1]) # labels
            >>> w = np.array([[0.8, 0.2], [0.1, 0.9], [0.96, 0.04], [0.49, 0.51], [0.45, 0.55], [0.60, 0.40]]) # class weights computed by NN
                        
            >>> p = predictions(w)
            >>> c = class_confidences(w)

            >>> sampler = ActiveLearningBatchGenerator(x=x, y=y, randomize=False, max_keep=0.5, conf_cut=0.5, seed=1, equal_rep=False, verbosity=1)
            positives:  3
            negatives:  3

            >>> x1, y1, _ = sampler.get_samples(num_samples=2) #0,1
            >>> np.all(x1 == x[0:2])    
            True
            
            >>> sampler.update_prediction_confidence(pred=p[:2], conf=c[:2])
            >>> x1, y1, _ = sampler.get_samples(num_samples=2) #2,3
            >>> np.all(x1 == x[2:4])    
            True
    """
    def __init__(self, x, y, randomize=False, num_samples=100, max_keep=0, conf_cut=0, seed=None, equal_rep=True, verbosity=0):

        if type(x) is not np.ndarray:
            x = np.array(x)

        N = x.shape[0]
        self.x = x
        self.df = pd.DataFrame({'y':y, 'pred':y, 'conf':np.ones(N), 'prev':np.zeros(N, dtype=bool)})
        self.randomize = randomize
        self.num_samples = num_samples
        self.max_keep = max_keep
        self.conf_cut = conf_cut
        self.it = 0
        self.current_pos = 0
        self.equal_rep = equal_rep
        self.seed = seed
        if seed is not None:
            np.random.seed(seed) 

        if verbosity >= 1:
            print('positives: ',  len(self.df[self.df.y == 1]))
            print('negatives: ',  len(self.df[self.df.y == 0]))

        self.posfrac = float(len(self.df[self.df.y == 1])) / float(len(self.df))

    def get_samples(self, num_samples=None, max_keep=None, conf_cut=None):
        """ Creates a batch of data with a mix of new instances and previously used instances which resulted in low confidence or wrong predictions.

        Args:
            num_samples:int
                The number of samples to be drawn 
            max_keep:int
                The maximum number of inputs with low confidence to keep
            conf_cut:float
                The confidence threshold. Inputs with that had confidence values higher than this will not be kept included. 
        Returns:tuple (x, y,keep_frac)
            x: numpy.array 
                The batch of inputs
            y: numpy.array
                The batch of labels
            keep_frac: float
                The fraction coming from low confidence samples
        """

        # use default value if none provided
        if num_samples is None:
            num_samples = self.num_samples
        if max_keep is None:
            max_keep = self.max_keep
        if conf_cut is None:
            conf_cut = self.conf_cut

        x, y = None, None

        # get poorly performing samples from previous iteration
        num_poor_max = int(np.ceil(num_samples * max_keep))
        idx_poor = self._get_poor(num=num_poor_max, conf_cut=conf_cut)
        num_poor = len(idx_poor)

        # get new samples
        idx = self._get_new(num_samples=num_samples - num_poor, randomize=self.randomize, equal_rep=self.equal_rep)
        if num_poor > 0:
            idx = idx.union(idx_poor)

        # combine poorly performing and new samples
        df = self.df.loc[idx]
        x = self.x[idx]
        y = df.y.values

        # internal book keeping
        self.df.prev = False
        self.df.loc[idx,'prev'] = True

        keep_frac = num_poor / len(idx)
        return x, y, keep_frac

    def update_prediction_confidence(self, pred, conf):
        """Updates the internal dataframe with the predictions and confidences from the last batch.

            Args:
                pred: numpy.array
                    Array containing the predictions on the last batch.
                    Created with ketos.neural_networks.neural_networks.predictions.
                conf: numpy.array
                    Array containing the confidences for the predictions on the last batch.
                    Created with ketos.neural_networks.neural_networks.class_confidences.    
        """
        assert len(pred) == len(conf),'length of prediction and confidence arrays do not match'
        idx = self.df[self.df.prev == True].index
        assert len(pred) == len(idx),'length of prediction and confidence arrays do not match the number of samples drawn in the last iteration'
        self.df.loc[idx,'pred'] = pred
        self.df.loc[idx,'conf'] = conf

    def _get_poor(self, num, conf_cut):
        """ Retrieves the instances from the previous batch for which predictions had low confidence or were wrong.

            Args:
                num:int
                    The number of instances to retrieve
                conf_cut:float
                    The confidence threshold. Only instances with confidence values below this or wrong predictions are included.

            Returns:
                idx: pandas.Index or empty list
                    The index of the selected low confidence or wrong prediction instances. Returns an empty list if none of the instances
                    in the previous batch had low confidences or wrong predictions, or if none of the instances have been used in the previous batch.
        """

        df_prev = self.df[self.df.prev == True]
        N = df_prev.shape[0]
        if N == 0:
            return list()
        df_poor = df_prev[(df_prev.pred != df_prev.y) | (df_prev.conf < self.conf_cut)]
        if df_poor.shape[0] == 0:
            return list()
        M = min(df_poor.shape[0], num)
        idx = np.random.choice(df_poor.index, M, replace=False)
        idx = pd.Index(idx)
        return idx

    def _get_new(self, num_samples, randomize, equal_rep):
        """ Retrieves a batch of new instances not used in the previous iteration.

            Args:
                num_samples: int
                    The number of samples to be drawn
                randomize: bool
                    If True, retrives samples in a random order. Otherwise, retrieves intances sequentially
                equal_rep:bool
                    If True, creates a batch of approximately the same number of positive and negative examples.

            Returns:
                idx: pandas.Index
                    The index of the selected new instances.
        """

        num_0 = int(num_samples / 2)
        num_1 = num_samples - num_0

        if self.randomize:
            df_new = self.df[self.df.prev == False]
            if self.equal_rep:
                df_new_0 = df_new[df_new.y == 0]
                df_new_1 = df_new[df_new.y == 1]
                idx_0 = np.random.choice(df_new_0.index, num_0, replace=False)
                idx_1 = np.random.choice(df_new_1.index, num_1, replace=False)
                idx = np.concatenate((idx_0, idx_1), axis=0)
                idx = shuffle(idx, random_state=self.seed)
            else:
                idx = np.random.choice(df_new.index, num_samples, replace=False)

            idx = pd.Index(idx)

        else:
            start = self.current_pos
            stop = min(start + num_samples, self.df.shape[0])
            idx = self.df.index[start:stop]
            dn = num_samples - len(idx)
            dn_0 = 0
            dn_1 = 0
            if self.equal_rep:
                dfi = self.df.loc[idx]
                n_0 = len(dfi[dfi.y == 0])
                n_1 = len(dfi[dfi.y == 1])
                dn_0 = num_0 - n_0
                dn_1 = num_1 - n_1

            while (dn > 0) or (dn_0 > 0) or (dn_1 > 0):

                start = stop % self.df.shape[0]

                if self.equal_rep:
                    if self.posfrac < 1.:
                        dn_0_norm = int(float(dn_0) / (1. - self.posfrac))
                    else:
                        dn_0_norm = 0

                    if self.posfrac > 0.:
                        dn_1_norm = int(float(dn_1) / self.posfrac)
                    else:
                        dn_1_norm = 0

                    stop = max(dn, max(dn_0_norm, dn_1_norm))
                else:
                    stop = dn

                stop += start
                stop = min(stop, self.df.shape[0])

                idx_add = self.df.index[start:stop].values
                idx = np.concatenate((idx.values, idx_add), axis=0)
                idx = pd.Index(idx)
                dn = num_samples - len(idx)

                if self.equal_rep:
                    dfi = self.df.loc[idx]
                    n_0 = len(dfi[dfi.y == 0])
                    n_1 = len(dfi[dfi.y == 1])
                    dn_0 = num_0 - n_0
                    dn_1 = num_1 - n_1

            if self.equal_rep:
                dfi = self.df.loc[idx]
                idx_0 = dfi[dfi.y == 0].index
                idx_1 = dfi[dfi.y == 1].index
                idx_0 = np.random.choice(idx_0, num_0, replace=False)
                idx_1 = np.random.choice(idx_1, num_1, replace=False)
                idx = np.concatenate((idx_0, idx_1), axis=0)
                idx = shuffle(idx, random_state=self.seed)
                idx = pd.Index(idx)

            idx = idx.drop_duplicates()

            self.current_pos = stop

        return idx

def func_identity(X,Y):
    return X,Y 

def func_normalize_X(X,Y):
    X = (X - np.mean(X)) / np.std(X)
    return X,Y 

def func_parse_labels(X,Y):
    YY = list()
    for _y in Y:
        _y = parse_labels(_y)
        if len(_y) == 1:
            _y = _y[0]

        YY.append(_y)

    if len(YY) == 1:
        YY = YY[0]

    return X,YY


class ActiveLearningBatchGenerator2():

    def __init__(self, table, session_size, batch_size, shuffle=False, refresh=False, return_indices=False,\
                    max_keep=0, conf_cut=0, seed=None, batch_norm=False, instance_function=None, x_field='data', y_field='labels'):

        self.data = table
        self.session_size = session_size
        self.batch_size = batch_size
        self.data_size = self.data.nrows
        self.shuffle = shuffle
        self.refresh = refresh
        self.return_indices = return_indices
        self.max_keep = max_keep
        self.conf_cut = conf_cut
        self.batch_norm = batch_norm
        self.seed = seed
        self.x_field = x_field
        self.y_field = y_field
        self.instance_function = instance_function

        if seed is not None:
            np.random.seed(seed) 

        self.poor_indices = self.__refresh_poor_indices__()
        self.indices = self.__refresh_indices__()

        self.session_indices = np.array([-1], dtype=int)
 
    def __refresh_poor_indices__(self):
        return np.array([], dtype=int)

    def __refresh_indices__(self):
        """Updates the indices used to divide the instances into batches.

            A list of indices is kept in the self.entry_indices attribute.
            The order of the indices determines which instances will be placed in each batch.
            If the self.shuffle is True, the indices are randomly reorganized, resulting in batches with randomly selected instances.

            Returns
                indices: list of ints
                    The list of instance indices
        """
        indices = np.arange(self.data_size)

        if self.shuffle:
            np.random.shuffle(indices)

        return indices

    def __get_session_indices__(self):
        """Selects the indices for the next session

            Divides the instances into batchs of self.batch_size, based on the list generated by __update_indices__()

            Returns:
                list_of_indices: list of tuples
                    A list of tuple, each containing two integer values: the start and end of the batch. These positions refer to the list stored in self.entry_indices.                
        
        """
        # number of instances from previous session with poor performace 
        num_poor = len(self.poor_indices)

        # number of examples kept from previous session
        num_keep = int(min(num_poor, self.max_keep * self.session_size))

        # number of new examples
        num_new = self.session_size - num_keep

        # select new examples
        i1 = self.session_indices[-1] + 1
        i2 = min(i1 + num_new, self.data_size)
        new_session = self.indices[i1:i2]

        # if necessary, go back to beginning to complete batch
        dn = num_new - new_session.shape[0]
        if dn > 0:
            new_session = np.concatenate((new_session, self.indices[:dn]))

        # select randomly from poorly predicted examples in previous session
        if num_keep > 0:
            new_session = np.concatenate((new_session, np.random.choice(np.unique(self.poor_indices), num_keep, replace=False)))

        # refresh at end of data set
        epoch_end = (i2 == self.data_size or dn > 0)
        if self.refresh and epoch_end:
            self.indices = self.__refresh_indices__()

        # shuffle new session, if it contains examples from previous session
        if num_keep > 0:
            np.random.shuffle(new_session)

        return new_session

    def __iter__(self):
        return self

    def __next__(self):
        """         
            Return: tuple
            A batch of instances (X,Y) or, if 'returns_batch_ids" is True, a batch of instances accompanied by their indices (ids, X, Y) 
        """
        # get indices for new session
        self.session_indices = self.__get_session_indices__()

        # refresh is_poor array
        self.poor_indices = self.__refresh_poor_indices__()

        # instance function
        if self.instance_function is None:
            f1 = func_identity
        else:
            f1 = self.instance_function

        if self.batch_norm:
            f2 = func_normalize_X
        else:
            f2 = func_identity

        if self.y_field == 'labels':
            f3 = func_parse_labels
        else:
            f3 = func_identity

        def func(X,Y):
            X,Y = f1(X,Y)
            X,Y = f2(X,Y)
            X,Y = f3(X,Y)
            return X,Y

        # create batch generator
        generator = BatchGenerator(hdf5_table=self.data, batch_size=self.batch_size, indices=self.session_indices,\
                    instance_function=func, x_field=self.x_field, y_field=self.y_field,\
                    shuffle=self.shuffle, refresh_on_epoch_end=self.refresh, return_batch_ids=self.return_indices)

        return generator

    def update_performance(self, indices, predictions, confidences=None):
        """Inform the generator about how well the neural network performed on a set of examples.

            Args:
                pred: numpy.array
                    Array containing the predictions on the last batch.
                    Created with ketos.neural_networks.neural_networks.predictions.
                conf: numpy.array
                    Array containing the confidences for the predictions on the last batch.
                    Created with ketos.neural_networks.neural_networks.class_confidences.    
        """
        if confidences is None:
            confidences = np.ones(len(predictions))
            
        assert len(indices) == len(predictions), 'length of indices and predictions arrays do not match'
        assert len(predictions) == len(confidences), 'length of prediction and confidence arrays do not match'

        if type(indices) != np.ndarray:
            indices = np.array(indices, dtype=int)

        if type(predictions) != np.ndarray:
            predictions = np.array(predictions, dtype=int)

        if type(confidences) != np.ndarray:
            confidences = np.array(confidences, dtype=float)

        Y = self.data[indices][self.y_field]
        if self.y_field == 'labels':
            _, Y = func_parse_labels(None, Y)

        poor = np.logical_or(predictions != Y, confidences < self.conf_cut)
        poor = np.argwhere(poor == True)
        poor = np.squeeze(poor)
        if np.ndim(poor) == 0:
            poor = np.array([poor], dtype=int)

        self.poor_indices = np.concatenate((self.poor_indices, indices[poor]))
