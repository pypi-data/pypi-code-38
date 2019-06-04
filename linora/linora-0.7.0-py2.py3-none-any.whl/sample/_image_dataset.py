import os
import pathlib
import itertools
import pandas as pd

__all__ = ['ImageDataset', 'ImageClassificationFolderDataset']


class ImageDataset():
    def __init__(self, root, image_format=['png', 'jpg', 'jpeg'], label_func=None):
        self.root = root
        self.image_format = image_format

        p = pathlib.Path(self.root)
        self.data = pd.DataFrame(itertools.chain.from_iterable((p.rglob(f'*.{i}') for i in self.image_format)), columns=['image'])
        if label_func is not None:
            self.data['label'] = self.data.image.map(lambda x:label_func(x.name))
        self.data['image'] = self.data.astype(str)

class ImageClassificationFolderDataset():
    def __init__(self, root, image_format=['png', 'jpg', 'jpeg'], label_encoder=False):
        self.root = root
        self.image_format = image_format    

        file = os.listdir(self.root)
        file = [i for i in file if os.path.isdir(self.root+'/'+i) and i[0]!='.']
        data = pd.DataFrame()
        for i in file:
            data = pd.concat([data, pd.DataFrame({'image':os.listdir(self.root+'/'+i), 'label':i})])
        data = data.reset_index(drop=True)
        data['image'] = self.root+'/'+data.label+'/'+data.image
        data = data[data.image.map(lambda x: True if '.' in x.split('/')[-1] else False)]
        data = data[data.image.map(lambda x: True if x.split('/')[-1][0]!='.' else False)]
        data = data[data.image.map(lambda x: True if len(x.split('/')[-1].split('.'))==2 else False)]
        data = data[data.image.map(lambda x: True if str.lower(x.split('/')[-1].split('.')[1]) in self.image_format else False)]
        self.dataset = data.reset_index(drop=True)
        self.name_label_dict = {j: i for i, j in enumerate(data.label.unique())}
        if label_encoder:
            self.dataset['label'] = self.dataset.label.replace(self.name_label_dict)
