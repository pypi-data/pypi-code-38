#!/usr/bin/env python
# encoding: utf-8

'''A set of helper utitilities to deal with menpo images and point clouds'''

import os
import collections

import logging
logger = logging.getLogger(__name__)

import numpy

import bob.ip.draw
import bob.ip.color
import bob.ip.facedetect

import menpo.io
import menpo.shape
import menpo.image


# This variable caches the loaded menpo landmark model to avoid reloading
LANDMARK_MODEL = None

# This variable caches the loaded dlib face detector to avoid reloading
DLIB_MODEL = None


def _detect_face_using_dlib(data):
  '''Detect faces using dlib's face detector with the help of menpo.

  .. warning::

     To use this function, you must have the modules ``menpodetect`` and
     ``dlib`` installed on your system.

  Parameters:

    data (:py:class:`numpy.ndarray`): A ``float64`` array with 2 dimensions,
      corresponding to a gray-scale image loaded with Bob (y, x) ordering and
      then normalized between 0 and 1.


  Returns:

    :py:class:`menpo.shape.PointCloud`: A point-cloud in Menpo format, with 4
      points corresponding to the 4 edges of the bounding box in the following
      format: (top-left, bottom-left, bottom-right, top-right).

  '''

  import menpodetect

  global DLIB_MODEL
  if DLIB_MODEL is None: #tries to load it
    logging.debug('Loading DLIB face detector...')
    DLIB_MODEL = menpodetect.load_dlib_frontal_face_detector()
    logging.debug('Loading DLIB face detector: OK')

  return DLIB_MODEL(data)


def _bob_boundingbox_to_menpo(b):
  '''Converts a :py:class:`bob.ip.facedetect.BoundingBox` into a
  :py:mod:`menpo.shape.PointCloud`.

  Parameters:

    b (:py:class:`bob.ip.facedetect.BoundingBox`): A bounding box in Bob
      format, as output by :py:func:`bob.ip.facedetect.detect_single_face`.


  Returns:

    :py:class:`menpo.shape.PointCloud`: A point-cloud in Menpo format, ready
      for use for the landmark detection.

  '''

  return menpo.shape.PointCloud([
    b.topleft,
    (b.bottomright[0], b.topleft[1]),
    b.bottomright,
    (b.topleft[0], b.bottomright[1]),
    ])


def _detect_landmarks_on_grayscale_image(data, bounding_box):
  '''Detects landmarks on gray-scaled image, returns point-clouds from menpo

  This function will first load a landmark detection model, if that is not
  already cached. It will then detect landmarks for the face at the provided
  bounding box.

  Parameters:

    data (:py:class:`numpy.ndarray`): An ``uint8`` array with 2 dimensions,
      corresponding to a gray-scale image loaded with Bob (y, x) ordering.

    bounding_box (:py:class:`bob.ip.facedetect.BoundingBox`): The bounding box
      in which the landmark detector will operate on


  Returns:

    :py:class:`menpo.shape.PointCloud`: A point-cloud in Menpo format, with the
      68 landmark points

  '''

  global LANDMARK_MODEL
  if LANDMARK_MODEL is None: #tries to load it
    import pkg_resources
    model_file = pkg_resources.resource_filename(__name__,
        os.path.join('data', 'keypoint_model.pkl.gz'))
    logging.debug('Loading Menpo landmark detector...')
    LANDMARK_MODEL = menpo.io.import_pickle(model_file)
    logging.debug('Loading Menpo landmark detector: OK')

  bounding_box_menpo = _bob_boundingbox_to_menpo(bounding_box)
  image_menpo = menpo.image.Image(data.astype('float64')/255.)

  return LANDMARK_MODEL.fit_from_bb(image_menpo, bounding_box_menpo)


_Result = collections.namedtuple('Result', 'bounding_box,quality,landmarks')

class Result(_Result):
  '''A :py:class:`collections.namedtuple` with landmark information

  Attributes:
    bounding_box (:py:class:`bob.ip.facedetect.BoundingBox`): A bounding box
      extracted with :py:mod:`bob.ip.facedetect`.

    quality (:py:class:`float`): the quality of the
      extracted bounding-box, as returned by :py:mod:`bob.ip.facedetect`'s
      Boosted classifier

    landmarks (:py:class:`numpy.ndarray`): A set of 68 points output
      by the menpofit landmark detector. The format of this output is a 2D
      :py:class:`numpy.ndarray` in which the first dimension encodes each point
      and the second, the point coordinates in the format (y, x). The 68 points
      are ordered in this way, from the menpo documentation:

      .. code-block:: python

         jaw_indices = [0, 17]
         lbrow_indices = [17, 22]
         rbrow_indices = [22, 27]
         upper_nose_indices = [27, 31]
         lower_nose_indices = [31, 36]
         leye_indices = [36, 42]
         reye_indices = [42, 48]
         outer_mouth_indices = [48, 60]
         inner_mouth_indices = [60, 68]

  '''
  pass


def _detect_multiple_landmarks_on_gray_image(data, top=0, min_quality=0.):
  '''Detects landmarks on a gray-scale image, returns point-clouds from menpo

  This helper will detect faces and landmarks, possibly many, on the input
  gray-scale image. It first detects faces in the input image, using
  :py:mod:`bob.ip.facedetect`, and then uses the result of the
  face-detection-step for detecting facial-landmarks.


  Parameters:

    data (:py:class:`numpy.ndarray`): An ``uint8`` array with 2 dimensions,
      corresponding to a gray-scale image loaded with Bob (y, x) ordering.

    top (:py:class:`int`): An integer which indicates if we should only
      consider the first N detections or all of them. A value of zero means the
      selector ignores this field. A value of 1 returns only the best detection
      (with the highest quality).

    min_quality (:py:class:`float`): Also trims the face detector output list
      by considering a minimum quality for the detection. A value of zero (0.0)
      means "any quality will do". Good detections have a typical value which
      is greater than 30. Use this parameter with care. If this and ``top`` are
      defined and non-zero, then ``top`` takes precedence.


  Returns:

    :py:class:`list`: A list of named tuples of type :py:class:`Result`,
      each containing the result of face detection and landmarks extracted from
      the input image.  The list MAY BE EMPTY if no face is detected in the
      input image (data).

  '''

  # detect the face location on the given image
  retval = []
  bounding_boxes = None
  qualities = None
  fdResult = bob.ip.facedetect.detect_all_faces(data)
  if fdResult is not None:
    bounding_boxes, qualities = fdResult
  else:
    return retval #return empty keypointset-list if no face-bounding-box was detected

  # filters bounding boxes according to priority and quality
  if top:
    bounding_boxes = bounding_boxes[:top]
    qualities = qualities[:top]

  bounding_boxes = [k for k,v in zip(bounding_boxes,qualities) \
      if v > min_quality]
  qualities = qualities[:len(bounding_boxes)]

  logger.info('Found %d valid face detection(s) (after filtering)',
      len(qualities))

  # runs the landmark detector and for, each face-bounding-box, adds the detected landmarks to the list retval.
  for k,(bb,qual) in enumerate(zip(bounding_boxes, qualities)):
    logger.debug('Detecting landmarks on bounding box %d/%d (quality=%g)...',
        k+1, len(qualities), qual)
    landmarks = _detect_landmarks_on_grayscale_image(data, bb)
    retval.append(Result(bb, qual, landmarks.final_shape.points))
  return retval


def detect_landmarks_on_boundingbox(data, bounding_box):
  '''Detects landmarks on a color or gray-scale image, returns them

  This function will detect landmarks on the input color or gray-scale image.

  Parameters:

    data (:py:class:`numpy.ndarray`): An ``uint8`` array with either 2 or 3
      dimensions, corresponding to a gray-scale or color image loaded with Bob
      (planes, y, x) ordering.

    bounding_box (:py:class:`bob.ip.facedetect.BoundingBox`): A bounding box
      extracted with :py:mod:`bob.ip.facedetect`.


  Returns:

    :py:class:`numpy.ndarray`: Containing the 68 detected landmarks around the
      bounding box provided as input. Notice this will detect landmarks if
      there is a face inside the bounding box or not. It is your task to make
      sure the bounding-box contains a valid face.

  '''

  if len(data.shape) == 3:
    data = bob.ip.color.rgb_to_gray(data)
  landmarks = _detect_landmarks_on_grayscale_image(data, bounding_box)
  return landmarks.final_shape.points


def _detect_multiple_landmarks_on_color_image(data, top=0, min_quality=0.):
  '''Detects landmarks on a color image, returns point-clouds from menpo

  This helper will detect faces and landmarks, possibly many, on the input
  color image.

  Parameters:

    data (:py:class:`numpy.ndarray`): An ``uint8`` array with 3 dimensions,
      corresponding to a color image loaded with Bob (planes, y, x) ordering.

    top (:py:class:`int`): An integer which indicates if we should only consider the first
      N detections or all of them. A value of zero means the selector ignores
      this field.

    min_quality (:py:class:`float`): also trims the face detector output list
      by considering a minimum quality for the detection. A value of zero (0.0)
      means "any quality will do". Good detections have a typical value which
      is greater than 30. Use this parameter with care. If this and ``top`` are
      defined and non-zero, then ``top`` takes precedence.


  Returns:

    :py:class:`list`: A list of named tuples of type :py:class:`Result`, each
      containing the result of face detection and landmarks extracted from the
      input image.

  '''

  return _detect_multiple_landmarks_on_gray_image(
      bob.ip.color.rgb_to_gray(data), top, min_quality)


def detect_landmarks(data, top=0, min_quality=0.):
  '''Detects landmarks on an image, returns point-clouds from menpo

  This helper will detect faces and landmarks, possibly many, on the input
  image.


  Parameters:

    data (:py:class:`numpy.ndarray`): An ``uint8`` array with either 2 or 3
      dimensions, corresponding to a either a gray-scale or color image loaded
      with Bob.

    top (:py:class:`int`): An integer which indicates if we should only
      consider the first N detections or all of them. A value of zero means the
      selector ignores this field.

    min_quality (:py:class:`float`): trims the face detector output list
      by considering a minimum quality for the detection. A value of zero (0.0)
      means "any quality will do". Good detections have a typical value which
      is greater than 30. Use this parameter with care. If this and ``top`` are
      defined and non-zero, then ``top`` takes precedence.


  Returns:

    :py:class:`list`: A list of named tuples of type :py:class:`Result`, each
      containing the result of face detection and landmarks extracted from the
      input image.

  '''

  if len(data.shape) == 2:
    return _detect_multiple_landmarks_on_gray_image(data, top, min_quality)
  else:
    return _detect_multiple_landmarks_on_color_image(data, top, min_quality)


def draw_landmarks(data, results):
  '''Draws bounding boxes and landmarks on the input image


  Parameters:

    data (:py:class:`numpy.ndarray`): An ``uint8`` array with either 2 or 3
      dimensions, corresponding to a either a gray-scale or color image loaded
      with Bob.

    results (:py:class:`list`): A list of named tuples of type
      :py:class:`Result`, each containing the result of face detection and
      landmarks extracted from the input image.

  '''

  if len(data.shape) == 2: #gray-scale
    bb_color = 255 #white
    pt_color = 255 #white
  else:
    bb_color = (0, 0, 255) #blue
    pt_color = (255, 0, 0) #red

  for r in results:
    bb_height = r.bounding_box.bottomright[0]-r.bounding_box.topleft[0]
    bb_width = r.bounding_box.bottomright[1]-r.bounding_box.topleft[1]
    bob.ip.draw.box(data, r.bounding_box.topleft, (bb_height, bb_width),
        bb_color)
    width = int(bb_width/50)
    for p in r.landmarks:
      bob.ip.draw.cross(data, p.astype('int'), width, pt_color)


def save_landmarks(results, fname):
  '''Saves landmarks to an HDF5 file

  This function will create an HDF5 file with the following structure::

    menpo_landmarks68: Dataset {68, 2} (float64)
    face_detector: {
      quality: float64,
      topleft_y: int32,
      topleft_x: int32,
      height: int32,
      width: int32,
    }

  The points inside the variable ``menpo_landmarks68`` are kept in the format
  ``(y, x)``.

  If there is more than a single detection on the input results, then the
  structure of the format is::

    menpo_landmarks68: Dataset {N, 68, 2} (float64)
    face_detector (Group): {
      quality: Dataset {N} (float64),
      topleft_y: Dataset {N} (int32),
      topleft_x: Dataset {N} (int32),
      height: Dataset {N} (int32),
      width: Dataset {N} (int32),
    }

  Where ``N`` corresponds to the number of entries in ``results``.

  In case the file exists already, then we'll try to create the entries defined
  above in case they don't exist yet on the said file.


  Parameters:

    results (:py:class:`list`): A list of named tuples of type
      :py:class:`Result`, each containing the result of face detection and
      landmarks extracted from the input image.

    fname (:py:class:`str`): A path with the output filename

  '''

  if os.path.exists(fname):
    logger.info("File `%s' already exists. Appending...", fname)
    h5f = bob.io.base.HDF5File(fname, 'a')
  else:
    logger.debug("Creating a new HDF5 file at `%s'...", fname)
    h5f = bob.io.base.HDF5File(fname, 'w')

  if len(results) == 1:
    if not h5f.has_group('face_detector'):
      # add it
      h5f.create_group('face_detector')
      h5f.set('/face_detector/quality', numpy.float64(results[0].quality))
      h5f.set('/face_detector/topleft_y',
          numpy.int32(results[0].bounding_box.topleft[0]))
      h5f.set('/face_detector/topleft_x',
          numpy.int32(results[0].bounding_box.topleft[1]))
      h5f.set('/face_detector/height',
          numpy.int32(results[0].bounding_box.size[0]))
      h5f.set('/face_detector/width',
          numpy.int32(results[0].bounding_box.size[1]))

    if not h5f.has_dataset('menpo_landmarks68'):
      h5f.set('/menpo_landmarks68', results[0].landmarks)

  else:
    if not h5f.has_group('face_detector'):
      # add it
      h5f.create_group('face_detector')
      h5f.set('/face_detector/quality',
          numpy.array([k.quality for k in results]).astype('float64'))
      h5f.set('/face_detector/topleft_y',
          numpy.array([k.bounding_box.topleft[0] \
              for k in results]).astype('int32'))
      h5f.set('/face_detector/topleft_x',
          numpy.array([k.bounding_box.topleft[1] \
              for k in results]).astype('int32'))
      h5f.set('/face_detector/height',
          numpy.array([k.bounding_box.size[0] \
              for k in results]).astype('int32'))
      h5f.set('/face_detector/width',
          numpy.array([k.bounding_box.size[1] \
              for k in results]).astype('int32'))

    if not h5f.has_dataset('menpo_landmarks68'):
      h5f.set('/menpo_landmarks68',
        numpy.array([k.landmarks for k in results]).astype('float64'))
