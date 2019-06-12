# Standard libraries
import os
import time
import random
import datetime
from abc import ABC, abstractmethod

# Third party libraries
import glob
import torch
import numpy as np
import torchvision.transforms.functional as FT
from torch import nn
from torch import optim
from torch.utils.data import DataLoader
from sklearn.externals import joblib

# User define libraries
from ..utils.helper import ProgressBar
from .lr_scheduler import ConstantLR
from .nn_helper import AverageMeter, clip_gradient
from ..utils.helper import mkdir
from .nn_helper import get_device

DEVICE = get_device()
#==============================================================================
# Base Class
#==============================================================================
class PTBaseModel(ABC):
    """ Interface containing some boilerplate code for training pytorch models.

    Subclassing models must implement
    define_evaluation_function
    define_loss_function
    define_model

    Parameters
    ----------
    data_loader: PTBaseDataLoader
        Class with function train_data_loader, valid_data_loader and attributes train_compose, valid_compose
        that yield tuple mapping data (pytorch tensor), label(pytorch tensor).
    plotter: VisdomLinePlotter, optional (default = None)
        Class for tracking data history.
    scheduler: _LRScheduler, optional (default = None)
        Child class of Pytorch learning rate scheduler.
    scheduler_params: dict
        Parameters of learning rate scheduler.
    batch_size: int, optional (default = 16)
        Train and valid batch size.
    num_training_epochs: int, optional (default = 100)
        Number of training epoachs.
    lr: double, optinal (default = 3e-4)
        Learning rate
    optimizer: str, optional (default = 'adam')
        Optimizer used for training model.
    grad_clip: double, optional (default = 5)
        Clip bound of weight.
    early_stopping_steps: int, optional (default = 5)
        Number of epoch to do early stop.
    warm_start_init_epoch:, optional (default = 0)
        Warm Started epoch.
    log_interval: optional (default = 5)
        Logging interval.
    log_dir:
        Log directory.
    checkpoint_dir:
        Check point directory.
    multi_gpus:int, optional (default = 1)
        1: Use multi gpus.
        0: Do not use multi gpus.
    num_restarts:int, optional (default = 0)
        Number of times to do restart after early stop.
    is_larger_better:bool, optional (default = 5)
        True: Evaluation metric larger better.
        False: Evaluation metric smaller better.
    """

    def __init__(self,
                 data_loader,
                 scheduler=None,
                 scheduler_params:dict=None,
                 plotter=None,
                 batch_size=16,
                 num_training_epochs=100,
                 lr=5e-4,
                 optimizer='adam',
                 grad_clip=5,
                 early_stopping_steps=5,
                 warm_start_init_epoch=0,
                 log_interval=1,
                 log_dir='logs',
                 checkpoint_dir='checkpoints',
                 multi_gpus=1,
                 num_restarts=None,
                 is_larger_better=1):

        self.data_loader = data_loader
        self.scheduler = scheduler
        self.scheduler_params = scheduler_params
        self.plotter = plotter
        self.batch_size = batch_size
        self.num_training_epochs = num_training_epochs
        self.lr = lr
        self.optimizer = optimizer
        self.grad_clip = grad_clip
        self.early_stopping_steps = early_stopping_steps
        self.warm_start_init_epoch = warm_start_init_epoch
        self.log_interval = log_interval
        self.log_dir = log_dir
        self.multi_gpus = multi_gpus
        self.checkpoint_dir = checkpoint_dir
        self.num_restarts = num_restarts
        self.is_larger_better = is_larger_better
        self.logging = print
        self.best_validation_loss = np.inf
        self.best_evaluation_score = 0
        self.best_validation_epoch = 1
        self.model = self.define_model()

    def fit(self):
        # time now
        self.now = datetime.datetime.now()

        # load pretrained model if necessary
        if self.warm_start_init_epoch:
            epoch = self.restore(self.warm_start_init_epoch)
            self.logging("warm start from epoch {}.".format(epoch))
        else:
            self.checkpoint_dir += str(self.now.year) + "_" + str(self.now.month) + "_" + str(self.now.day) + '_' + str(self.now.hour) + "_" + str(self.now.minute) + "/"
            epoch = 1

        train_data_loader = self.data_loader.train_data_loader(self.batch_size)
        valid_data_loader = self.data_loader.valid_data_loader(self.batch_size)

        # define model
        if self.multi_gpus:
            self.model = nn.DataParallel(self.model).to(DEVICE)
            self.logging("Training use multi GPUs.")
        else:
            self.model = self.model.to(DEVICE)

        # define loss function
        criterion = self.define_loss_function()

        # define trackers
        epochs_since_improvement = 0
        if self.is_larger_better:
            self.best_evaluation_score = -np.inf
        else:
            self.best_evaluation_score = np.inf
        restarts = 0


        optimizer = self.get_optimizer(self.lr)

        if self.scheduler is None:
            self.scheduler = ConstantLR(optimizer)
        else:
            self.scheduler = self.scheduler(optimizer=optimizer, **self.scheduler_params)

        while epoch <= self.num_training_epochs:
            self.progress_bar_train = ProgressBar(len(train_data_loader))
            self.progress_bar_valid = ProgressBar(len(valid_data_loader))
            self.scheduler.step()

            self._train(train_data_loader, criterion, optimizer, epoch)

            if epoch % self.log_interval == 0:
                validation_loss, val_evaluation_score = self._valid(valid_data_loader, criterion, epoch, restarts)

            validation_gap_loss= self.best_validation_loss - validation_loss
            self.best_validation_loss = min(validation_loss, self.best_validation_loss)
            validation_gap_metric = val_evaluation_score - self.best_evaluation_score
            if self.is_larger_better:
                self.best_evaluation_score = max(self.best_evaluation_score, val_evaluation_score)
            else:
                self.best_evaluation_score = min(self.best_evaluation_score, val_evaluation_score)

            if validation_gap_loss > 0 or validation_gap_metric > 0:
                self.save(self.checkpoint_dir, epoch)
                epochs_since_improvement = 0
                self.best_validation_epoch = epoch
                self.logging(f" * Save model at Epoch {epoch}\t | Improved loss: {validation_gap_loss:.3f}\t | Improved accuracy: {validation_gap_metric:.3f}")
            else:
                # early stop schedule
                epochs_since_improvement += 1
                self.logging(f" * Have not improved for {epochs_since_improvement} rounds")

            if epochs_since_improvement >= self.early_stopping_steps:
                if self.num_restarts is None or restarts >= self.num_restarts:
                    self.logging('Best validation [loss: {:.3f}], [accuracy: {:.3f}] at training epoch [{}]'.format(self.best_validation_loss, self.best_evaluation_score, self.best_validation_epoch))
                    return

                if restarts < self.num_restarts:
                    self.restore(self.best_validation_epoch)
                    epochs_since_improvement = 0
                    self.logging(" * Restore from epoch {}".format(self.best_validation_epoch))
                    for param_group, lr in zip(optimizer.param_groups, self.scheduler.get_lr()):
                        param_group['lr'] = lr/2
                    epoch = self.best_validation_epoch
                    restarts += 1

            epoch += 1


        self.logging('num_training_steps reached - ending training')

    def _train(self, data_loader, criterion, optimizer, epoch):
        """
        One epoch's training.

        :param train_loader: DataLoader for training data
        :param model: model
        :param criterion: MultiBox loss
        :param optimizer: optimizer
        :param epoch: epoch number
        """
        self.model.train()  # training mode enables dropout

        losses = AverageMeter()  # loss
        data_time = AverageMeter()  # data loading time
        batch_time = AverageMeter()  # forward prop. + back prop. time

        start = time.time()

        # Batches
        self.logging("\n")
        for i, (images, labels) in enumerate(data_loader):
            self.progress_bar_train.step(i+1)
            data_time.update(time.time() - start)
            # Move to default device
            images = images.to(DEVICE)
            if type(labels) == list:
                labels_update = []
                for label in labels:
                    labels_update.append([l.to(DEVICE) for l in label])
                labels = labels_update
                predicted_scores = self.model(images)
                # predicted_scores = [predicted_score.double().to(DEVICE) for predicted_score in predicted_scores]
            else:
                predicted_scores = self.model(images)

            loss = criterion(predicted_scores, labels)

            # Backward prop.
            optimizer.zero_grad()
            loss.backward()

            # Clip gradients, if necessary
            if self.grad_clip is not None:
                clip_gradient(optimizer, self.grad_clip)

            # Update model
            optimizer.step()

            losses.update(loss.item(), images.size(0))
            batch_time.update(time.time() - start)
            start = time.time()

        # Print status
        self.logging("\n" + "=" * 80)
        # self.logging(f"lr             : {self.scheduler.get_lr()[0]}")
        self.logging(f"Epoch          : {epoch} / {self.num_training_epochs}\t\t| progress => {(epoch) / self.num_training_epochs:.0%}")
        self.logging(f"Batch          : {i} / {len(data_loader)}\t\t| progress => {i / len(data_loader):.0%}")
        self.logging(f"Data Load Time : batch=>{data_time.value:.2f}[s]\t| average  => {data_time.avg:.2f}[s]")
        self.logging(f"Batch Run Time : batch=>{batch_time.value:.2f}[s]\t| average  => {batch_time.avg:.2f}[s]\t| sum  ==> {batch_time.sum:.2f}[s]")
        self.logging(f"Training Loss  : batch=>{losses.value:.4f}\t| average  => {losses.avg:.4f}")
        self.logging("=" * 80)
        if self.plotter is None:
            pass
        else:
            self.plotter.plot('loss', 'train', "Loss | Time [{}:{}]".format(self.now.hour, self.now.minute), epoch, losses.avg)

    def _valid(self, data_loader, criterion, epoch, restarts):
        """
        One epoch's validation.

        :param val_loader: DataLoader for validation data
        :param model: model
        :param criterion: MultiBox loss
        :return: average validation loss
        """
        self.model.eval()  # eval mode disables dropout

        losses = AverageMeter()
        accuracy = AverageMeter()
        batch_time = AverageMeter()

        start = time.time()

        # Prohibit gradient computation explicity because I had some problems with memory
        with torch.no_grad():
            # Batches

            for i, (images, labels) in enumerate(data_loader):
                self.progress_bar_valid.step(i+1)
                images = images.to(DEVICE)
                if type(labels) == list:
                    labels_update = []
                    for label in labels:
                        labels_update.append([l.to(DEVICE) for l in label])
                    labels = labels_update
                    predicted_scores = self.model(images)
                else:
                    predicted_scores = self.model(images)

                loss = criterion(predicted_scores, labels)

                evaluate_metric = self.define_evaluation_function(predicted_scores, labels)

                losses.update(loss.item(), images.size(0))
                if evaluate_metric is None:
                    pass
                else:
                    accuracy.update(evaluate_metric / images.size(0), images.size(0))
                batch_time.update(time.time() - start)

                start = time.time()

        if self.plotter is None:
            pass
        else:
            self.plotter.plot('loss', 'valid', "Loss | Time [{}:{}]".format(self.now.hour, self.now.minute), epoch, losses.avg)
            if evaluate_metric is not None:
                self.plotter.plot('accuracy', 'valid', "Accuracy | Time [{}:{}]".format(self.now.hour, self.now.minute), epoch, accuracy.avg)

        if evaluate_metric is not None:
            self.logging('\n * Validation Loss: {:.3f}\t | Accuracy: {:.2%}\t\t | Restart times: {}'.format(losses.avg, accuracy.avg, restarts))
        else:
            self.logging('\n * Validation Loss: {:.3f}\t | Restart times: {}'.format(losses.avg, restarts))

        return losses.avg, accuracy.avg

    def predict(self, image):
        """
        Args:
            image: PIL format
        """
        with torch.no_grad():
            try:
                image = self.data_loader.valid_compose(image)
            except AttributeError:
                image = FT.to_tensor(image)
            image = image.unsqueeze(0)
            image = image.to('cpu')
            # s = time.time()
            predicted_score = self.model(image)
            # e = time.time()
            # print(e - s)
        return predicted_score

    def __predict_folder(self, batch_size=16):
        test_data_loader = self.data_loader.test_data_loader(batch_size)

        predicted_scores_list = []
        with torch.no_grad():
            # Batches
            for i, image in enumerate(test_data_loader):
                # Move to default device
                image = image.to('cpu')
                # Forward prop.
                predicted_scores = self.model(image).double()
                predicted_scores_list.append(predicted_scores)

        res = torch.cat(predicted_scores_list, dim=0)

        joblib.dump(res, self.prediction_dir + "")
        return res

    def save(self, checkpoint_dir, epoch):
        mkdir(checkpoint_dir)
        state = {'epoch': epoch, 'model': checkpoint_dir + 'model_' + 'epoch' + str(epoch) + ".pth"}
        if self.multi_gpus:
            torch.save(self.model.module.state_dict(), checkpoint_dir + 'model_' + 'epoch' + str(epoch) + ".pth")
        else:
            torch.save(self.model.state_dict(), checkpoint_dir + 'model_' + 'epoch' + str(epoch) + ".pth")
        torch.save(state, checkpoint_dir + 'model_' + 'epoch' + str(epoch) + ".pth.tar")
        self._save_latest_checkpoint(checkpoint_dir)

    def _save_latest_checkpoint(self, checkpoint_dir, max_to_keep=4, verbose=0):
        saved_model_files = glob.glob(checkpoint_dir+'*.pth') + glob.glob(checkpoint_dir+'*.pth.tar')
        saved_model_files_lasted_n = sorted(saved_model_files, key=os.path.getctime)[-max_to_keep:]
        files_tobe_deleted = set(saved_model_files).difference(saved_model_files_lasted_n)

        for file in files_tobe_deleted:
            os.remove(file)
            if verbose:
                self.logging("Only keep {} model files, remove {}".format(max_to_keep, checkpoint_dir + file))

    def restore(self, epoch=None):
        if not epoch:
            newest_model_files = sorted(glob.glob(self.checkpoint_dir + '*.pth'), key=os.path.getctime)[-1]
            self.model.load_state_dict(torch.load(newest_model_files, map_location=DEVICE.type))
        else:
            checkpoint = torch.load(self.checkpoint_dir + 'model_' + 'epoch' + str(epoch) + ".pth.tar")
            epoch = checkpoint['epoch']
            self.model.load_state_dict(torch.load(checkpoint['model'], map_location=DEVICE.type))
        return epoch

    @abstractmethod
    def define_evaluation_function(self, preds, labels):
        """ Implement evaluation function here

        Parameters
        ----------
        labels : pytorch tensor or [pytorch tensor, ...]
                True labels, shape is [batch_size, num_pictures, 1]
        preds : pytorch tensor or [pytorch tensor, ...]
                Predict scores, shape is [batch_size, num_pictures, num_classes]

        Returns
        -------
        anonymous : python float
        """
        raise NotImplementedError

    @abstractmethod
    def define_loss_function(self):
        """ Implement loss function here

        Returns
        -------
        Pytorch Module Object, must implement __init__() and forward() method.
        """
        raise NotImplementedError

    @abstractmethod
    def define_model(self):
        """ Implement model structure here

        Returns
        -------
        Pytorch Module Object, must implement __init__() and forward() method.
        """
        raise NotImplementedError

    def get_optimizer(self, lr):
        if self.optimizer == 'adam':
            return optim.Adam(self.model.parameters(), lr=lr)
        else:
            return None

class PTBaseDataLoader:
    def __init__(self, PTBaseDataset, folder, train_compose, valid_compose, **kwargs):
        self.folder = folder
        self.PTBaseDataset = PTBaseDataset
        self.train_compose = train_compose
        self.valid_compose = valid_compose
        self.kwargs = kwargs

    def train_data_loader(self, batch_size):
        train_dataset = self.PTBaseDataset(self.folder, 'train', self.train_compose, **self.kwargs)
        return DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=train_dataset.collate_fn)

    def valid_data_loader(self, batch_size):
        valid_dataset = self.PTBaseDataset(self.folder, 'valid', self.valid_compose, **self.kwargs)
        return DataLoader(valid_dataset, batch_size=batch_size, shuffle=False, collate_fn=valid_dataset.collate_fn)

#==============================================================================
# 图像相关
#==============================================================================
def xyccwd_to_xymmmm(cxcy):
    """
        Convert bounding boxes from center-size coordinates (c_x, c_y, w, h) to boundary coordinates (x_min, y_min, x_max, y_max).

        :param cxcy: bounding boxes in center-size coordinates, a tensor of size (n_boxes, 4)
        :return: bounding boxes in boundary coordinates, a tensor of size (n_boxes, 4)
        """
    return torch.cat([cxcy[:,:2] - cxcy[:,2:]/2, cxcy[:,:2] + cxcy[:,2:]/2], dim=1)

def xymmmm_to_xyccwd(xy):
    """
        Convert bounding boxes from boundary coordinates (x_min, y_min, x_max, y_max) to center-size coordinates (c_x, c_y, w, h).

        :param xy: bounding boxes in boundary coordinates, a tensor of size (n_boxes, 4)
        :return: bounding boxes in center-size coordinates, a tensor of size (n_boxes, 4)
        """
    return torch.cat([(xy[:, 2:] + xy[:, :2]) / 2,  # c_x, c_y
                      xy[:, 2:] - xy[:, :2]], 1)  # w, h

def xyccwd_to_xygcgcgwgh(cxcy, priors_cxcy):
    """
        Encode bounding boxes (that are in center-size form) w.r.t. the corresponding prior boxes (that are in center-size form).

        For the center coordinates, find the offset with respect to the prior box, and scale by the size of the prior box.
        For the size coordinates, scale by the size of the prior box, and convert to the log-space.

        In the model, we are predicting bounding box coordinates in this encoded form.

        :param cxcy: bounding boxes in center-size coordinates, a tensor of size (n_priors, 4)
        :param priors_cxcy: prior boxes with respect to which the encoding must be performed, a tensor of size (n_priors, 4)
        :return: encoded bounding boxes, a tensor of size (n_priors, 4)
        """

    # The 10 and 5 below are referred to as 'variances' in the original Caffe repo, completely empirical
    # They are for some sort of numerical conditioning, for 'scaling the localization gradient'
    # See https://github.com/weiliu89/caffe/issues/155
    return torch.cat([(cxcy[:, :2] - priors_cxcy[:, :2]) / (priors_cxcy[:, 2:] / 10),  # g_c_x, g_c_y
                      torch.log(cxcy[:, 2:] / priors_cxcy[:, 2:]) * 5], 1)  # g_w, g_h

def xygcgcgwgh_to_xyccwd(gcxgcy, priors_cxcy):
    """
    Decode bounding box coordinates predicted by the model, since they are encoded in the form mentioned above.

    They are decoded into center-size coordinates.

    This is the inverse of the function above.

    :param gcxgcy: encoded bounding boxes, i.e. output of the model, a tensor of size (n_priors, 4)
    :param priors_cxcy: prior boxes with respect to which the encoding is defined, a tensor of size (n_priors, 4)
    :return: decoded bounding boxes in center-size form, a tensor of size (n_priors, 4)
    """

    return torch.cat([gcxgcy[:, :2] * priors_cxcy[:, 2:] / 10 + priors_cxcy[:, :2],  # c_x, c_y
                      torch.exp(gcxgcy[:, 2:] / 5) * priors_cxcy[:, 2:]], 1)  # w, h

def find_intersection(set_1, set_2):
    """
        Find the intersection of every box combination between two sets of boxes that are in boundary coordinates.

        :param set_1: set 1, a tensor of dimensions (n1, 4)
        :param set_2: set 2, a tensor of dimensions (n2, 4)
        :return: intersection of each of the boxes in set 1 with respect to each of the boxes in set 2, a tensor of dimensions (n1, n2)
        """
    lower_left = torch.max(set_1[:,:2].unsqueeze(1), set_2[:,:2].unsqueeze(0)) # (n1, n2, 4)
    upper_right = torch.min(set_1[:,2:].unsqueeze(1), set_2[:,2:].unsqueeze(0)) # (n1, n2, 4)
    dims_intersection = torch.clamp(upper_right - lower_left, min=0) # (n1, n2, 2)
    return dims_intersection[:,:,0] * dims_intersection[:,:,1] # (n1, n2)

def find_jaccard_overlap(set_1, set_2):
    """
        Find the Jaccard Overlap (IoU) of every box combination between two sets of boxes that are in boundary coordinates.

        :param set_1: set 1, a tensor of dimensions (n1, 4)
        :param set_2: set 2, a tensor of dimensions (n2, 4)
        :return: Jaccard Overlap of each of the boxes in set 1 with respect to each of the boxes in set 2, a tensor of dimensions (n1, n2)
        """
    areas_intersection = find_intersection(set_1, set_2) # (n1, n2)

    areas_set_1 = (set_1[:, 2] - set_1[:, 0]) * (set_1[:, 3] - set_1[:, 1])  # (n1)
    areas_set_2 = (set_2[:, 2] - set_2[:, 0]) * (set_2[:, 3] - set_2[:, 1])  # (n2)

    areas_union = areas_set_1.unsqueeze(1) + areas_set_2.unsqueeze(0) - areas_intersection # (n1, n2)

    return areas_intersection / areas_union # (n1, n2)

# Some augmentation functions below have been adapted from
# From https://github.com/amdegroot/ssd.pytorch/blob/master/utils/augmentations.py
def expand(image, boxes, filler):
    """
    Perform a zooming out operation by placing the image in a larger canvas of filler material.

    Helps to learn to detect smaller objects.

    :param image: image, a tensor of dimensions (3, original_h, original_w)
    :param boxes: bounding boxes in boundary coordinates, a tensor of dimensions (n_objects, 4)
    :param filler: RBG values of the filler material, a list like [R, G, B]
    :return: expanded image, updated bounding box coordinates
    """
    # Calculate dimensions of proposed expanded (zoomed-out) image
    original_h = image.size(1)
    original_w = image.size(2)
    max_scale = 4
    scale = random.uniform(1, max_scale)
    new_h = int(scale * original_h)
    new_w = int(scale * original_w)

    # Create such an image with the filler
    filler = torch.FloatTensor(filler)  # (3)
    new_image = torch.ones((3, new_h, new_w), dtype=torch.float) * filler.unsqueeze(1).unsqueeze(1)  # (3, new_h, new_w)
    # Note - do not use expand() like new_image = filler.unsqueeze(1).unsqueeze(1).expand(3, new_h, new_w)
    # because all expanded values will share the same memory, so changing one pixel will change all

    # Place the original image at random coordinates in this new image (origin at top-left of image)
    left = random.randint(0, new_w - original_w)
    right = left + original_w
    top = random.randint(0, new_h - original_h)
    bottom = top + original_h
    new_image[:, top:bottom, left:right] = image

    # Adjust bounding boxes' coordinates accordingly
    new_boxes = boxes + torch.FloatTensor([left, top, left, top]).unsqueeze(0)  # (n_objects, 4), n_objects is the no. of objects in this image

    return new_image, new_boxes

def random_crop(image, boxes, labels, difficulties):
    """
    Performs a random crop in the manner stated in the paper. Helps to learn to detect larger and partial objects.

    Note that some objects may be cut out entirely.

    Adapted from https://github.com/amdegroot/ssd.pytorch/blob/master/utils/augmentations.py

    :param image: image, a tensor of dimensions (3, original_h, original_w)
    :param boxes: bounding boxes in boundary coordinates, a tensor of dimensions (n_objects, 4)
    :param labels: labels of objects, a tensor of dimensions (n_objects)
    :param difficulties: difficulties of detection of these objects, a tensor of dimensions (n_objects)
    :return: cropped image, updated bounding box coordinates, updated labels, updated difficulties
    """
    original_h = image.size(1)
    original_w = image.size(2)
    # Keep choosing a minimum overlap until a successful crop is made
    while True:
        # Randomly draw the value for minimum overlap
        min_overlap = random.choice([0., .1, .3, .5, .7, .9, None])  # 'None' refers to no cropping

        # If not cropping
        if min_overlap is None:
            return image, boxes, labels, difficulties

        # Try up to 50 times for this choice of minimum overlap
        # This isn't mentioned in the paper, of course, but 50 is chosen in paper authors' original Caffe repo
        max_trials = 50
        for _ in range(max_trials):
            # Crop dimensions must be in [0.3, 1] of original dimensions
            # Note - it's [0.1, 1] in the paper, but actually [0.3, 1] in the authors' repo
            min_scale = 0.3
            scale_h = random.uniform(min_scale, 1)
            scale_w = random.uniform(min_scale, 1)
            new_h = int(scale_h * original_h)
            new_w = int(scale_w * original_w)

            # Aspect ratio has to be in [0.5, 2]
            aspect_ratio = new_h / new_w
            if not 0.5 < aspect_ratio < 2:
                continue

            # Crop coordinates (origin at top-left of image)
            left = random.randint(0, original_w - new_w)
            right = left + new_w
            top = random.randint(0, original_h - new_h)
            bottom = top + new_h
            crop = torch.FloatTensor([left, top, right, bottom])  # (4)

            # Calculate Jaccard overlap between the crop and the bounding boxes
            overlap = find_jaccard_overlap(crop.unsqueeze(0), boxes)  # (1, n_objects), n_objects is the no. of objects in this image
            overlap = overlap.squeeze(0)  # (n_objects)

            # If not a single bounding box has a Jaccard overlap of greater than the minimum, try again
            if overlap.max().item() < min_overlap:
                continue

            # Crop image
            new_image = image[:, top:bottom, left:right]  # (3, new_h, new_w)

            # Find centers of original bounding boxes
            bb_centers = (boxes[:, :2] + boxes[:, 2:]) / 2.  # (n_objects, 2)

            # Find bounding boxes whose centers are in the crop
            centers_in_crop = (bb_centers[:, 0] > left) * (bb_centers[:, 0] < right) * (bb_centers[:, 1] > top) * (
                    bb_centers[:, 1] < bottom)  # (n_objects), a Torch uInt8/Byte tensor, can be used as a boolean index

            # If not a single bounding box has its center in the crop, try again
            if not centers_in_crop.any():
                continue

            # Discard bounding boxes that don't meet this criterion
            new_boxes = boxes[centers_in_crop, :]
            new_labels = labels[centers_in_crop]
            new_difficulties = difficulties[centers_in_crop]

            # Calculate bounding boxes' new coordinates in the crop
            new_boxes[:, :2] = torch.max(new_boxes[:, :2], crop[:2])  # crop[:2] is [left, top]
            new_boxes[:, :2] -= crop[:2]
            new_boxes[:, 2:] = torch.min(new_boxes[:, 2:], crop[2:])  # crop[2:] is [right, bottom]
            new_boxes[:, 2:] -= crop[:2]

            return new_image, new_boxes, new_labels, new_difficulties

def flip(image, boxes):
    """
    Flip image horizontally.

    :param image: image, a PIL Image
    :param boxes: bounding boxes in boundary coordinates, a tensor of dimensions (n_objects, 4)
    :return: flipped image, updated bounding box coordinates
    """
    # Flip image
    new_image = FT.hflip(image)

    # Flip boxes
    new_boxes = boxes
    new_boxes[:, 0] = image.width - boxes[:, 0] - 1
    new_boxes[:, 2] = image.width - boxes[:, 2] - 1
    new_boxes = new_boxes[:, [2, 1, 0, 3]]

    return new_image, new_boxes

def resize(image, boxes, dims=(300, 300), return_percent_coords=True):
    """
    Resize image. For the SSD300, resize to (300, 300).

    Since percent/fractional coordinates are calculated for the bounding boxes (w.r.t image dimensions) in this process,
    you may choose to retain them.

    :param image: image, a PIL Image
    :param boxes: bounding boxes in boundary coordinates, a tensor of dimensions (n_objects, 4)
    :return: resized image, updated bounding box coordinates (or fractional coordinates, in which case they remain the same)
    """
    # Resize image
    new_image = FT.resize(image, dims)

    # Resize bounding boxes
    old_dims = torch.FloatTensor([image.width, image.height, image.width, image.height]).unsqueeze(0)
    new_boxes = boxes / old_dims  # percent coordinates

    if not return_percent_coords:
        new_dims = torch.FloatTensor([dims[1], dims[0], dims[1], dims[0]]).unsqueeze(0)
        new_boxes = new_boxes * new_dims

    return new_image, new_boxes

def photometric_distort(image):
    """
    Distort brightness, contrast, saturation, and hue, each with a 50% chance, in random order.

    :param image: image, a PIL Image
    :return: distorted image
    """
    new_image = image

    distortions = [FT.adjust_brightness,
                   FT.adjust_contrast,
                   FT.adjust_saturation,
                   FT.adjust_hue]

    random.shuffle(distortions)

    for d in distortions:
        if random.random() < 0.5:
            if d.__name__ is 'adjust_hue':
                # Caffe repo uses a 'hue_delta' of 18 - we divide by 255 because PyTorch needs a normalized value
                adjust_factor = random.uniform(-18 / 255., 18 / 255.)
            else:
                # Caffe repo uses 'lower' and 'upper' values of 0.5 and 1.5 for brightness, contrast, and saturation
                adjust_factor = random.uniform(0.5, 1.5)

            # Apply this distortion
            new_image = d(new_image, adjust_factor)

    return new_image

def transform(image, boxes, labels, difficulties, split):
    """
    Apply the transformations above.

    :param image: image, a PIL Image
    :param boxes: bounding boxes in boundary coordinates, a tensor of dimensions (n_objects, 4)
    :param labels: labels of objects, a tensor of dimensions (n_objects)
    :param difficulties: difficulties of detection of these objects, a tensor of dimensions (n_objects)
    :param split: one of 'TRAIN' or 'TEST', since different sets of transformations are applied
    :return: transformed image, transformed bounding box coordinates, transformed labels, transformed difficulties
    """
    assert split in {'TRAIN', 'TEST'}

    # Mean and standard deviation of ImageNet data that our base VGG from torchvision was trained on
    # see: https://pytorch.org/docs/stable/torchvision/models.html
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    new_image = image
    new_boxes = boxes
    new_labels = labels
    new_difficulties = difficulties
    # Skip the following operations if validation/evaluation
    if split == 'TRAIN':
        # A series of photometric distortions in random order, each with 50% chance of occurrence, as in Caffe repo
        new_image = photometric_distort(new_image)

        # Convert PIL image to Torch tensor
        new_image = FT.to_tensor(new_image)

        if 0:
         # Expand image (zoom out) with a 50% chance - helpful for training detection of small objects
            # Fill surrounding space with the mean of ImageNet data that our base VGG was trained on
            if random.random() < 0.5:
                new_image, new_boxes = expand(new_image, boxes, filler=mean)

            # Randomly crop image (zoom in)
            new_image, new_boxes, new_labels, new_difficulties = random_crop(new_image, new_boxes, new_labels,
                                                                             new_difficulties)

        # Convert Torch tensor to PIL image
        new_image = FT.to_pil_image(new_image)

        # Flip image with a 50% chance
        if random.random() < 0.5:
            new_image, new_boxes = flip(new_image, new_boxes)

    # Resize image to (300, 300) - this also converts absolute boundary coordinates to their fractional form
    new_image, new_boxes = resize(new_image, new_boxes, dims=(300, 300))

    # Convert PIL image to Torch tensor
    new_image = FT.to_tensor(new_image)

    # Normalize by mean and standard deviation of ImageNet data that our base VGG was trained on
    new_image = FT.normalize(new_image, mean=mean, std=std)

    return new_image, new_boxes, new_labels, new_difficulties
