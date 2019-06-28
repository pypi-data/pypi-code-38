import numpy as np, math

#converts a string into a 2D numpy array of text the same shape as the image to be texterized
def buildBlock(text, dimensions):
    '''
    params:
    -text: a string to be split into a block
    -dimensions: the numpy shape of the input image

    return:
    A 2D numpy array of characters in the shape of dimensions
    '''

    assert len(dimensions) == 3, "Image dimensions have an invalid shape, aborting."

    char_arr = np.array(list(text))
    CHROMA_AREA = dimensions[0] * dimensions[1]
    
    if len(char_arr) > CHROMA_AREA:
        char_arr = char_arr[:CHROMA_AREA]
    else:
        append_index = 0
        while len(char_arr) < CHROMA_AREA:
            char_arr = np.append(char_arr, char_arr[append_index])
            append_index += 1
    
    return np.reshape(char_arr, dimensions[:2])