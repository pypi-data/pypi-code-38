from torch.utils.data import Dataset
import pandas as pd
import os
from skimage import io, transform


class MOTDataset(Dataset):
    """
    Dataset from the MOT 17 challenge
    URL: https://motchallenge.net/data/MOT17/
    """

    def __init__(self, scene, root_dir, challenge='MOT17', transform=None):
        """
        Args:
            scene (string): Path to a MOT scene.
            root_dir (string): Directory with all the images.
            challenge (string): Specify the MOT challenge.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_dir = root_dir
        self.transform = transform
        self.scene = scene

        if challenge in ['2D MOT 2015', 'MOT16', 'PETS2017', 'MOT17']:
            det_path = os.path.join(root_dir, self.scene, 'det', 'det.txt')
            self.detections = pd.read_csv(det_path, header=None)

    def __len__(self):
        return len([name for name in os.listdir(os.path.join(self.root_dir, self.scene, 'img1'))
                    if os.path.isfile(name)])

    def __getitem__(self, idx):
        try:
            img_name = os.path.join(self.root_dir, self.scene, 'img1', str(idx + 1).zfill(6) + '.jpg')
            image = io.imread(img_name)
        except FileNotFoundError:
            raise IndexError
        detections = self.detections.loc[self.detections[0] == idx + 1].values
        sample = {'image': image, 'detections': detections}
        return sample


class MOT17DetDataset(Dataset):
    """
    Dataset from the MOT17Det challenge
    URL: https://motchallenge.net/data/MOT17Det/
    """

    def __init__(self, scene, root_dir, transform=None, train=True):
        """
        Args:
            scene (string): Path to a MOT scene.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
            train (boolean): Specify whether to use training data or testing data.
        """
        self.train = train
        if self.train:
            self.root_dir = os.path.join(root_dir, 'train')
        else:
            self.root_dir = os.path.join(root_dir, 'test')
        self.transform = transform
        self.scene = scene
        if self.train:
            det_path = os.path.join(self.root_dir, self.scene, 'gt', 'gt.txt')
            self.detections = pd.read_csv(det_path, header=None)
        else:
            self.detections = None

    def __len__(self):
        return len([name for name in os.listdir(os.path.join(self.root_dir, self.scene, 'img1'))
                    if os.path.isfile(name)])

    def __getitem__(self, idx):
        try:
            img_name = os.path.join(self.root_dir, self.scene, 'img1', str(idx + 1).zfill(6) + '.jpg')
            image = io.imread(img_name)
        except FileNotFoundError:
            raise IndexError
        if self.train:
            detections = self.detections.loc[self.detections[0] == idx + 1].values
            scores = detections[:,6]
            detections = detections[:,2:6]
            print(detections)
        else:
            detections = None
        sample = {'image': image, 'detections': detections}
        return sample


class CDNet2014Dataset(Dataset):
    """
    Dataset from the CDNet 2014 Challenge
    """

    def __init__(self, category, scene, root_dir, transform=None):
        """
        Args:
            root_dir (string): Directory with all the images.
            category (string): Category of the CDNet 2014 challenge (e.g. 'cameraJitter').
            scene (string): Name of the CDNet 2014 scene in this category (e.g. 'traffic').
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_dir = root_dir
        self.transform = transform
        self.category = category
        self.scene = scene

        roi_name = os.path.join(self.root_dir, self.category, self.scene,
                                'temporalROI.txt')
        with open(roi_name) as f:
            roi_str = f.readline()
        start, end = tuple(roi_str.split(' '))
        self.start = int(start)
        self.end = int(end)

    def __len__(self):
        return len([name for name in os.listdir(os.path.join(self.root_dir, self.category, self.scene, 'in'))
                    if os.path.isfile(name)])

    def __getitem__(self, idx):
        try:
            img_name = os.path.join(self.root_dir, self.category, self.scene,
                                    'input', 'in' + str(idx + 1).zfill(6) + '.jpg')
            image = io.imread(img_name, as_gray=True)
            gt_name = os.path.join(self.root_dir, self.category, self.scene,
                                   'groundtruth', 'gt' + str(idx + 1).zfill(6) + '.png')
            gt = io.imread(gt_name, as_gray=True)
        except FileNotFoundError:
            raise IndexError
        sample = {'image': image, 'gt': gt, 'start': self.start, 'end': self.end}
        return sample
