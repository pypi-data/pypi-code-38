import os
import re
import logging
import subprocess

from pathlib import Path
from tempfile import TemporaryDirectory

import xml.etree.ElementTree as ET

import click
import dtoolcore

from parse import parse

from dtoolbioimage.derived_dataset import DerivedDataSet


def get_image_metadata_from_raw_image(raw_image_fpath):

    showinf_path = "showinf"
    showinf_args = ["-nocore", "-nopix", "-novalid", "-no-upgrade", "-omexml-only"]

    command = [showinf_path] + showinf_args + [raw_image_fpath]

    raw_output = subprocess.check_output(command)
    xml_string_output = raw_output.decode()
    image_metadata = image_metadata_from_xml(xml_string_output)

    return image_metadata


def image_metadata_from_xml(xml_metadata_string):

    root = ET.fromstring(xml_metadata_string)

    xml_namespace = list(root.attrib.values())[0].split()[0]

    def ns_element(name):
        return "{{{}}}{}".format(xml_namespace, name)

    metadata_by_image_name = {}
    for element in root.findall(ns_element("Image")):
        image_name = element.attrib['Name']
        pixels_element = element.find(ns_element("Pixels"))
        image_data = pixels_element.attrib
        metadata_by_image_name[image_name] = image_data

    return metadata_by_image_name


def simple_slugify(input_string):

    return re.sub('[ #]', '_', input_string)


def path_to_root_name(raw_path):

    basename = os.path.basename(raw_path)
    name, ext = os.path.splitext(basename)

    return simple_slugify(name)


def run_conversion(raw_image_fpath, root_name, output_dirpath, sep):

    bfconvert_path = "bfconvert"

    Path(output_dirpath).mkdir(exist_ok=True, parents=True)

    format_string = "{}{}%n{}S%s_T%t_C%c_Z%z.png".format(root_name, sep, sep)
    output_format_string = os.path.join(output_dirpath, format_string)
    command = [bfconvert_path, raw_image_fpath, output_format_string]
    subprocess.call(command)


def raw_image_idns(dataset):

    microscope_image_exts = ['.czi', '.lif']

    def is_microscope_image(idn):
        root, ext = os.path.splitext(dataset.item_properties(idn)['relpath'])
        return ext in microscope_image_exts

    return list(idn for idn in dataset.identifiers if is_microscope_image(idn))


def convert_and_stage(raw_image_fpath, root_name, staging_path, output_ds):

    sep = "-_-"
    run_conversion(raw_image_fpath, root_name, staging_path, sep)

    image_metadata_by_name = get_image_metadata_from_raw_image(raw_image_fpath)

    to_push = os.listdir(staging_path)
    n_items = len(to_push)
    for n, fn in enumerate(to_push, 1):
        root_name, series_name, descriptor = fn.rsplit(sep, maxsplit=2)
        S, T, C, Z = parse("S{}_T{}_C{}_Z{}.png", descriptor)
        plane_coords = {'S': S, 'T': T, 'C': C, 'Z': Z}

        item_fpath = os.path.join(staging_path, fn)
        item_relpath = "{}/{}/{}".format(root_name, series_name, descriptor)

        image_metadata = image_metadata_by_name[series_name]
        logging.info('Pushing {}/{}, {}'.format(n, n_items, item_relpath))
        output_ds.put_item(item_fpath, item_relpath)
        output_ds.add_item_metadata(item_relpath, "plane_coords", plane_coords)
        output_ds.add_item_metadata(item_relpath, "microscope_metadata", image_metadata)


def convert_single_idn(dataset, idn, output_ds):

    with TemporaryDirectory() as tempdir:
        relpath_name = dataset.item_properties(idn)['relpath']
        root_name = path_to_root_name(relpath_name)
        raw_image_fpath = dataset.item_content_abspath(idn)
        convert_and_stage(raw_image_fpath, root_name, tempdir, output_ds)


def raw_image_dataset_to_image_dataset(dataset, output_ds):

    microscope_image_idns = raw_image_idns(dataset)
    for idn in microscope_image_idns:
        logging.info('Converting {}'.format(idn))
        convert_single_idn(dataset, idn, output_ds)
    logging.info('Freezing')


@click.command()
@click.argument('dataset_uri')
@click.argument('output_base_uri')
@click.argument('output_name')
def cli(dataset_uri, output_base_uri, output_name):

    logging.basicConfig(level=logging.INFO)

    dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    with DerivedDataSet(output_base_uri, output_name, dataset, overwrite=True) as output_ds:
        output_ds.readme_dict['type'] = 'image_dataset'
        output_ds.readme_dict['converted_by'] = 'dtoolbioimage.convert'

        raw_image_dataset_to_image_dataset(dataset, output_ds)


if __name__ == '__main__':
    cli()  # NOQA
