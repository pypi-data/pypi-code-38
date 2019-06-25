import numpy
import torch
from torch.autograd import Variable
import torchvision.transforms as transforms
from bob.learn.pytorch.architectures.DltResNet import dltresnet34 as drn_arc
from bob.learn.pytorch.architectures.ResNet import resnet34 as resnet_arc
from bob.bio.base.preprocessor import Preprocessor
import bob.io.base
import torch.backends.cudnn as cudnn
import pickle
import pkg_resources
from bob.extension import rc
from bob.extension.download import download_file
import os
from bob.ap import Spectrogram
from scipy.signal import resample


class DltResNetExtractor(Preprocessor):
  """ The class for implementing the feature extraction of DltResNet embeddings.

  Attributes
  ----------
  network: :py:class:`torch.nn.Module`
      The network architecture
  cuda_flag: int32
      Use gpu for extracting the embeddings.

  """

  def __init__(self, model_file=None, num_classes=1211, bn_dim=128, cuda_flag=0, test=False, use_res=False):
    """ Init method

    Parameters
    ----------
    model_file: str
        The path of the trained network to load
    num_classes: float
        The number of classes (Default: 1211).
    bn_dim: int32
        The embedding dimension (Default: 128).
    cuda_flag: int32
        Use gpu for extracting the embeddings (Default: 0).
    test: bool
        Called for unit test (Default: False).
    use_res: bool
        Use ResNet model instead of DltResNet model (Default: False).

    """

    Preprocessor.__init__(self, min_preprocessed_file_size=bn_dim)

    # model
    model_type = "emb"
    if use_res:
      self.network = resnet_arc(num_classes=num_classes, tp=model_type, bn_dim=bn_dim)
    else:
      self.network = drn_arc(num_classes=num_classes, tp=model_type, bn_dim=bn_dim)
    self.cuda_flag = cuda_flag

    if model_file is None:
      if not test:
        if use_res:
          model_path = pkg_resources.resource_filename(__name__, 'data/rn34.pth.tar')
          if rc['bob.learn.pytorch.extractor.audio.rn_modelpath'] != None:
            model_path = rc['bob.learn.pytorch.extractor.audio.rn_modelpath']
        else:
          model_path = pkg_resources.resource_filename(__name__, 'data/drn34.pth.tar')
          if rc['bob.learn.pytorch.extractor.audio.drn_modelpath'] != None:
            model_path = rc['bob.learn.pytorch.extractor.audio.drn_modelpath']

        if not os.path.exists(model_path):
          os.makedirs(os.path.dirname(model_path), exist_ok=True)
          if use_res:
            url = 'https://www.idiap.ch/software/bob/data/bob/bob.learn.pytorch/master/models_emb128_2drp_aug_relu__voxceleb___rn34-best.cls.pth.tar'
          else:
            url = 'https://www.idiap.ch/software/bob/data/bob/bob.learn.pytorch/master/models_emb128_2drp_dlt_aug_relu__voxceleb___rn34-best.cls.pth.tar'
          download_file(url, model_path)
        model_file = model_path

      else:
        # do nothing (used mainly for unit testing)
        pass

    if test:
      self.network = torch.nn.DataParallel(self.network)
    else:
      if cuda_flag == 1:
        self.network = torch.nn.DataParallel(self.network).cuda()
        cudnn.benchmark = True
        checkpoint = torch.load(model_file)
      else:
        self.network = torch.nn.DataParallel(self.network)
        checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
      if 'state_dict' in checkpoint:
        self.network.load_state_dict(checkpoint['state_dict'], strict=False)
        self.network.net_type = model_type
        self.network.module.net_type = self.network.net_type
        self.network.eval()


  def extract_embeddings(self, model, specs, L, batch_size=1, cuda_flag=0, min_length=30):
    """ Extract features from spectrogram

    Parameters
    ----------
    model : :py:class:`torch.nn.Module`
      The trained pytorch model.
    specs : :py:class:`numpy.ndarray` (floats)
      The spectrogram of audio file.
    L : int32
      Maximum chunk size for embedding extraction. 0 for using all the data (Default: 0).
    batch_size : int32
      Batch size for extracting the embedding (Default: 1).
    cuda_flag : int32
      Use gpu for extracting the embeddings
    min_length : int32
      Minimum chunk size for embedding extraction (Default: 30).

    Returns
    -------
    feature : 2D :py:class:`numpy.ndarray` (floats)
      The extracted features as a 1d array of size 128

    """

    feats = []
    batch = []

    if L == 0 or L > specs.shape[0]:
        L = specs.shape[0]

    embedding_count = specs.shape[0] // L
    if embedding_count == 0 :
        embedding_count = 1
    elif specs.shape[0] % L > min_length:
        embedding_count += 1

    for i in range(embedding_count):
        if (i+1)* L < specs.shape[0]:
            k = specs[i*L:(i+1)*L,:]
        else:
            k = specs[i*L:,:]

        X = (k - k.mean(axis=0)) / (k.std(axis=0) + 1e-7)
        batch.append(X)
        if len(batch) == batch_size or i == embedding_count - 2 or i == embedding_count - 1:
          with torch.no_grad():
            in_batch = numpy.array(batch)
            if cuda_flag == 1:
                input_var = torch.autograd.Variable(torch.Tensor(in_batch).unsqueeze(1).cuda(async=True))
            else:
                input_var = torch.autograd.Variable(torch.Tensor(in_batch).unsqueeze(1))
            fX = model(input_var).data.cpu().numpy()
            feats.append(fX)
            batch = []

    return numpy.vstack(feats)

  def __call__(self, audio, annotations=None):
    """ Extract features from an audio file

    Parameters
    ----------
    audio : :py:class:`numpy.ndarray` (floats)
      The audio file to extract the features from.
    annotations : None
      Apply annotations if needed

    Returns
    -------
    feature : 2D :py:class:`numpy.ndarray` (floats)
      The extracted features as a 1d array of size 128

    """
    data = audio[1]
    if data.dtype =='int16':
      data = numpy.cast['float'](data)
    if numpy.max(numpy.abs(data)) < 1:
      data = data * 2**15

    rate = audio[0]
    # resample audio to 16KHz so it can work with the model
    if rate != 16000:
      samps = round(len(data) * 16000 / rate)  # Number of samples to resample
      data = resample(data, samps)
      rate = 16000

    win_length_ms = 25
    win_shift_ms = 10
    normalize_mean = True
    n_filters = 24
    f_min = 0.
    f_max = 4000.
    pre_emphasis_coef = 0.97
    mel_scale = True
    c = Spectrogram(rate, win_length_ms, win_shift_ms, n_filters,
                    f_min, f_max, pre_emphasis_coef, mel_scale, normalize_mean)
    input_feat = c(data)
    features = self.extract_embeddings(self.network, input_feat, 0, batch_size=1, cuda_flag=self.cuda_flag)
    return features


  def write_data(self, data, data_file, compression=0):
    """ Writes the given *preprocessed* data to a file with the given name.
    """
    f = bob.io.base.HDF5File(data_file, 'w')
    f.set("feats", data.astype('float'), compression=compression)


  def read_data(self, data_file):
    """ Reads the *preprocessed* data from the file
    """
    f= bob.io.base.HDF5File(data_file)
    feats = f.read("feats")
    return feats
