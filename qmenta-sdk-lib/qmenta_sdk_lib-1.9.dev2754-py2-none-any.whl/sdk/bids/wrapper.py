import json
import logging
import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from qmenta.sdk.directory_utils import mkdirs, TemporaryDirectory


def tag_files(files):
    # TODO: improve tagging
    tfiles = []

    for f in files:
        tags = []

        # Modality
        if 'T1w' in f:
            tags.append('m:T1')
        elif 'T2w' in f:
            tags.append('m:T2')

        # Tags
        if 'brainmask' in f:
            tags.append('mask')
        elif 'labels' in f:
            tags.append('labels')
            if 'tissue_labels' in f:
                tags.append('tissue_segmentation')
        elif 'biasfield' in f:
            tags.append('bf')
        elif 'restore' in f:
            tags.append('bfc')
        elif 'anat2' in f or '2anat' in f:
            tags.append('warp')

        tfiles.append((f, tags))

    return tfiles


def generate_file_path(original_name, sub_name, modality_name, cat_dir):
    """
    Returns a valid BIDS name (full path) for the given file name.

    Parameters
    ----------
    original_name : str
        Original name of the file.
    sub_name : str
        QMENTA platform subject name (SUB-XXX_...).
    modality_name : str
        Modality string in the BIDS format (may be part of the name).
    cat_dir : str
        Path to the directory where the file will be stored.

    Returns
    -------
    str
        The full BIDS-compatible path where the file should be downloaded.
    """

    # Try to detect if the file name is already in BIDS format
    if original_name.startswith('sub-') and modality_name in original_name:

        # Use the original name (replacing the subject ID)
        target_name = '_'.join([sub_name] + original_name.split('_')[1:])

    else:

        # Automatically generate a BIDS compatible name for the file
        extension = '.' + '.'.join(original_name.split('.')[1:])
        if extension in ['.bval', '.bvec']:  # In BIDS, bval and bvec use dwi as modality
            target_name = '{}_dwi{}'.format(sub_name, extension)
        else:
            target_name = '{}_{}{}'.format(sub_name, modality_name, extension)

    return os.path.join(cat_dir, target_name)


def format_input_data(context, subject, session, path):
    """
    Format input data followings the BIDS specification: http://bids.neuroimaging.io/bids_spec.pdf

    :param context: AnalysisContext of the running analysis
    :param subject: Subject name (from analysis_data)
    :param session: Session ID (from analysis_data)
    :param path: Destination directory where the files will be placed

    TODO: support group analyses (multiple input containers).
    """

    logger = logging.getLogger(__name__)

    dataset_description = {
        'Name': 'QMENTA_ANALYSIS',
        'BIDSVersion': '1.1.0'
    }

    # The input container specification must include file filters following the bids_ff_names nomenclature
    bids_ff_names = {
        'anat': ['T1w', 'T2w', 'T1rho', 'T1map', 'T2map', 'T2star', 'FLAIR', 'FLASH',
                 'PD', 'PDmap', 'PDT2', 'inplaneT1', 'inplaneT2', 'angio'],
        'func': ['bold', 'events', 'physio', 'sbref'],
        'dwi': ['dwi', 'bval', 'bvec'],
        'fmap': ['phasediff, magnitude1']
    }

    supported_extensions = ['.nii', '.nii.gz', '.bval', '.bvec', '.tsv']

    # BIDS spec does not allow underscores or dashes
    sub_name = 'sub-{}'.format(subject.replace('-', '').replace('_', ''))
    sub_path = os.path.join(path, sub_name)
    mkdirs(sub_path)

    with open(os.path.join(path, 'dataset_description.json'), 'w') as fp:
        json.dump(dataset_description, fp)

    for category in list(bids_ff_names.keys()):
        for modality_name in bids_ff_names[category]:
            try:
                file_handlers = context.get_files(
                    'input', file_filter_condition_name='c_{}'.format(modality_name))
            except:  # noqa: E731,E123
                continue

            for fh in file_handlers:

                # NIFTI IS A MUST FOR BIDS
                if any([fh.name.endswith(ext) for ext in supported_extensions]):
                    cat_dir = os.path.join(sub_path, category)
                    mkdirs(cat_dir)

                    target_path = generate_file_path(
                        fh.name, subject, modality_name, cat_dir)

                    if os.path.isfile(target_path):
                        logger.warning(
                            'Multiple files with same name ({}). Only the first will be used'.format(
                                target_path)
                        )
                        break

                    with TemporaryDirectory() as tmp_dir:
                        download_path = fh.download(tmp_dir)
                        shutil.move(download_path, target_path)
                        logger.info('File: {}'.format(target_path))

                    metadata = fh.get_file_info()
                    if metadata:
                        metadata_target_name = '{}_{}{}'.format(
                            sub_name, modality_name, '.json')
                        metadata_target_path = os.path.join(
                            cat_dir, metadata_target_name)
                        with open(metadata_target_path, 'w') as fp:
                            json.dump(metadata, fp)
                else:
                    logger.warning('File {} extension not supported ({})'.format(
                        fh.name, supported_extensions))


def format_settings(settings):
    # Bypass from JSON schema
    # See docs.qmenta.com for more information

    # FIXME: Better define inputs, for now, we'll skip common settings
    ignore_param_list = ['input', 'age_months']

    options = []
    for param in settings:
        if param not in ignore_param_list:
            options += ['--' + param, str(settings[param])]
    return options


def run(context):
    logger = logging.getLogger(__name__)

    # Get information from the platform such as patient name, user_id, ssid...
    analysis_data = context.fetch_analysis_data()
    context.set_progress(message='Preparing data...')

    # Create in/out dirs
    input_path = '/analysis/input/'
    output_path = '/analysis/output/'
    mkdirs(input_path)
    mkdirs(output_path)

    # Download data from the platform and store following the BIDS specification
    format_input_data(
        context, subject=analysis_data['patient_secret_name'], session=analysis_data['ssid'], path=input_path
    )

    # Select type of analysis (TODO: add support for group analysis)
    analysis_type = 'participant'

    # Prepare a list of arguments from the settings
    options = format_settings(context.get_settings())

    # Run the original BIDS-APP entrypoint
    app_path = os.environ['BIDS_APP_ENTRYPOINT']
    context.set_progress(message='Running {}'.format(
        os.path.basename(app_path)))
    try:
        args = [app_path, input_path, output_path, analysis_type] + options
        logger.info('Calling: {}'.format(' '.join(args)))
        ret = check_output(args, stderr=STDOUT)
        logger.info(ret)
    except CalledProcessError as e:
        raise RuntimeError(
            'Program exited with error: {}\nOutput:\n{}'.format(e, e.output))
    except Exception:
        raise

    # Upload output files
    context.set_progress(message='Saving output...')
    output_files = []
    for dirpath, _, filenames in os.walk(output_path):
        for f in filenames:
            file_path = os.path.abspath(os.path.join(dirpath, f))
            output_files.append(file_path)

    for f, tags in tag_files(output_files):
        output_container_path = os.path.relpath(f, output_path)
        context.upload_file(f, output_container_path, tags=tags)
