import torch
import PIL
import cv2

__all__ = ['LineSplit', 'LoadImageAndLabel', 'PIL_Loader', 'CV2_Loader', 'PIL2Numpy', 'Numpy2PIL', 'Numpy2Tensor', 'SavePIL', 'SaveCV2', 'CVImage2Tensor']

def str2int(s):
    return int(s)
def str2ints(s, sep=','):
    return [int(i.strip()) for i in s.split(',')]

LABEL_FUNCS = {
    'str2int': str2int,
}

class LineSplit(object):
    def __init__(self, root_folder='', sep=None, label_func='str2int'):
        self.root_folder = root_folder
        self.sep = sep
        self.label_func = label_func

    def __call__(self, line):
        imgpath, label = line.split(self.sep)
        imgpath = self.root_folder + imgpath
        label = LABEL_FUNCS[self.label_func]
        return imgpath, label

class LoadImageAndLabel(object):
    def __init__(self, root_folder='', sep=None, color_mode='rgb', lib='cv2'):
        self.root_folder = root_folder
        self.sep = sep
        self.color_mode = color_mode
        self.lib = lib

    def __call__(self, line):
        imgpath, label = line.split(self.sep)
        imgpath = self.root_folder + imgpath
        label = int(label)
        if self.color_mode == 'rgb':
            if self.lib == 'cv2':
                img = cv2.imread(imgpath)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if self.lib == 'pil':
                img = PIL.Image.open(imgpath).convert('RGB')
        elif self.color_mode == 'bgr':
            if self.lib == 'cv2':
                img = cv2.imread(imgpath)
            if self.lib == 'pil':
                img = PIL.Image.open(imgpath).convert('RGB')
                img = np.array(img)
                r, g, b = img.T
                img = np.array([b, g, r]).transpose()
                img = PIL.Image.fromarray(img)
        elif self.color_mode == 'gray':
            if self.lib == 'cv2':
                img = cv2.imread(imgpath, 0)
            if self.lib == 'pil':
                img = PIL.Image.open(imgpath).convert('L')
        else:
            assert False, "Unknown color_mode %s" % self.color_mode
        return img, label

class PIL_Loader(object):
    def __init__(self, color_mode='rgb'):
        self.color_mode = color_mode

    def __call__(self, imgpath):
        if self.color_mode.lower() == 'rgb':
            img = PIL.Image.open(imgpath).convert('RGB')
        elif self.color_mode.lower() == 'gray':
            img = PIL.Image.open(imgpath).convert('L')
        elif self.color_mode.lower() == 'bgr':
            img = PIL.Image.open(imgpath).convert('RGB')
            img = np.array(img)
            r, g, b = img.T
            img = np.array([b, g, r]).transpose()
            img = PIL.Image.fromarray(img)
        return img

class CV2_Loader(object):
    def __init__(self, color_mode='bgr'):
        self.color_mode = color_mode

    def __call__(self, imgpath):
        if self.color_mode.lower() == 'bgr':
            img = cv2.imread(imgpath)
        elif self.color_mode.lower() == 'gray':
            img = cv2.imread(imgpath, 0)
        elif self.color_mode.lower() == 'rgb':
            img = cv2.imgread(imgpath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

class PIL2Numpy(object):
   def __call__(self, img):
       return np.array(img)

class Numpy2PIL(object):
    def __call__(self, array):
        return PIL.Image.fromarray(array)

class Numpy2Tensor(object):
    def __call__(self, array):
        return torch.from_numpy(array)

class CVImage2Tensor(object):
    def __call__(self, image):
        return torch.from_numpy(image).permute(2, 0, 1)

class SavePIL(object):
    def __init__(self, savename):
        self.savename = savename

    def __call__(self, img):
        img.save(self.savename)
        return img

class SaveCV2(object):
    def __init__(self, savename):
        self.savename = savename

    def __call__(self, img):
        cv2.imwrite(self.savename, img)
        return img
