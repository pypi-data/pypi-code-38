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
from ketos.data_handling.data_handling import check_data_sanity, to1hot


class BatchGenerator():
    """ Creates batches to be fed to a model

        Instances of this class are python generators. They will load one batch at 
        a time from a HDF5 database, which is particularly useful when working with 
        larger than memory datasets. Yield (X,Y) or (ids,X,Y) if 'return_batch_ids' 
        is True. X is a batch of data as a np.array of shape (batch_size,mx,nx) where 
        mx,nx are the shape of on instance of X in the database. Similarly, Y is an 
        np.array of shape[0]=batch_size with the corresponding labels.

        It is also possible to load the entire data set into memory and provide it 
        to the BatchGenerator via the arguments x and y. This can be convenient when 
        working with smaller data sets.

        Args:
            batch_size: int
                The number of instances in each batch. The last batch of an epoch might 
                have fewer examples, depending on the number of instances in the hdf5_table.
            hdf5_table: pytables table (instance of table.Table()) 
                The HDF5 table containing the data
            x: numpy array
                Array containing the data images.
            y: numpy array
                Array containing the data labels.
            indices: list of ints
                Indices of those instances that will retrieved from the HDF5 table by the 
                BatchGenerator. By default all instances are retrieved.
            instance_function: function
                A function to be applied to the batch, transforming the instances. Must accept 
                'X' and 'Y' and, after processing, also return  'X' and 'Y' in a tuple.
            x_field: str
                The name of the column containing the X data in the hdf5_table
            y_field: str
                The name of the column containing the Y labels in the hdf5_table
            shuffle: bool
                If True, instances are selected randomly (without replacement). If False, 
                instances are selected in the order the appear in the database
            refresh_on_epoch: bool
                If True, and shuffle is also True, resampling is performed at the end of 
                each epoch resulting in different batches for every epoch. If False, the 
                same batches are used in all epochs.
                Has no effect if shuffle is False.
            return_batch_ids: bool
                If False, each batch will consist of X and Y. If True, the instance indices 
                (as they are in the hdf5_table) will be included ((ids, X, Y)).

        Attr:
            data: pytables table (instance of table.Table()) 
                The HDF5 table containing the data
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
            from_memory: bool
                True if the data are loaded from memory rather than an HDF5 table.

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
    def __init__(self, batch_size, hdf5_table=None, x=None, y=None, indices=None, instance_function=None, x_field='data', y_field='boxes',\
                    shuffle=False, refresh_on_epoch_end=False, return_batch_ids=False):

        self.from_memory = x is not None and y is not None

        if self.from_memory:
            check_data_sanity(x, y)
            self.x = x
            self.y = y

            if indices is None:
                self.indices = np.arange(len(self.x), dtype=int) 
            else:
                self.indices = indices

            self.n_instances = len(self.indices)
        else:
            assert hdf5_table is not None, 'hdf5_table or x,y must be specified'
            self.data = hdf5_table
            self.x_field = x_field
            self.y_field = y_field
            if indices is None:
                self.n_instances = self.data.nrows
                self.indices = np.arange(self.n_instances)
            else:
                self.n_instances = len(indices)
                self.indices = indices

        self.batch_size = batch_size
        self.shuffle = shuffle
        self.instance_function = instance_function
        self.batch_count = 0
        self.refresh_on_epoch_end = refresh_on_epoch_end
        self.return_batch_ids = return_batch_ids

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
        n_complete_batches = int(self.n_instances // self.batch_size) # number of batches that can accomodate self.batch_size intances
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

        if self.from_memory:
            X = np.take(self.x, batch_ids, axis=0)
            Y = np.take(self.y, batch_ids, axis=0)
        else:
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
    """ Creates batch generators to be used in active learning.

        The learning process is divided into sessions. During each 
        session the neural network considers only a part of the 
        entire training data set. Typically, the network is exposed 
        to a mixture of new examples and examples from the previous 
        session, which it failed to learn (or learned, but with low 
        confidence).

        Args:
            session_size: int
                The number of instances in each learning session.
            batch_size: int
                The number of instances in each batch. The last batch of 
                an epoch might have fewer examples, depending on the number 
                of instances in the hdf5_table.
            num_labels: int
                Number of labels
            hdf5_table: pytables table (instance of table.Table()) 
                The HDF5 table containing the data
            x: numpy array
                Array containing the data images.
            y: numpy array
                Array containing the data labels.
            instance_function: function
                A function to be applied to the batch, transforming the instances. 
                Must accept 'X' and 'Y' and, after processing, also return  'X' and 
                'Y' in a tuple.
            x_field: str
                The name of the column containing the X data in the hdf5_table
            y_field: str
                The name of the column containing the Y labels in the hdf5_table
            shuffle: bool
                If True, instances are selected randomly (without replacement). If 
                False, instances are selected in the order the appear in the database
            refresh: bool
                If True, and shuffle is also True, resampling is performed at the end of 
                each epoch resulting in different batches for every epoch. If False, the 
                same batches are used in all epochs. Has no effect if shuffle is False.
            return_indices: bool
                If False, each batch will consist of X and Y. If True, the instance indices 
                (as they are in the hdf5_table) will be included ((ids, X, Y)).
            max_keep: float
                Maximum number of examples that are kept from the previous session, expressed 
                as a fraction of the session size
            conf_cut: float
                Correct predictions with confidence below conf_cut will be kept for next session 
                (all wrong predictions are also kept)
            seed: int
                Seed for random number generator
            parse_labels: bool
                Parse labels field. Only applicable if y_field is 'labels' and instance_function is None.
            convert_to_one_hot: bool
                Convert labels to 1-hot representation. Only applicable if instance_function is None.
            val_frac: float between 0 and 1
                Fraction of data that will be used for validation
            val_size: int
                Number of samples that will be used for validation. 
                None by default. Overwrites val_frac.
            suppress_warnings: bool
                Do not show warnings

        Attr:
            data: pytables table (instance of table.Table()) 
                The HDF5 table containing the data
            data_size: int
                The total number of instances in the data set
            indices: numpy array
                Indices of all instances in the data set
            session_indices: numpy array  
                Indices of all instances in the current session              
            poor_indices: numpy array
                Indices of those instances in the previous session that were wronly 
                predicted, or correctly predicted but with low confidence
            from_memory: bool
                True if the data are loaded from memory rather than an HDF5 table.
            suppress_warnings: bool
                Do not show warnings
            val_frac: float between 0 and 1
                Fraction of data that will be used for validation

        Example:
            >>> from tables import open_file
            >>> from ketos.data_handling.database_interface import open_table
            >>> h5 = open_file("ketos/tests/assets/15x_same_spec.h5", 'r') # open the database file 
            >>> table = open_table(h5, "/train/species1") # access the table of interest
            >>> # create an active learning module with session_size of 6, batch_size of 3 and max_keep of 0.4
            >>> active_learning = ActiveLearningBatchGenerator(session_size=6, batch_size=3, table=table, max_keep=0.4, seed=1, return_indices=True) 
            >>> # run 2 sessions, and 3 epochs for each session
            >>> num_sessions = 2
            >>> num_epochs = 3  
            >>> for s in range(num_sessions): # loop over sessions
            ...    generator = next(active_learning)
            ...    for e in range(num_epochs): # loop over epochs
            ...       for b in range(generator.n_batches): # loop over batches
            ...          idx, X, Y = next(generator)
            ...          # pretend that neural network makes predictions [1 1 0]
            ...          active_learning.update_performance(idx, predictions=[1, 1, 0])  
            ...          print("session:{0}, epoch:{1}, batch:{2} | instance: {3}, X shape: {4}, Y length: {5}".format(s, e, b, idx, X.shape, len(Y)))
            session:0, epoch:0, batch:0 | instance: [0, 1, 2], X shape: (3, 2413, 201), Y length: 3
            session:0, epoch:0, batch:1 | instance: [3, 4, 5], X shape: (3, 2413, 201), Y length: 3
            session:0, epoch:1, batch:0 | instance: [0, 1, 2], X shape: (3, 2413, 201), Y length: 3
            session:0, epoch:1, batch:1 | instance: [3, 4, 5], X shape: (3, 2413, 201), Y length: 3
            session:0, epoch:2, batch:0 | instance: [0, 1, 2], X shape: (3, 2413, 201), Y length: 3
            session:0, epoch:2, batch:1 | instance: [3, 4, 5], X shape: (3, 2413, 201), Y length: 3
            session:1, epoch:0, batch:0 | instance: [5, 8, 7], X shape: (3, 2413, 201), Y length: 3
            session:1, epoch:0, batch:1 | instance: [6, 2, 9], X shape: (3, 2413, 201), Y length: 3
            session:1, epoch:1, batch:0 | instance: [5, 8, 7], X shape: (3, 2413, 201), Y length: 3
            session:1, epoch:1, batch:1 | instance: [6, 2, 9], X shape: (3, 2413, 201), Y length: 3
            session:1, epoch:2, batch:0 | instance: [5, 8, 7], X shape: (3, 2413, 201), Y length: 3
            session:1, epoch:2, batch:1 | instance: [6, 2, 9], X shape: (3, 2413, 201), Y length: 3
            >>> h5.close()
    """
    def __init__(self, session_size, batch_size, num_labels=2, table=None, x=None, y=None, shuffle=False, refresh=False, return_indices=False,\
                    max_keep=0, conf_cut=0, seed=None, instance_function=None, x_field='data', y_field='labels', parse_labels=True,\
                    convert_to_one_hot=False, val_frac=0.0, val_size=None, suppress_warnings=False):

        self.from_memory = x is not None and y is not None

        if self.from_memory:
            check_data_sanity(x, y)
            self.x = x
            self.y = y
            self.data_size = len(x)
            self.data = None
            self.x_field = None
            self.y_field = None
        else:
            assert table is not None, 'table or x,y must be specified'
            self.data = table
            self.data_size = self.data.nrows
            self.x_field = x_field
            self.y_field = y_field
            self.x = None
            self.y = None

        self.session_size = session_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.refresh = refresh
        self.return_indices = return_indices
        self.max_keep = max_keep
        self.conf_cut = conf_cut
        self.seed = seed
        self.instance_function = instance_function
        self.num_labels = num_labels
        self.convert_to_one_hot = convert_to_one_hot
        self.parse_labels = parse_labels
        self.instance_function = instance_function
        self.suppress_warnings = suppress_warnings

        if seed is not None:
            np.random.seed(seed) 

        self.poor_indices = np.array([], dtype=int)
        self.indices = np.arange(self.data_size, dtype=int) 

        # reserve for validation
        self.val_indices = []
        if val_size is not None:
            val_frac = min(1.0, val_size / self.data_size)

        if val_frac > 0:
            num_val = max(1, int(val_frac * self.data_size))
            self.val_indices = np.random.choice(self.indices, num_val, replace=False)
            self.indices = np.delete(self.indices, self.val_indices)

        self.indices = self.__refresh_indices__()

        self.counter = 0


    def __instance_function__(self):
        """Creates the instance function for the batch generator

            Returns:
                func: function
                    The instance function               
        
        """
        if self.instance_function:
            self.__f1__ = self.instance_function
            self.__f2__ = self.__identity__
            self.__f3__ = self.__identity__
        else:
            self.__f1__ = self.__identity__
            if self.parse_labels and self.y_field == 'labels':
                self.__f2__ = self.__parse_labels__
            else:
                self.__f2__ = self.__identity__
            if self.convert_to_one_hot:
                self.__f3__ = self.__convert_to_one_hot__
            else:
                self.__f3__ = self.__identity__

        def func(X,Y):
            X,Y = self.__f1__(X,Y)
            X,Y = self.__f2__(X,Y)
            X,Y = self.__f3__(X,Y)
            return X,Y

        return func

    def __refresh_indices__(self):
        """Updates the indices used to divide the data into sessions

            The order of the indices determines which instances will be placed in each batch.
            If the self.shuffle is True, the indices are randomly reorganized, resulting in batches with randomly selected instances.

            Returns
                indices: list of ints
                    The list of instance indices
        """
        indices = self.indices

        if self.shuffle:
            np.random.shuffle(indices)

        return indices

    def __get_session_indices__(self):
        """Selects the indices for the next session

            Returns:
                list_of_indices: list of ints
                    Indices for the next session                
        
        """
        # number of instances from previous session with poor performace 
        num_poor = len(np.unique(self.poor_indices))

        # number of examples kept from previous session
        num_keep = int(min(num_poor, self.max_keep * self.session_size))

        # number of new examples
        num_new = self.session_size - num_keep

        # select new examples
        i1 = self.counter
        i2 = min(i1 + num_new, self.data_size)
        new_session = self.indices[i1:i2]
        self.counter = i2

        # if necessary, go back to beginning to complete batch
        dn = num_new - new_session.shape[0]
        if dn > 0:
            new_session = np.concatenate((new_session, self.indices[:dn]))
            self.counter = dn

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
            Return: BatchGenerator
                Batch generator for the next session.
        """
        # get indices for new session
        session_indices = self.__get_session_indices__()

        # refresh poor_indices array
        self.poor_indices = np.array([], dtype=int)

        # create batch generator
        generator = BatchGenerator(hdf5_table=self.data, x=self.x, y=self.y, batch_size=self.batch_size, indices=session_indices,\
                    instance_function=self.__instance_function__(), x_field=self.x_field, y_field=self.y_field,\
                    shuffle=self.shuffle, refresh_on_epoch_end=self.refresh, return_batch_ids=self.return_indices)

        return generator

    def get_validation_data(self):
        """ Get validation data.

                Returns: tuple
                    Instances (X,Y) or, if 'return_indices" is True, instances accompanied by their indices (ids, X, Y) 
        """
        if len(self.val_indices) == 0:
            X, Y = [], []
    
        else:
            if self.from_memory:
                X = np.take(self.x, self.val_indices, axis=0)
                Y = np.take(self.y, self.val_indices, axis=0)
            else:
                X = self.data[self.val_indices][self.x_field]
                Y = self.data[self.val_indices][self.y_field]

            X, Y = self.__instance_function__()(X, Y)

        if self.return_indices:
            return (self.val_indices, X, Y)
        else:
            return (X, Y)        

    def update_performance(self, indices, predictions, confidences=None):
        """Inform the generator about how well the neural network performed on a set of examples.

            Args:
                indices: numpy.array
                    Indices of the examples that the predictions and confidences refer to
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

        if self.from_memory:
            Y = np.take(self.y, indices)            
        else:
            Y = self.data[indices][self.y_field]

        if self.parse_labels and self.y_field == 'labels':
            _, Y = self.__parse_labels__(None, Y)

        poor = np.logical_or(predictions != Y, confidences < self.conf_cut)
        poor = np.argwhere(poor == True)
        poor = np.squeeze(poor)
        if np.ndim(poor) == 0:
            poor = np.array([poor], dtype=int)

        self.poor_indices = np.concatenate((self.poor_indices, indices[poor]))

    def __identity__(self,X,Y):
        """Identity function.
        """
        return X,Y 

    def __parse_labels__(self,X,Y):
        """Parse labels extracted from hdf5 database.
        """
        YY = list()
        for _y in Y:
            _y = parse_labels(_y)
            if len(_y) >= 1:# if there are one or more labels, we use the first label
                if len(_y) > 1:
                    if not self.suppress_warnings:
                        print('Warning: ActiveLearningBatchGenerator encountered instance with more than one label. Using the first label only.')

                _y = _y[0]
            elif len(_y) == 0:# if there are no labels, we use the label 0
                _y = 0

            YY.append(_y)

        if len(YY) == 1:
            YY = YY[0]        

        return X,YY

    def __convert_to_one_hot__(self,X,Y):
        """Convert labels to 1-hot encoding
        """
        Y = to1hot(Y, self.num_labels)
        return X,Y

