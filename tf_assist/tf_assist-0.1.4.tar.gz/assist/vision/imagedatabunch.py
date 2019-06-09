from .utils import subfolder_count


from pathlib import Path
from tensorflow import keras
from tensorflow.keras import applications as models
import scipy

class ImageDataBunch:
    ''' Provides methods for loading images
    Dep: tf.keras, scipy, pathlib.Path()
    '''
    def __init__(self, image_shape:tuple, num_classes:int=None):
        
        self.image_shape = image_shape
        self.train = None  # set it to train_generator
        self.val = None    # set it to val_generator
        self.num_classes = num_classes #will be updated  in methods
        
        self.batch_size = 32
        self.train_size = None
        self.val_size = None
        self.path = None

    
    def from_folder(self, path:'pathlib.Path'='data',
                    train_folder:str='train', valid_folder:str='valid',
                    batch_size:int=32):
        '''Creates dataloader from images in train and validation folder
        path: location of dataset
        batch_size = batch size
        
        '''
        
        self.path = Path(path)
        self.train_path = self.path/train_folder
        self.val_path = self.path/valid_folder
        
        train_datagen = keras.preprocessing.image.ImageDataGenerator(
                rescale=1./255)
        test_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
        
        # count classes by looking at subfolder count
        num_subfolders = subfolder_count(self.train_path)
        if num_subfolders > 2:
            class_mode = 'categorical'
        else:
            class_mode = 'binary'
        
        
        train_generator = train_datagen.flow_from_directory(
                self.train_path,
                target_size= self.image_shape,
                batch_size=batch_size,
                class_mode=class_mode)
        validation_generator = test_datagen.flow_from_directory(
                self.val_path,
                target_size= self.image_shape,
                batch_size=batch_size,
                class_mode=class_mode)
        
        self.num_classes = train_generator.num_classes
        self.train = train_generator
        self.val = validation_generator
        self.train_size = train_generator.n
        self.val_size = validation_generator.n
        self.batch_size = batch_size
        
        return train_generator, validation_generator
