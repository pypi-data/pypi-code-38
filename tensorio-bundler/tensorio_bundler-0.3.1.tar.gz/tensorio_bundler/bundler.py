"""
TensorIO Bundler core functionality and CLI
"""

import argparse
import json
import os
import tempfile
import zipfile

import requests
import tensorflow as tf

TFLITE = 'tflite'
SAVED_MODEL = 'savedmodel'

class SavedModelDirMisspecificationError(Exception):
    """
    Raised in the process of a TFLite build if the SavedModel directory either does not
    exist or is not a directory.
    """
    pass

class TFLiteFileExistsError(Exception):
    """
    Raised in the process of a TFLite build if a file (or directory) already exists
    at the specified build path. """
    pass

class ZippedTIOBundleExistsError(Exception):
    """
    Raised in the process of a zipped tiobundle build if a file (or directory) already exists
    at the specified build path.
    """
    pass

class ZippedTIOBundleMisspecificationError(Exception):
    """
    Raised in the process of a zipped tiobundle build if one or more of:
    1. model.json
    2. tflite binary
    does not exist as a file.
    """
    pass

class TIOZipError(Exception):
    """
    Raised if there is an error in the zipping process when creating a TIOBundle.
    """
    pass

class TIOModelsRegistrationError(Exception):
    """
    Raised if there is an error registering a bundle against a TensorIO Models repository.
    """
    pass

class InvalidBundleSpecification(Exception):
    """
    Raised if the bundle specification (e.g. model.json) is invalid.
    """
    pass

def tflite_build_from_saved_model(saved_model_dir, outfile):
    """
    Builds TFLite binary from SavedModel directory

    Args:
    1. saved_model_dir - Directory containing SavedModel protobuf file and variables
    2. outfile - Path to which to write TFLite binary

    Returns: None
    """
    if tf.gfile.Exists(outfile):
        raise TFLiteFileExistsError(
            'ERROR: Specified TFLite binary path ({}) already exists'.format(outfile)
        )
    if not tf.gfile.Exists(saved_model_dir) or not tf.gfile.IsDirectory(saved_model_dir):
        raise SavedModelDirMisspecificationError(
            ('ERROR: Specified SavedModel directory ({}) either does not exist or is not a '
             'directory').format(saved_model_dir)
        )

    converter = tf.contrib.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    tflite_model = converter.convert()
    with tf.gfile.Open(outfile, 'wb') as outf:
        outf.write(tflite_model)

def tiobundle_build(model_path, model_json_path, assets_path, bundle_name, outfile):
    """
    Builds zipped tiobundle file (e.g. for direct download into Net Runner)

    Args:
    1. model_path - Path to TFLite binary or SavedModel directory
    2. model_json_path - Path to TensorIO-compatible model.json file
    3. assets_path - Path to TensorIO-compatible assets directory
    4. bundle_name - Name of the bundle
    5. outfile - Name under which the zipped tiobundle file should be stored

    Returns: outfile path if the zipped tiobundle was created successfully
    """
    if tf.gfile.Exists(outfile):
        raise ZippedTIOBundleExistsError(
            'ERROR: Specified zipped tiobundle output path ({}) already exists'.format(outfile)
        )

    if not tf.gfile.Exists(model_path):
        raise ZippedTIOBundleMisspecificationError(
            'ERROR: TFLite binary path ({}) does not exist'.format(
                model_path
            )
        )

    if not tf.gfile.Exists(model_json_path) or tf.gfile.IsDirectory(model_json_path):
        raise ZippedTIOBundleMisspecificationError(
            'ERROR: model.json path ({}) either does not exist or is not a file'.format(
                model_path
            )
        )

    _, temp_outfile = tempfile.mkstemp(suffix='.zip')
    with zipfile.ZipFile(temp_outfile, 'w') as tiobundle_zip:
        # We have to use the ZipFile writestr method because there is no guarantee that
        # all the files to be included in the archive are on the same filesystem that
        # the function is running on -- they could be on GCS.
        with tf.gfile.Open(model_json_path, 'rb') as model_json_file:
            model_json = model_json_file.read()
            model_json_string = model_json.decode('utf-8')
            bundle_spec = json.loads(model_json_string)
        tiobundle_zip.writestr(
            os.path.join(bundle_name, 'model.json'),
            model_json
        )

        model_spec = bundle_spec.get('model', {})
        if tf.gfile.IsDirectory(model_path):
            # We are bundling a SavedModel directory.
            # It goes into the train/ subdirectory of bundle
            model_dirname = model_spec.get('file')
            if model_dirname is None:
                raise InvalidBundleSpecification('No "file" specified under "model" key')
            saved_model_target = os.path.join(bundle_name, model_dirname)
            write_assets_to_zipfile(model_path, tiobundle_zip, saved_model_target)
        else:
            # We are bundling a tflite file.
            # We will store the tflite file under the model_filename specified in the model.json
            # If this is not specified, we store the file as "model.tflite"
            model_filename = model_spec.get('file', 'model.tflite')
            with tf.gfile.Open(model_path, 'rb') as tflite_file:
                tflite_model = tflite_file.read()
            tiobundle_zip.writestr(
                os.path.join(bundle_name, model_filename),
                tflite_model
            )

        if assets_path is not None:
            assets_zip_target = os.path.join(bundle_name, 'assets')
            write_assets_to_zipfile(assets_path, tiobundle_zip, assets_zip_target)

    tf.gfile.Copy(temp_outfile, outfile)
    os.remove(temp_outfile)

    return outfile

def write_assets_to_zipfile(assets_dir, zfile, zip_subdir):
    """
    Recursively writes the contents of assets directory into assets/ directory in zipfile.

    Raises a TIOZipError if there is an issue writing the assets from assets_dir into the zipfile
    at the given zip_subdir.

    Args:
    1. assets_dir - Local or GCS path to be written into zfile
    2. zfile - zipfile.ZipFile instance representing the zipfile into which assets should be
       written
    3. zip_subdir - Path in zipfile under which to write the assets at the given assets_dir

    Returns: None
    """
    assets = tf.gfile.Glob(os.path.join(assets_dir, '*'))
    # Will map asset subdirectories to their target zip subdirectories
    assets_subdirs = {}
    for asset in assets:
        asset_basename = os.path.basename(asset)
        if tf.gfile.IsDirectory(asset):
            # The zip subdirectory into which the asset subdirectory should be written is formed
            # by joining the current zip_subdir with the asset_basename
            zip_target = os.path.join(zip_subdir, asset_basename)
            assets_subdirs[asset] = zip_target
        else:
            zip_target = os.path.join(zip_subdir, asset_basename)
            try:
                with tf.gfile.Open(asset, 'rb') as asset_file:
                    asset_bytes = asset_file.read()
                zfile.writestr(zip_target, asset_bytes)
            except Exception as err:
                message = 'Error inserting {} into zipfile at {}: {}'.format(asset, zip_target, err)
                raise TIOZipError(message)

    for assets_subdir in assets_subdirs:
        write_assets_to_zipfile(assets_subdir, zfile, assets_subdirs[assets_subdir])

    return None

def register_bundle(bundle_path, resource_path):
    """
    Registeres bundle at the given path against a TensorIO Models repository at the given resource
    path.

    Args:
    1. bundle_path - path to TensorIO bundle (GCS ok)
    2. resource_path - Full checkpoint path at which bundle should be registered
       (e.g. /models/<modelName>/hyperparameters/<hyperparametersName>/checkpoints/<checkpointName>)

    Returns: Response text if the registration was successful, raises an error otherwise.
    """
    checkpoints, checkpoint_id = os.path.split(resource_path)
    if checkpoints == '' or checkpoint_id == '':
        raise TIOModelsRegistrationError('Invalid resource path: {}'.format(resource_path))

    repository_url = os.environ.get('REPOSITORY')
    if repository_url is None:
        # Should be in the form <host>[:<port>]/v1/repository
        raise TIOModelsRegistrationError('REPOSITORY environment variable not set')

    repository_api_key = os.environ.get('REPOSITORY_API_KEY')
    if repository_api_key is None:
        raise TIOModelsRegistrationError('REPOSITORY_API_KEY environment variable not set')

    gcs_prefix = 'gs://'
    if bundle_path[:len(gcs_prefix)] == gcs_prefix:
        link = 'https://storage.googleapis.com/{}'.format(bundle_path[len(gcs_prefix):])

    payload = {
        'checkpointId': checkpoint_id,
        'link': link
    }
    request_url = repository_url + checkpoints
    bearer_token = 'Bearer {}'.format(repository_api_key)
    headers = {'Authorization': bearer_token}
    response = requests.post(request_url, headers=headers, json=payload)
    return response.text

def generate_argument_parser():
    """
    Generates an argument parser for use with the TensorIO Bundler CLI; also used by bundlebot

    Args: None

    Returns: None
    """
    parser = argparse.ArgumentParser(description='Create tiobundles for use with TensorIO')

    parser.add_argument(
        '--build',
        required=True,
        choices={TFLITE, SAVED_MODEL},
        help='Specifies whether bundle is being built with tflite file or SavedModel binary.'
    )
    parser.add_argument(
        '--saved-model-dir',
        required=True,
        help='Path to directory containing SavedModel pb file and variables (GCS ok)'
    )
    parser.add_argument(
        '--tflite-model',
        required=False,
        help='Path to TFLite model (GCS allowed)'
    )
    parser.add_argument(
        '--model-json',
        required=True,
        help='Path to TensorIO model.json file'
    )
    parser.add_argument(
        '--assets-dir',
        required=False,
        help='Path to assets directory'
    )
    parser.add_argument( '--bundle-name',
        required=True,
        help='Name of tiobundle'
    )
    parser.add_argument(
        '--outfile',
        required=False,
        help='Path at which tiobundle zipfile should be created; defaults to <BUNDLE_NAME>.zip'
    )
    parser.add_argument(
        '--repository-path',
        required=False,
        default='',
        help=(
            '(Optional) TensorIO models repository resource path at which to save the bundle; the '
            'path should be of the form /models/<modelName>/hyperparameters/<hyperparametersName>/'
            'checkpoints/<checkpointName>; if specified, requires the REPOSITORY and '
            'REPOSITORY_API_KEY and environment variables to be set.'
        )
    )

    return parser


if __name__ == '__main__':
    parser = generate_argument_parser()
    args = parser.parse_args()
    model_path = args.saved_model_dir
    if args.build == TFLITE:
        if args.tflite_model is None:
            raise ValueError(
                '--tflite-model argument must be specified when --build={}'.format(TFLITE)
            )
        if tf.gfile.Exists(args.tflite_model):
            raise Exception('ERROR: TFLite model already exists - {}'.format(args.tflite_model))

        model_path = args.tflite_model

        print('Building TFLite model -')
        print('SavedModel directory: {}, TFLite model: {}'.format(
            args.saved_model_dir, args.tflite_model
        ))
        tflite_build_from_saved_model(args.saved_model_dir, args.tflite_model)

    tiobundle_zip = args.outfile
    if tiobundle_zip is None:
        tiobundle_zip = '{}.zip'.format(args.bundle_name)

    print('Building tiobundle -')
    print('model: {}, model.json: {}, assets directory: {}, bundle: {}, zipfile: {}'.format(
        model_path,
        args.model_json,
        args.assets_dir,
        args.bundle_name,
        tiobundle_zip
    ))
    bundle_path = tiobundle_build(
        model_path,
        args.model_json,
        args.assets_dir,
        args.bundle_name,
        tiobundle_zip
    )
    print('Bundle created: {}'.format(bundle_path))

    if args.repository_path != '':
        registration = register_bundle(bundle_path, args.repository_path)
        print('Bundle registered against repository: {}'.format(registration))

    print('Done!')
