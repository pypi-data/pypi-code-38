from __future__ import print_function
import os
import re
import random
import logging
from shutil import copyfile
from pathlib import Path

import PIL
from lxml import etree
from eyewitness.config import (
    BBOX,
    BoundedBoxObject,
    DATASET_TRAIN_AND_VALID,
    DATASET_TEST_ONLY,
    DATASET_ALL,
)
from eyewitness.image_id import ImageId
from eyewitness.image_utils import Image
from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.models.feedback_models import FalseAlertFeedback
from eyewitness.models.detection_models import BboxDetectionResult
from eyewitness.utils import make_path

LOG = logging.getLogger(__name__)


def add_filename_prefix(filename, prefix):
    return "%s_%s" % (prefix, filename)


def create_bbox_dataset_from_eyewitness(
        database, valid_classes, output_dataset_folder, dataset_name):
    """
    generate bbox dataset from eyewitness requires:

    - FalseAlertFeedback table: remove images with false-alert feedback

    - BboxDetectionResult: get images with selected classes objects
    """
    anno_folder = str(Path(output_dataset_folder, 'Annotations'))
    jpg_images_folder = str(Path(output_dataset_folder, 'JPEGImages'))
    main_folder = str(Path(output_dataset_folder, 'ImageSets', 'Main'))

    # mkdir if not exist
    make_path(anno_folder)
    make_path(jpg_images_folder)
    make_path(main_folder)

    DATABASE_PROXY.initialize(database)
    # filter false alert, and valid_classes
    false_alert_query = FalseAlertFeedback.select(
        FalseAlertFeedback.image_id).where(FalseAlertFeedback.is_false_alert)
    valid_objects = BboxDetectionResult.select().where(
        BboxDetectionResult.image_id.not_in(false_alert_query),
        BboxDetectionResult.label.in_(valid_classes))

    # get valid_images with raw_image_path
    valid_images = set(i.image_id for i in valid_objects if i.image_id.raw_image_path)

    # generate etree obj for each images
    valid_image_count = 0
    for valid_image in valid_images:
        if (valid_image.file_format != 'jpg' or not os.path.exists(valid_image.raw_image_path)):
            # TODO: support other file_format
            continue

        ori_image_file = valid_image.raw_image_path
        dest_image_file = str(Path(jpg_images_folder, "%s.jpg" % valid_image.image_id))
        copyfile(ori_image_file, dest_image_file)

        # prepare anno_file
        anno_file = str(Path(anno_folder, "%s.xml" % valid_image.image_id))
        detected_objects = list(BboxDetectionResult.select().where(
            BboxDetectionResult.image_id == valid_image,
            BboxDetectionResult.label.in_(valid_classes)))
        if detected_objects:  # make sure there is detected objects
            etree_obj = generate_etree_obj(valid_image.image_id, detected_objects, dataset_name)
            etree_obj.write(anno_file, pretty_print=True)
            valid_image_count += 1
    LOG.info('create_bbox_dataset_from_eyewitness: output %s images', valid_image_count)


def generate_etree_obj(image_id, detected_objects, dataset_name):
    """
    Parameters
    ----------
    image_id: str
        image_id as filename
    detected_objects:
        detected_objects obj from detected_objects table
    dataset_name: str
        dataset_name
    """
    root = etree.Element("annotation")
    filename = etree.SubElement(root, "filename")
    source = etree.SubElement(root, "source")
    databases = etree.SubElement(source, "database")

    filename.text = image_id
    databases.text = dataset_name
    for obj in detected_objects:
        object_ = etree.SubElement(root, "object")
        name = etree.SubElement(object_, "name")
        name.text = obj.label
        pose = etree.SubElement(object_, "pose")
        pose.text = "Unspecified"
        truncated = etree.SubElement(object_, "truncated")
        truncated.text = "0"
        difficult = etree.SubElement(object_, "difficult")
        difficult.text = "0"
        # bounded box
        bndbox = etree.SubElement(object_, "bndbox")
        xmin_ = etree.SubElement(bndbox, "xmin")
        ymin_ = etree.SubElement(bndbox, "ymin")
        xmax_ = etree.SubElement(bndbox, "xmax")
        ymax_ = etree.SubElement(bndbox, "ymax")
        xmin_.text = str(obj.x1)
        ymin_.text = str(obj.y1)
        xmax_.text = str(obj.x2)
        ymax_.text = str(obj.y2)
    return etree.ElementTree(root)


def read_ori_anno_and_store_filered_result(
        ori_anno_file, dest_anno_file, filter_labels, remove_empty_labels_file):
    """
    read the original annotation file, filter objects with valid labels
    export to the dest_anno_file

    Parameters
    ----------
    ori_anno_file: str
        original annotation file
    dest_anno_file: str
        destination annotation file
    filter_labels: Optional[set[String]]
        filter the labels
    remove_empty_labels_file: bool
        remove the image if it don't have obj
    """
    etree_obj = etree.parse(ori_anno_file)
    for labeled_obj in etree_obj.findall('object'):
        label_name = labeled_obj.find('name').text
        if label_name not in filter_labels:
            labeled_obj.getparent().remove(labeled_obj)

    if remove_empty_labels_file:
        if not etree_obj.findall('object'):
            return
    etree_obj.write(dest_anno_file)


def copy_image_to_output_dataset(
        filename, src_dataset, jpg_images_folder, anno_folder, file_fp, filter_labels=None,
        remove_empty_labels_file=False):
    """
    move annotation, jpg file from src_dataset to file destination,
    add prefix to filename and print to id list file

    Parameters
    ----------
    filename: str
        ori filename
    src_dataset: BboxDataSet
        source dataset

    jpg_images_folder: str
        destination jpg file folder

    anno_folder: str
        destination annotation file folder

    file_fp:
        the file pointer used to export the id list

    filter_labels: Optional[set[String]]
        used for filtering label for the destination dataset
    """
    filename_with_prefix = add_filename_prefix(filename, src_dataset.dataset_name)

    # copy image file
    ori_image_file = str(Path(src_dataset.jpg_images_folder, "%s.jpg" % filename))
    dest_image_file = str(Path(jpg_images_folder, "%s.jpg" % filename_with_prefix))

    ori_anno_file = str(Path(src_dataset.anno_folder, "%s.xml" % filename))
    dest_anno_file = str(Path(anno_folder, "%s.xml" % filename_with_prefix))
    if filter_labels is None:
        # copy annotation file
        copyfile(ori_anno_file, dest_anno_file)
    else:
        read_ori_anno_and_store_filered_result(
            ori_anno_file, dest_anno_file, filter_labels, remove_empty_labels_file)

    # check annotation file were generated
    if os.path.exists(dest_anno_file):
        copyfile(ori_image_file, dest_image_file)
        # print filename to the filename list file
        print(filename_with_prefix, file=file_fp)


def parse_xml_obj(obj):
    label = obj.find('name').text
    x1 = int(obj.find('bndbox').find('xmin').text)
    y1 = int(obj.find('bndbox').find('ymin').text)
    x2 = int(obj.find('bndbox').find('xmax').text)
    y2 = int(obj.find('bndbox').find('ymax').text)
    return BoundedBoxObject(x1, y1, x2, y2, label, 1, '')


class BboxDataSet(object):
    """
    generate DataSet with same format as VOC object detections:

    <dataset_folder>/Annotations/<image_name>.xml

    <dataset_folder>/JPEGImages/<image_name>.jpg

    <dataset_folder>/ImageSets/Main/trainval.txt

    <dataset_folder>/ImageSets/Main/test.txt

    """
    def __init__(self, dataset_folder, dataset_name, valid_labels=None):
        self.dataset_folder = dataset_folder
        self.anno_folder = str(Path(dataset_folder, 'Annotations'))
        self.jpg_images_folder = str(Path(dataset_folder, 'JPEGImages'))
        self.main_folder = str(Path(dataset_folder, 'ImageSets', 'Main'))
        self.trainval_file = str(Path(self.main_folder, 'trainval.txt'))
        self.test_file = str(Path(self.main_folder, 'test.txt'))
        self.dataset_name = dataset_name
        self._valid_labels = valid_labels

    @property
    def dataset_type(self):
        return BBOX

    @property
    def valid_labels(self):
        """
        the valid_labels in the dataset
        """
        if self._valid_labels is None:
            self._valid_labels = self.get_valid_labels()
        assert len(self._valid_labels) > 0
        return self._valid_labels

    @property
    def training_and_validation_set(self):
        with open(self.trainval_file) as f:
            for i in f:
                yield i.strip()

    @property
    def testing_set(self):
        with open(self.test_file) as f:
            for i in f:
                yield i.strip()

    def generate_train_test_list(self, overwrite=True, train_ratio=0.9):
        """generate train and test list

        Parameters
        ----------
            overwrite: bool
                if overwrite and file not exit will regenerate the train, test list
            train_ratio: float
                the ratio used to sample train, test list, should between 0~1
        """
        if not overwrite and os.path.exists(self.trainval_file) and os.path.exists(self.test_file):
            return
        else:
            anno_files = Path(self.anno_folder).glob('*.xml')
            anno_regex = re.compile(str(Path(self.anno_folder, '(?P<image_id>.*).xml')))
            image_ids_anno = set(
                anno_regex.match(str(anno_file)).group('image_id') for anno_file in anno_files)

            jpg_files = Path(self.jpg_images_folder).glob('*.jpg')
            jpg_regex = re.compile(str(Path(self.jpg_images_folder, '(?P<image_id>.*).jpg')))
            image_ids_jpg = set(
                jpg_regex.match(str(jpg_file)).group('image_id') for jpg_file in jpg_files)
            image_ids = image_ids_jpg.intersection(image_ids_anno)

            # write to training set
            training_set = random.sample(image_ids, int(len(image_ids) * train_ratio))
            with open(self.trainval_file, 'w') as f:
                for train_id in training_set:
                    print(train_id, file=f)

            testing_set = image_ids.difference(training_set)
            with open(self.test_file, 'w') as f:
                for test_id in testing_set:
                    print(test_id, file=f)

    def get_valid_labels(self):
        valid_labels = set()
        xml_files = Path(self.anno_folder).glob('*.xml')
        for xml_file in xml_files:
            x = etree.parse(str(xml_file))
            gt_objects = x.findall('object')
            labels = [parse_xml_obj(gt_object).label for gt_object in gt_objects]
            valid_labels.update(labels)
        return valid_labels

    def get_selected_images(self, mode=DATASET_TEST_ONLY):
        if mode == DATASET_TRAIN_AND_VALID:
            selected_images = list(self.training_and_validation_set)
        elif mode == DATASET_TEST_ONLY:
            selected_images = list(self.testing_set)
        elif mode == DATASET_ALL:
            selected_images = list(self.training_and_validation_set)
            selected_images.extend(self.testing_set)
        else:
            raise Exception('unknown dataset mode')
        return selected_images

    def image_obj_iterator(self, selected_images):
        """
        generate eyewitness Image obj from dataset

        Parameters
        ----------
        mode: str
            the mode to iterate the dataset

        Returns
        -------
        image_obj_generator: Generator[eyewitness.image_utils.Image]
            eyewitness Image obj generator
        """
        for selected_image in selected_images:
            # TODO: design better representation for ImageId
            image_id = ImageId.from_str(selected_image)
            jpg_file = str(Path(self.jpg_images_folder, '%s.jpg' % selected_image))
            yield Image(image_id, raw_image_path=jpg_file)

    def ground_truth_iterator(self, selected_images):
        """
        ground_truth interator

        Parameters
        ----------
        mode: str
            the mode to iterate the dataset

        Returns
        -------
        gt_object_generator: Generator[(ImageId, List[BoundedBoxObject])]
            ground_truth_object generator, with first item if the ImageId
        """
        for selected_image in selected_images:
            # TODO: design better representation for ImageId
            xml_file = str(Path(self.anno_folder, '%s.xml' % (selected_image)))
            x = etree.parse(xml_file)
            gt_objects = [parse_xml_obj(gt_object) for gt_object in x.findall('object')]
            yield gt_objects

    def dataset_iterator(self, with_gt_objs=True, mode=DATASET_TEST_ONLY):
        selected_images = self.get_selected_images(mode)
        img_generator = self.image_obj_iterator(selected_images)
        if with_gt_objs:
            gt_generator = self.ground_truth_iterator(selected_images)
            for img_tuples in zip(img_generator, gt_generator):
                yield img_tuples
        else:
            for img in img_generator:
                yield img

    @classmethod
    def union_bbox_datasets(cls, datasets, output_dataset_folder, dataset_name,
                            filter_labels=None, remove_empty_labels_file=False):
        """
        union bbox datasets and copy files to the given output_dataset
        """
        assert all(dataset.dataset_type == BBOX for dataset in datasets)

        anno_folder = str(Path(output_dataset_folder, 'Annotations'))
        jpg_images_folder = str(Path(output_dataset_folder, 'JPEGImages'))
        main_folder = str(Path(output_dataset_folder, 'ImageSets', 'Main'))

        # mkdir if not exist
        make_path(anno_folder)
        make_path(jpg_images_folder)
        make_path(main_folder)

        # write train, test list out
        trainval_file = str(Path(main_folder, 'trainval.txt'))
        test_file = str(Path(main_folder, 'test.txt'))
        with open(trainval_file, 'w') as train_fp, open(test_file, 'w') as test_fp:
            for dataset in datasets:
                for train_file in dataset.training_and_validation_set:
                    copy_image_to_output_dataset(
                        train_file, dataset, jpg_images_folder, anno_folder, train_fp,
                        filter_labels, remove_empty_labels_file)

                for test_file in dataset.testing_set:
                    copy_image_to_output_dataset(
                        test_file, dataset, jpg_images_folder, anno_folder, test_fp,
                        filter_labels, remove_empty_labels_file)

        return cls(output_dataset_folder, dataset_name)

    def convert_into_darknet_format(self):
        darknet_anno_folder = Path(self.dataset_folder, 'Darknet_annotation')
        make_path(str(darknet_anno_folder))
        sorted_valid_labels = sorted(self.get_valid_labels())

        n_classes = len(sorted_valid_labels)
        label2idx = {label: idx for idx, label in enumerate(sorted_valid_labels)}
        label_name_file = str(darknet_anno_folder / 'label.names')
        with open(label_name_file, 'w') as f:
            for valid_label in sorted_valid_labels:
                print(valid_label, file=f)

        images_dir = darknet_anno_folder / 'images'
        make_path(str(images_dir))
        labels_dir = darknet_anno_folder / 'labels'
        make_path(str(labels_dir))

        training_set_file = str(darknet_anno_folder / 'training_set.txt')
        LOG.info('generating darknet training dataset: %s ', training_set_file)
        self.store_and_convert_darknet_bbox_tuples(
            training_set_file, self.training_and_validation_set, images_dir, labels_dir, label2idx)

        testing_set_file = str(darknet_anno_folder / 'testing_set.txt')
        LOG.info('generating darknet testing dataset: %s ', training_set_file)
        self.store_and_convert_darknet_bbox_tuples(
            testing_set_file, self.testing_set, images_dir, labels_dir, label2idx)

        dataset_cfg = {
            'classes': n_classes,
            'names': label_name_file,
            'train': training_set_file,
            'valid': testing_set_file,
        }
        dataset_cfg_file = str(darknet_anno_folder / 'config.data')
        with open(dataset_cfg_file, 'w') as f:
            for key, value in dataset_cfg.items():
                print('{key}={value}'.format(key=key, value=value), file=f)

    def store_and_convert_darknet_bbox_tuples(
            self, dataset_file, selected_images, images_dir, labels_dir, label2idx,
            logging_frequency=100):
        processed_image_count = 0
        with open(dataset_file, 'w') as f:
            for img_id in selected_images:
                processed_image_count += 1
                if processed_image_count % logging_frequency == 0:
                    LOG.info('processed images: %d', processed_image_count)

                img_file_name = "%s.jpg" % img_id
                anno_file_name = "%s.xml" % img_id
                darknet_label_file_name = "%s.txt" % img_id
                ori_image_file = Path(self.jpg_images_folder, img_file_name)
                ori_anno_file = Path(self.anno_folder, anno_file_name)
                if not (ori_image_file.exists() and ori_anno_file.exists()):
                    continue
                # move image to destination folder
                dest_image_file = images_dir / img_file_name
                dest_label_file = labels_dir / darknet_label_file_name
                copyfile(str(ori_image_file), str(dest_image_file))
                print(str(dest_image_file), file=f)

                # wirte annotation file
                gt_objects = [parse_xml_obj(gt_object) for gt_object in
                              etree.parse(str(ori_anno_file)).findall('object')]
                img_width, img_height = PIL.Image.open(str(ori_image_file)).size

                with open(str(dest_label_file), 'w') as lf:
                    for gt_object in gt_objects:
                        label_idx = label2idx[gt_object.label]
                        x_center = (gt_object.x1 + gt_object.x2) / 2 / img_width
                        y_center = (gt_object.y1 + gt_object.y2) / 2 / img_height
                        width = (gt_object.x2 - gt_object.x1) / img_width
                        height = (gt_object.y2 - gt_object.y1) / img_height
                        str_tuple = (str(i) for i in
                                     [label_idx, x_center, y_center, width, height])
                        print(' '.join(str_tuple), file=lf)
