# based on: https://github.com/eclique/RISE/blob/fac5d54225977091dc18cc71ef8e07f726c3bc20/explanations.py

import numpy as np
import torch
import torch.nn as nn
from skimage.transform import resize
from tqdm import tqdm


class RISEResult:
    """
    Class returned by :func:`~interpret_segmentation.rise.SegmentationRISE.forward`.
    """
    def __init__(self, saliencies):
        self.saliencies = saliencies

    def max(self):
        """
        Merges the per pixel saliency map into one map using the ``torch.max()`` method.

        :return: 2D saliency map (PyTorch tensor)
        """
        return torch.max(self.saliencies, dim=0)[0].cpu().numpy()

    def mean(self):
        """
        Merges the per pixel saliency map into one map using the ``torch.mean()`` method.

        :return: 2D saliency map (PyTorch tensor)
        """
        return torch.mean(self.saliencies, dim=0).cpu().numpy()


class SegmentationRISE(nn.Module):
    """
    Explainer class for RISE on image segmentation models.
    The class is a PyTorch model, explaining works by calling the class instance as a function.
    """
    def __init__(self, model, input_size, device):
        """
        Constructor.
        The model needs to reside on the device given as a parameter to this method.

        :param model: Neural network model (PyTorch module)
        :param input_size: Tuple of image width and height
        :param device: PyTorch device
        """
        super(SegmentationRISE, self).__init__()
        self.model = model
        self.input_size = input_size
        self.device = device

    def generate_masks(self, N, s, p1, savepath='masks.npy'):
        """
        Generate rise masks.

        :param N: Mask count
        :param s: Distance between mask peaks
        :param p1: Threshold where to set mask. Between 0.0 and 1.0, 1.0 means masks on the whole image, \
        0.0 means no masks.
        :param savepath: Where to save the masks after generation, path to .npy file.
        """
        cell_size = np.ceil(np.array(self.input_size) / s)
        up_size = (s + 1) * cell_size

        grid = np.random.rand(N, s, s) < p1
        grid = grid.astype('float32')

        self.masks = np.empty((N, *self.input_size))

        for i in tqdm(range(N), desc='Generating filters'):
            # Random shifts
            x = np.random.randint(0, cell_size[0])
            y = np.random.randint(0, cell_size[1])
            # Linear upsampling and cropping
            self.masks[i, :, :] = resize(grid[i], up_size, order=1, mode='reflect',
                                         anti_aliasing=False)[x:x + self.input_size[0], y:y + self.input_size[1]]
        self.masks = self.masks.reshape(-1, 1, *self.input_size)
        np.save(savepath, self.masks)
        self.masks = torch.from_numpy(self.masks).float()
        self.masks = self.masks.to(self.device)
        self.N = N

    def load_masks(self, filepath):
        """
        Load masks from file saved by :func:`~interpret_segmentation.rise.SegmentationRISE.generate_masks`.

        :param filepath: Path to the .npy mask file
        """
        self.masks = np.load(filepath)
        self.masks = torch.from_numpy(self.masks).float().to(self.device)
        self.N = self.masks.shape[0]

    def forward(self, x):
        """
        Generate the saliency map for image x. Because this class is a PyTorch module, this method
        is never called directly but instead the class instance is used as a Functor:

        .. code-block:: python

            explainer = SegmentationRISE(...)
            ...
            explainer(image)

        :param x: The input image as a 2D numpy array
        :return: An instance of :class:`~interpret_segmentation.rise.RISEResult`
        """
        mask_count = self.N
        _, _, H, W = x.size()

        # generate new images by putting mask on top of original image
        stack = torch.mul(self.masks, x.data)

        output = self.model(x).squeeze()
        output = (output > output.mean())

        pixels = []
        for x in range(output.shape[0]):
            for y in range(output.shape[1]):
                if output[x][y]:
                    pixels.append((x, y))

        pixels_per_batch = 1000
        saliencies = []
        for i in range(0, len(pixels), pixels_per_batch):
            current_pixels = pixels[i:i+pixels_per_batch]

            # run generated images through the model
            p = []
            for i in range(0, mask_count):
                output_mask = self.model(stack[i:min(i + 1, mask_count)])
                pixel_classes = []
                for x, y in current_pixels:
                    pixel_classes.append(output_mask[0][x][y])
                p.append(torch.tensor([pixel_classes]))
            p = torch.cat(p)
            p = p.to(self.device)

            # Number of classes
            CL = p.size(1)

            sal = torch.matmul(p.data.transpose(0, 1), self.masks.view(mask_count, H * W))

            sal = sal.view((CL, H, W))
            sal /= mask_count
            saliencies.append(sal)

        merged = torch.cat(saliencies)
        return RISEResult(merged)
