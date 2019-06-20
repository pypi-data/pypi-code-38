from keras.layers import Input, Dense
from keras.models import Model, Sequential
import numpy as np
def get_AE(units):
    """ build an autoencoder with explict encoder and decorder object

    Parameters
    =========
    units : list of integers
        The number of units (neurons) in each layer as in the following order:
        [n_inputs, h1, h2, ..., middle_layer]. See examples below.
    
    Returns
    =======
    autoencoder : keras Model
        The autoencoder model, made of encoder+decoder.
    
    encoder : keras Model
        The encoder part of the autoencoder.
    
    decoder : keras model
        The decoder part of the autoencoder.
    
    Examples
    ========
    Given parameter units = [10, 5, 3], this represents an autoencoder of structure [10, 5, 3, 5, 10].
    Specifically, it has 10 inputs, 5 units in the first hidden layer, 3 units in the second
    hidden layer (the bottleneck) and 5 units in the decoder layer, and 10 units in the output
    layer (same as the number of inputs).
    """
    n_encoder_inputs = units[0]
    n_encoder_units = units[1:]
    n_decoder_inputs = units[-1]
    n_decoder_units = units[:-1][::-1]
    # build encoder
    encoder = Sequential()
    encoder.add(Dense(n_encoder_units[0], input_dim=n_encoder_inputs, activation='sigmoid'))
    for n in n_encoder_units[1:]:
        encoder.add(Dense(n, activation='sigmoid'))
    # build decoder
    decoder = Sequential()
    decoder.add(Dense(n_decoder_units[0], input_dim=n_decoder_inputs,activation='sigmoid'))
    for n in n_decoder_units[1:]:
        decoder.add(Dense(n, activation='sigmoid'))
    # build the autoencoder
    autoencoder = Sequential(encoder.layers + decoder.layers)
    return (autoencoder, encoder, decoder)

def add_noise_masking(noiseParam, data):
    """Add noise to the input data by setting a proportion of each observation to 0.
    This function adds noise as described in Vincent et al. (2008). 
    https://www.iro.umontreal.ca/~vincentp/Publications/denoising_autoencoders_tr1316.pdf
    Parameters
    ==========
    noiseParam : float, in range [0,1]
        The proportion of inputs to be set to 0 to introduce noise. Particularly,
        0 means adding no noise, 1 means setting all inputs to 0 (not useful).
    
    data : 2D matrix, each row is an observation of X
        So, data(i,:) is the i-th training example.
    
    Returns
    =======
    noisyData : 2D matrix, each row is an observation of X_tild
        Original data with noise.
    """
    noiseMask = np.ones(data.shape)
    n_featuers = data.shape[1]
    n_noised = int(n_featuers * noiseParam)
    
    # add noise by setting part of the mask to zero
    noise_vector = np.ones(n_featuers)
    noise_vector[:n_noised] = 0

    # shuffle the noise in each row
    for i in range(noiseMask.shape[0]):
        np.random.shuffle(noise_vector)
        noiseMask[i,:] = noise_vector
    
    noisyData = data * noiseMask
    return noisyData

def get_NN(units):
    model = Sequential()
    n_features = units[0]
    for i, n in enumerate(units[1:]):
        if i==0:
            model.add(Dense(units=n, activation='sigmoid', input_dim=n_features))
        else:
            model.add(Dense(units=n, activation='sigmoid'))
    return model