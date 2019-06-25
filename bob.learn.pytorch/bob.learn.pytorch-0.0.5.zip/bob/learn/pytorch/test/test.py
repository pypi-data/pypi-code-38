#!/usr/bin/env python
# encoding: utf-8


from torch.utils.data import Dataset
""" Unit tests

"""

import numpy
import torch
from torch.autograd import Variable


def test_architectures():

    a = numpy.random.rand(1, 3, 128, 128).astype("float32")
    t = torch.from_numpy(a)

    number_of_classes = 20
    output_dimension = number_of_classes

    # CASIANet
    from ..architectures import CASIANet
    net = CASIANet(number_of_classes)
    embedding_dimension = 320
    output, emdedding = net.forward(t)
    assert output.shape == torch.Size([1, 20])
    assert emdedding.shape == torch.Size([1, 320])

    # CNN8
    from ..architectures import CNN8
    net = CNN8(number_of_classes)
    embedding_dimension = 512
    output, emdedding = net.forward(t)
    assert output.shape == torch.Size([1, 20])
    assert emdedding.shape == torch.Size([1, 512])

    # LightCNN9
    a = numpy.random.rand(1, 1, 128, 128).astype("float32")
    t = torch.from_numpy(a)
    from ..architectures import LightCNN9
    net = LightCNN9()
    output, emdedding = net.forward(t)
    assert output.shape == torch.Size([1, 79077])
    assert emdedding.shape == torch.Size([1, 256])

    # LightCNN29
    from ..architectures import LightCNN29
    net = LightCNN29()
    output, emdedding = net.forward(t)
    assert output.shape == torch.Size([1, 79077])
    assert emdedding.shape == torch.Size([1, 256])

    # LightCNN29v2
    from ..architectures import LightCNN29v2
    net = LightCNN29v2()
    output, emdedding = net.forward(t)
    assert output.shape == torch.Size([1, 79077])
    assert emdedding.shape == torch.Size([1, 256])

    # MCCNN
    a = numpy.random.rand(1, 4, 128, 128).astype("float32")
    t = torch.from_numpy(a)
    from ..architectures import MCCNN
    net = MCCNN(num_channels=4)
    output = net.forward(t)
    assert output.shape == torch.Size([1, 1])

    # MCCNNv2
    from ..architectures import MCCNNv2
    net = MCCNNv2(num_channels=4)
    output = net.forward(t)
    assert output.shape == torch.Size([1, 1])

    # FASNet
    a = numpy.random.rand(1, 3, 224, 224).astype("float32")
    t = torch.from_numpy(a)
    from ..architectures import FASNet
    net = FASNet(pretrained=False)
    output = net.forward(t)
    assert output.shape == torch.Size([1, 1])

    # DeepMSPAD
    a = numpy.random.rand(1, 8, 224, 224).astype("float32")
    t = torch.from_numpy(a)
    from ..architectures import DeepMSPAD
    net = DeepMSPAD(pretrained=False, num_channels=8)
    output = net.forward(t)
    assert output.shape == torch.Size([1, 1])

    # DeepPixBiS
    a = numpy.random.rand(1, 3, 224, 224).astype("float32")
    t = torch.from_numpy(a)
    from ..architectures import DeepPixBiS
    net = DeepPixBiS(pretrained=False)
    output = net.forward(t)
    assert output[0].shape == torch.Size([1, 1, 14, 14])
    assert output[1].shape == torch.Size([1, 1])

    # MCDeepPixBiS
    a = numpy.random.rand(1, 8, 224, 224).astype("float32")
    t = torch.from_numpy(a)
    from ..architectures import MCDeepPixBiS
    net = MCDeepPixBiS(pretrained=False, num_channels=8)
    output = net.forward(t)
    assert output[0].shape == torch.Size([1, 1, 14, 14])
    assert output[1].shape == torch.Size([1, 1])

    # DCGAN
    d = numpy.random.rand(1, 3, 64, 64).astype("float32")
    t = torch.from_numpy(d)
    from ..architectures import DCGAN_discriminator
    discriminator = DCGAN_discriminator(1)
    output = discriminator.forward(t)
    assert output.shape == torch.Size([1])

    g = numpy.random.rand(1, 100, 1, 1).astype("float32")
    t = torch.from_numpy(g)
    from ..architectures import DCGAN_generator
    generator = DCGAN_generator(1)
    output = generator.forward(t)
    assert output.shape == torch.Size([1, 3, 64, 64])

    # Conditional GAN
    t = torch.from_numpy(d)
    cfm = numpy.zeros((1, 13, 64, 64), dtype="float32")
    cfm[:, 0, :, :] = 1
    cfmt = torch.from_numpy(cfm)
    from ..architectures import ConditionalGAN_discriminator
    discriminator = ConditionalGAN_discriminator(13)
    output = discriminator.forward(t, cfmt)
    assert output.shape == torch.Size([1])

    t = torch.from_numpy(g)
    oh = numpy.zeros((1, 13, 1, 1), dtype="float32")
    oh[0] = 1
    oht = torch.from_numpy(oh)
    from ..architectures import ConditionalGAN_generator
    discriminator = ConditionalGAN_generator(100, 13)
    output = discriminator.forward(t, oht)
    assert output.shape == torch.Size([1, 3, 64, 64])

    # Convolutional Autoencoder
    from bob.learn.pytorch.architectures import ConvAutoencoder
    batch = torch.randn(1, 3, 64, 64)
    model = ConvAutoencoder()
    output = model(batch)
    assert batch.shape == output.shape
    model_embeddings = ConvAutoencoder(return_latent_embedding=True)
    embedding = model_embeddings(batch)
    assert list(embedding.shape) == [1, 16, 5, 5]


def test_transforms():

    image = numpy.random.rand(3, 128, 128).astype("uint8")

    img = numpy.random.rand(128, 128, 4).astype("uint8")

    from ..datasets import ChannelSelect
    cs = ChannelSelect(selected_channels=[0, 1, 2])
    assert(cs(img).shape == (128, 128, 3))

    from ..datasets import RandomHorizontalFlipImage
    rh = RandomHorizontalFlipImage(p=0.5)
    assert(numpy.allclose(rh(rh(img)), img))

    from ..datasets import RollChannels
    sample = {'image': image}
    rc = RollChannels()
    rc(sample)
    assert sample['image'].shape == (128, 128, 3)

    from ..datasets import ToTensor
    tt = ToTensor()
    tt(sample)
    assert isinstance(sample['image'], torch.Tensor)
    # grayscale
    image_gray = numpy.random.rand(128, 128).astype("uint8")
    sample_gray = {'image': image_gray}
    tt(sample_gray)
    assert isinstance(sample['image'], torch.Tensor)

    from ..datasets import Normalize
    image_copy = torch.Tensor(sample['image'])
    norm = Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    norm(sample)
    for c in range(3):
        for h in range(sample['image'].shape[0]):
            for w in range(sample['image'].shape[1]):
                assert (abs(sample['image'][c, h, w]) -
                        abs((image_copy[c, h, w] - 0.5) / 0.5)) < 1e-10


def test_map_labels():

    labels = ['1', '4', '7']
    from ..datasets import map_labels
    new_labels = map_labels(labels)
    assert '0' in new_labels, "new_labels = {}".format(new_labels)
    assert '1' in new_labels, "new_labels = {}".format(new_labels)
    assert '2' in new_labels, "new_labels = {}".format(new_labels)

    new_labels = map_labels(labels, start_index=5)
    assert '5' in new_labels, "new_labels = {}".format(new_labels)
    assert '6' in new_labels, "new_labels = {}".format(new_labels)
    assert '7' in new_labels, "new_labels = {}".format(new_labels)


class DummyDataSet(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 100

    def __getitem__(self, idx):
        data = numpy.random.rand(1, 128, 128).astype("float32")
        label = numpy.random.randint(20)
        sample = {'image': torch.from_numpy(data), 'label': label}
        return sample


class DummyDataSetGeneric(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 20

    def __getitem__(self, idx):
        data = numpy.random.rand(1, 224, 224).astype("float32")
        label = numpy.random.randint(2)
        sample = torch.from_numpy(data), label
        return sample


def test_CNNtrainer():

    from ..architectures import LightCNN9
    net = LightCNN9(20)

    dataloader = torch.utils.data.DataLoader(
        DummyDataSet(), batch_size=32, shuffle=True)

    from ..trainers import CNNTrainer
    trainer = CNNTrainer(net, verbosity_level=3)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('model_1_0.pth')

    os.remove('model_1_0.pth')


def test_Generictrainer():

    from ..architectures import DeepMSPAD
    net = DeepMSPAD(num_channels=1, pretrained=False)

    dataloader = {}
    dataloader['train'] = torch.utils.data.DataLoader(
        DummyDataSetGeneric(), batch_size=8, shuffle=True)

    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, net.parameters()), lr=0.1)

    criterion = torch.nn.BCELoss()

    def compute_loss(network, img, labels, device):
        """
        Compute the losses, given the network, data and labels and 
        device in which the computation will be performed. 
        """

        imagesv = Variable(img.to(device))

        labelsv_binary = Variable(labels.to(device))

        out = network(imagesv)

        loss = criterion(out, labelsv_binary.unsqueeze(1).float())

        return loss

    from ..trainers import GenericTrainer
    trainer = GenericTrainer(net, optimizer=optimizer,
                             compute_loss=compute_loss, verbosity_level=3)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('model_1_0.pth')
    assert os.path.isfile('model_0_0.pth')

    os.remove('model_1_0.pth')
    os.remove('model_0_0.pth')


class DummyDataSetMCCNN(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 100

    def __getitem__(self, idx):
        data = numpy.random.rand(4, 128, 128).astype("float32")
        label = numpy.random.randint(2)
        sample = data, label
        return sample


def test_MCCNNtrainer():

    from ..architectures import MCCNN
    net = MCCNN(num_channels=4)

    dataloader = {}
    dataloader['train'] = torch.utils.data.DataLoader(
        DummyDataSetMCCNN(), batch_size=32, shuffle=True)

    from ..trainers import MCCNNTrainer
    trainer = MCCNNTrainer(net, verbosity_level=3, do_crossvalidation=False)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('model_1_0.pth')

    os.remove('model_1_0.pth')


def test_MCCNNtrainer_cv():

    from ..architectures import MCCNN
    net = MCCNN(num_channels=4)

    dataloader = {}
    dataloader['train'] = torch.utils.data.DataLoader(
        DummyDataSetMCCNN(), batch_size=32, shuffle=True)
    dataloader['val'] = torch.utils.data.DataLoader(
        DummyDataSetMCCNN(), batch_size=32, shuffle=True)

    from ..trainers import MCCNNTrainer
    trainer = MCCNNTrainer(net, verbosity_level=3, do_crossvalidation=True)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('model_1_0.pth')
    assert os.path.isfile('model_100_0.pth')  # the best model

    os.remove('model_1_0.pth')
    os.remove('model_100_0.pth')


class DummyDataSetFASNet(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 100

    def __getitem__(self, idx):
        data = numpy.random.rand(3, 224, 224).astype("float32")
        label = numpy.random.randint(2)
        sample = data, label
        return sample


def test_FASNettrainer():

    from ..architectures import FASNet
    net = FASNet(pretrained=False)

    dataloader = {}
    dataloader['train'] = torch.utils.data.DataLoader(
        DummyDataSetFASNet(), batch_size=32, shuffle=True)

    from ..trainers import FASNetTrainer
    trainer = FASNetTrainer(net, verbosity_level=3, do_crossvalidation=False)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('model_1_0.pth')

    os.remove('model_1_0.pth')


def test_FASNettrainer_cv():

    from ..architectures import FASNet
    net = FASNet(pretrained=False)

    dataloader = {}
    dataloader['train'] = torch.utils.data.DataLoader(
        DummyDataSetFASNet(), batch_size=32, shuffle=True)
    dataloader['val'] = torch.utils.data.DataLoader(
        DummyDataSetFASNet(), batch_size=32, shuffle=True)

    from ..trainers import FASNetTrainer
    trainer = FASNetTrainer(net, verbosity_level=3, do_crossvalidation=True)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('model_1_0.pth')
    assert os.path.isfile('model_100_0.pth')

    os.remove('model_1_0.pth')
    os.remove('model_100_0.pth')


class DummyDataSetGAN(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 100

    def __getitem__(self, idx):
        data = numpy.random.rand(3, 64, 64).astype("float32")
        sample = {'image': torch.from_numpy(data)}
        return sample


def test_DCGANtrainer():

    from ..architectures import DCGAN_generator
    from ..architectures import DCGAN_discriminator
    g = DCGAN_generator(1)
    d = DCGAN_discriminator(1)

    dataloader = torch.utils.data.DataLoader(
        DummyDataSetGAN(), batch_size=32, shuffle=True)

    from ..trainers import DCGANTrainer
    trainer = DCGANTrainer(g, d, batch_size=32, noise_dim=100,
                           use_gpu=False, verbosity_level=2)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('fake_samples_epoch_000.png')
    assert os.path.isfile('netD_epoch_0.pth')
    assert os.path.isfile('netG_epoch_0.pth')

    os.remove('fake_samples_epoch_000.png')
    os.remove('netD_epoch_0.pth')
    os.remove('netG_epoch_0.pth')


class DummyDataSetConditionalGAN(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 100

    def __getitem__(self, idx):
        data = numpy.random.rand(3, 64, 64).astype("float32")
        sample = {'image': torch.from_numpy(
            data), 'pose': numpy.random.randint(0, 13)}
        return sample


def test_ConditionalGANTrainer():

    from ..architectures import ConditionalGAN_generator
    from ..architectures import ConditionalGAN_discriminator
    g = ConditionalGAN_generator(100, 13)
    d = ConditionalGAN_discriminator(13)

    dataloader = torch.utils.data.DataLoader(
        DummyDataSetConditionalGAN(), batch_size=32, shuffle=True)

    from ..trainers import ConditionalGANTrainer
    trainer = ConditionalGANTrainer(
        g, d, [3, 64, 64], batch_size=32, noise_dim=100, conditional_dim=13)
    trainer.train(dataloader, n_epochs=1, output_dir='.')

    import os
    assert os.path.isfile('fake_samples_epoch_000.png')
    assert os.path.isfile('netD_epoch_0.pth')
    assert os.path.isfile('netG_epoch_0.pth')
    os.remove('fake_samples_epoch_000.png')
    os.remove('netD_epoch_0.pth')
    os.remove('netG_epoch_0.pth')


def test_extractors():

    # lightCNN9
    from bob.learn.pytorch.extractor.image import LightCNN9Extractor
    extractor = LightCNN9Extractor()
    # this architecture expects 128x128 grayscale images
    data = numpy.random.rand(128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 256

    # lightCNN29
    from bob.learn.pytorch.extractor.image import LightCNN29Extractor
    extractor = LightCNN29Extractor()
    # this architecture expects 128x128 grayscale images
    data = numpy.random.rand(128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 256

    # lightCNN29v2
    from bob.learn.pytorch.extractor.image import LightCNN29v2Extractor
    extractor = LightCNN29v2Extractor()
    # this architecture expects 128x128 grayscale images
    data = numpy.random.rand(128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 256

    # MCCNN
    from ..extractor.image import MCCNNExtractor
    extractor = MCCNNExtractor(num_channels_used=4)
    # this architecture expects num_channelsx128x128 Multi channel images
    data = numpy.random.rand(4, 128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 1

    # MCCNNv2
    from ..extractor.image import MCCNNv2Extractor
    extractor = MCCNNv2Extractor(num_channels_used=4)
    # this architecture expects num_channelsx128x128 Multi channel images
    data = numpy.random.rand(4, 128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 1

    # FASNet
    from ..extractor.image import FASNetExtractor
    extractor = FASNetExtractor()
    # this architecture expects RGB images of size 3x224x224 channel images
    data = numpy.random.rand(3, 224, 224).astype("uint8")
    output = extractor(data)
    assert output.shape[0] == 1

    # MCDeepPixBiS
    from ..extractor.image import MCDeepPixBiSExtractor
    extractor = MCDeepPixBiSExtractor(
        num_channels=8, scoring_method='pixel_mean')
    # this architecture expects multi-channel images of size num_channelsx224x224
    data = numpy.random.rand(8, 224, 224).astype("uint8")
    output = extractor(data)
    assert output.shape[0] == 1
