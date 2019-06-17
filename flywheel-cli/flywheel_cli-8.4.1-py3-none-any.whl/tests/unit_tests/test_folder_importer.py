import collections
import re

import fs
import pytest

from flywheel_cli.importers import FolderImporter, StringMatchNode
from flywheel_cli.config import Config
from flywheel_cli.walker import PyFsWalker
from .test_container_factory import MockContainerResolver

def mock_fs(structure):
    mockfs = fs.open_fs('mem://')

    for path, files in structure.items():
        with mockfs.makedirs(path, recreate=True) as subdir:
            for name in files:
                with subdir.open(name, 'w') as f:
                    f.write('Hello World!')

    return mockfs

def make_config(resolver):
    config = Config()
    config._resolver = resolver
    return config

def make_importer(resolver, group=None, project=None, no_subjects=False, no_sessions=False):
    importer = FolderImporter(group=group, project=project,
        merge_subject_and_session=(no_subjects or no_sessions), config=make_config(resolver))

    if not group:
        importer.add_template_node(StringMatchNode('group'))

    if not project:
        importer.add_template_node(StringMatchNode('project'))

    if not no_subjects:
        importer.add_template_node(StringMatchNode('subject'))

    if not no_sessions:
        importer.add_template_node(StringMatchNode('session'))

    importer.add_template_node(StringMatchNode('acquisition'))
    return importer

def test_folder_resolver_default():
    # Normal discovery
    mockfs = mock_fs(collections.OrderedDict({
        'scitran/Anxiety Study': [
            'InformedConsent_MRI.pdf', 'ScreeningForm_MRI.pdf'
        ],
        'scitran/Anxiety Study/anx_s1/ses1': [
            'FractionalAnisotropy_Single_Subject.csv', 'MeanDiffusivity_Single_Subject.csv'
        ],
        'scitran/Anxiety Study/anx_s1/ses1/T1_high-res_inplane_Ret_knk': [
            '8403_4_1_t1.dcm.zip'
        ],
        'scitran/Anxiety Study/anx_s1/ses1/fMRI_Ret_knk/dicom': [
            '001.dcm',
            '002.dcm',
            '003.dcm'
        ]
    }))

    resolver = MockContainerResolver()
    importer = make_importer(resolver)

    walker = PyFsWalker('mockfs://', src_fs=mockfs)
    importer.discover(walker)

    itr = iter(importer.container_factory.walk_containers())

    _, child = next(itr)
    assert child.container_type == 'group'
    assert child.id == 'scitran'

    _, child = next(itr)
    assert child.container_type == 'project'
    assert child.label == 'Anxiety Study'
    assert len(child.files) == 2
    assert '/scitran/Anxiety Study/InformedConsent_MRI.pdf' in child.files
    assert '/scitran/Anxiety Study/ScreeningForm_MRI.pdf' in child.files

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == 'anx_s1'

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == 'ses1'
    assert len(child.files) == 2
    assert '/scitran/Anxiety Study/anx_s1/ses1/FractionalAnisotropy_Single_Subject.csv' in child.files
    assert '/scitran/Anxiety Study/anx_s1/ses1/MeanDiffusivity_Single_Subject.csv' in child.files

    # Order is not guaranteed
    for i in range(2):
        _, child = next(itr)

        if child.label == 'T1_high-res_inplane_Ret_knk':
            assert child.container_type == 'acquisition'
            assert len(child.files) == 1
            assert '/scitran/Anxiety Study/anx_s1/ses1/T1_high-res_inplane_Ret_knk/8403_4_1_t1.dcm.zip' in child.files
        else:
            assert child.container_type == 'acquisition'
            assert child.label == 'fMRI_Ret_knk'
            assert len(child.files) == 0
            assert len(child.packfiles) == 1
            desc = child.packfiles[0]
            assert desc.packfile_type == 'dicom'
            assert desc.path == '/scitran/Anxiety Study/anx_s1/ses1/fMRI_Ret_knk/dicom'
            assert desc.count == 3

    try:
        next(itr)
        pytest.fail('Unexpected container found')
    except StopIteration:
        pass

def test_folder_resolver_group_and_project():
    # Normal discovery
    mockfs = mock_fs(collections.OrderedDict({
        '/': [
            'InformedConsent_MRI.pdf'
        ],
        'anx_s1/ses1/T1_high-res_inplane_Ret_knk': [
            '8403_4_1_t1.dcm.zip'
        ]
    }))

    resolver = MockContainerResolver()
    importer = make_importer(resolver, group='psychology', project='Anxiety Study')

    walker = PyFsWalker('mockfs://', src_fs=mockfs)
    importer.discover(walker)

    itr = iter(importer.container_factory.walk_containers())

    _, child = next(itr)
    assert child.container_type == 'group'
    assert child.id == 'psychology'

    _, child = next(itr)
    assert child.container_type == 'project'
    assert child.label == 'Anxiety Study'
    assert child.files == ['/InformedConsent_MRI.pdf']

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == 'anx_s1'

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == 'ses1'

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'T1_high-res_inplane_Ret_knk'
    assert child.files == ['/anx_s1/ses1/T1_high-res_inplane_Ret_knk/8403_4_1_t1.dcm.zip']

    try:
        next(itr)
        pytest.fail('Unexpected container found')
    except StopIteration:
        pass

def test_composite_packfiles():
    mockfs = mock_fs(collections.OrderedDict({
        'subject/session/pv5': [
            'file1.txt',
            'file2.txt'
        ],
        'subject/session/acquisition': [
            'file3.txt'
        ]
    }))

    resolver = MockContainerResolver()
    importer = FolderImporter(group='group', project='project', config=make_config(resolver))
    importer.add_template_node(StringMatchNode('subject'))
    importer.add_template_node(StringMatchNode('session'))

    importer.add_composite_template_node([
        StringMatchNode(re.compile('pv5'), packfile_type='pv5'),
        StringMatchNode('acquisition')
    ])

    walker = PyFsWalker('mockfs://', src_fs=mockfs)
    importer.discover(walker)

    itr = iter(importer.container_factory.walk_containers())

    _, child = next(itr)
    assert child.container_type == 'group'
    assert child.id == 'group'

    _, child = next(itr)
    assert child.container_type == 'project'
    assert child.label == 'project'

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == 'subject'

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == 'session'

    assert len(child.packfiles) == 1
    desc = child.packfiles[0]
    assert desc.packfile_type == 'pv5'
    assert desc.path == '/subject/session/pv5'
    assert desc.count == 2

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'acquisition'
    assert child.files == ['/subject/session/acquisition/file3.txt']

    try:
        next(itr)
        pytest.fail('Unexpected container found')
    except StopIteration:
        pass

def test_nested_packfiles():
    mockfs = mock_fs(collections.OrderedDict({
        'subject/session/pv5': [
            'file1.txt',
            'file2.txt'
        ],
        'subject/session/pv5/subdir': [
            'file3.txt',
            'file4.txt'
        ],
        'subject/session/acquisition': [
            'file5.txt'
        ],
        'subject/session/acquisition/dicom': [
            'file6.txt',
            'file7.txt'
        ],
        'subject/session/acquisition/dicom/subdir2': [
            'file8.txt'
        ]
    }))

    resolver = MockContainerResolver()
    importer = FolderImporter(group='group', project='project', config=make_config(resolver))
    importer.add_template_node(StringMatchNode('subject'))
    importer.add_template_node(StringMatchNode('session'))

    importer.add_composite_template_node([
        StringMatchNode(re.compile('pv5'), packfile_type='pv5'),
        StringMatchNode('acquisition')
    ])

    walker = PyFsWalker('mockfs://', src_fs=mockfs)
    importer.discover(walker)

    itr = iter(importer.container_factory.walk_containers())

    _, child = next(itr)
    assert child.container_type == 'group'
    assert child.id == 'group'

    _, child = next(itr)
    assert child.container_type == 'project'
    assert child.label == 'project'

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == 'subject'

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == 'session'

    assert len(child.packfiles) == 1
    desc = child.packfiles[0]
    assert desc.packfile_type == 'pv5'
    assert desc.path == '/subject/session/pv5'
    assert desc.count == 4

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'acquisition'
    assert child.files == ['/subject/session/acquisition/file5.txt']

    assert len(child.packfiles) == 1
    desc = child.packfiles[0]
    assert desc.packfile_type == 'dicom'
    assert desc.path == '/subject/session/acquisition/dicom'
    assert desc.count == 3

    try:
        next(itr)
        pytest.fail('Unexpected container found')
    except StopIteration:
        pass

