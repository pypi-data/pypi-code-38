from bob.pad.face.test.dummy.database import DummyDatabase as Database
from bob.pad.face.utils import yield_faces, scale_face, blocks
from nose.tools import raises
import numpy

padfile = Database().all_files(('train', 'dev'))[0][0]
image = padfile.load(Database().original_directory,
                     Database().original_extension)[0][1]


def dummy_cropper(frame, annotations=None):
    return frame


def test_yield_frames():
    database = Database()
    nframes = database.number_of_frames(padfile)
    assert nframes == 1, nframes
    for frame in padfile.frames:
        assert frame.ndim == 2
        assert frame.shape == database.frame_shape


@raises(ValueError)
def test_yield_faces_1():
    padfile.none_annotations = True
    for face in yield_faces(padfile, dummy_cropper):
        pass


def test_yield_faces_2():
    padfile.none_annotations = False
    assert len(list(yield_faces(padfile, dummy_cropper)))
    for face in yield_faces(padfile, dummy_cropper):
        assert face.ndim == 2
        assert face.shape == padfile.frame_shape


def test_scale_face():
    # gray-scale image
    face = image
    scaled_face = scale_face(face, 64)
    assert scaled_face.dtype == 'float64'
    assert scaled_face.shape == (64, 64)
    # color image
    scaled_face = scale_face(numpy.array([face, face, face]), 64)
    assert scaled_face.dtype == 'float64'
    assert scaled_face.shape == (3, 64, 64)
    assert (scaled_face[0] == scaled_face[1]).all()
    assert (scaled_face[0] == scaled_face[2]).all()


def test_blocks():
    # gray-scale image
    patches = blocks(image, (28, 28))
    assert patches.shape == (12, 28, 28), patches.shape
    # color image
    patches_gray = patches
    patches = blocks([image, image, image], (28, 28))
    assert patches.shape == (12, 3, 28, 28), patches.shape
    assert (patches_gray == patches[:, 0, ...]).all()
    assert (patches_gray == patches[:, 1, ...]).all()
    assert (patches_gray == patches[:, 2, ...]).all()
    # color video
    patches = blocks([[image, image, image]], (28, 28))
    assert patches.shape == (12, 3, 28, 28), patches.shape
    assert (patches_gray == patches[:, 0, ...]).all()
    assert (patches_gray == patches[:, 1, ...]).all()
    assert (patches_gray == patches[:, 2, ...]).all()


@raises(ValueError)
def test_block_raises1():
    blocks(image[0], (28, 28))


@raises(ValueError)
def test_block_raises2():
    blocks([[[image]]], (28, 28))
