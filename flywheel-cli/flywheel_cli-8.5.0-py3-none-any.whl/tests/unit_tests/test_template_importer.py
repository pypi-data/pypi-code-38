import collections

import fs
import pytest
import yaml

from flywheel_cli.importers import compile_regex, parse_template_string, parse_template_list, StringMatchNode, CompositeNode
from flywheel_cli.util import METADATA_EXPR

from flywheel_cli.importers import FolderImporter, StringMatchNode
from flywheel_cli.config import Config
from flywheel_cli.walker import PyFsWalker
from .test_container_factory import MockContainerResolver
from .test_folder_importer import mock_fs, make_config
from .test_template_string import project_pattern, subject_pattern, session_pattern

def make_importer(resolver, template='', **kwargs):
    assert template
    template_list = yaml.load(template)

    config = make_config(resolver)
    importer = FolderImporter(config=config, **kwargs)
    importer.root_node = parse_template_list(template_list, config)

    return importer

"""
archive/PROJECT_NAME/arc001/SESSION_ID/SCANS/SEQUENCE_NUMBER/DICOM|ASSOCIATED|STIM|PMU|PRESENTATION/

where PROJECT_NAME is the name of the Project/Study
SESSION_ID is the internal number which we assign to each Imaging session
SEQUENCE_NUMBER is the chronological order of the MRI Sequence
arc001 and SCANS remain constant throughout the archive.
"""
def test_parse_yaml_template():
    importer = make_importer(MockContainerResolver(), group='unsorted', template=r"""
    - pattern: archive
    - pattern: "{project}"
    - pattern: arc001
    - pattern: "{session}"
    - pattern: SCANS
    - pattern: (?P<acquisition>\d+)
    - select:
        - pattern: DICOM
          packfile_type: dicom
        - pattern: ASSOCIATED|STIM|PRESENTATION
        - pattern: .*
          ignore: true
    """, merge_subject_and_session=True)

    result = importer.root_node

    assert result
    assert result.template.pattern == 'archive'
    assert result.packfile_type == None

    result = result.next_node
    assert result
    assert result.template.pattern == project_pattern
    assert result.packfile_type == None

    result = result.next_node
    assert result
    assert result.template.pattern == 'arc001'
    assert result.packfile_type == None

    result = result.next_node
    assert result
    assert result.template.pattern == session_pattern
    assert result.packfile_type == None

    result = result.next_node
    assert result
    assert result.template.pattern == 'SCANS'
    assert result.packfile_type == None

    result = result.next_node
    assert result
    assert result.template.pattern == r'(?P<acquisition>\d+)'
    assert result.packfile_type == None

    result = result.next_node
    assert result
    assert len(result.children) == 3

    assert result.children[0].template.pattern == 'DICOM'
    assert result.children[0].packfile_type == 'dicom'

    assert result.children[1].template.pattern == 'ASSOCIATED|STIM|PRESENTATION'
    assert result.children[1].template.match('ASSOCIATED')
    assert result.children[1].template.match('STIM')
    assert result.children[1].template.match('PRESENTATION')
    assert not result.children[1].template.match('PMU')
    assert result.children[1].packfile_type == None

    assert result.children[2].template.pattern == '.*'
    assert result.children[2].packfile_type == None
    assert result.children[2].ignore

def test_yaml_template1():
    # Normal discovery
    mockfs = mock_fs(collections.OrderedDict({
        'archive/ASST_12345/arc001/001001/SCANS/110/DICOM': [
            '001.dcm',
            '002.dcm',
            '003.dcm'
        ],
        'archive/ASST_12345/arc001/001001/SCANS/110/PRESENTATION': [
            'rec_feedback.log'
        ],
        'archive/ASST_12345/arc001/001001/SCANS/110/ASSOCIATED': [
            'dti.bval', 'dti.bvec'
        ],
        'archive/ASST_12345/arc001/001001/SCANS/110/PMU': [
            'exclude.txt'
        ],
    }))

    resolver = MockContainerResolver()
    importer = make_importer(resolver, group='unsorted', template=r"""
    - pattern: archive
    - pattern: "{project}"
    - pattern: arc001
    - pattern: "{session}"
    - pattern: SCANS
    - pattern: (?P<acquisition>\d+)
    - select:
        - pattern: DICOM
          packfile_type: dicom
        - pattern: ASSOCIATED|STIM|PRESENTATION
        - pattern: .*
          ignore: true
    """, merge_subject_and_session=True)

    assert importer.merge_subject_and_session

    walker = PyFsWalker('mockfs://', src_fs=mockfs)
    importer.discover(walker)

    itr = iter(importer.container_factory.walk_containers())

    _, child = next(itr)
    assert child.container_type == 'group'
    assert child.id == 'unsorted'

    _, child = next(itr)
    assert child.container_type == 'project'
    assert child.label == 'ASST_12345'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == '001001'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == '001001'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == '110'

    assert len(child.files) == 3
    assert '/archive/ASST_12345/arc001/001001/SCANS/110/PRESENTATION/rec_feedback.log' in child.files
    assert '/archive/ASST_12345/arc001/001001/SCANS/110/ASSOCIATED/dti.bval' in child.files
    assert '/archive/ASST_12345/arc001/001001/SCANS/110/ASSOCIATED/dti.bvec' in child.files

    assert len(child.packfiles) == 1
    desc = child.packfiles[0]
    assert desc.packfile_type == 'dicom'
    assert desc.path == '/archive/ASST_12345/arc001/001001/SCANS/110/DICOM'
    assert desc.count == 3

    try:
        next(itr)
        pytest.fail('Unexpected container found')
    except StopIteration:
        pass

def test_slurp_scanner():
    resolver = MockContainerResolver()
    importer = make_importer(resolver, group='unsorted', project="POD", template=r"""
    - pattern: "{subject}&{session}"
      scan: slurp
    """)

    # Template check
    result = importer.root_node

    assert result
    assert result.template.pattern == '{}&{}'.format(subject_pattern, session_pattern)
    assert result.packfile_type == None

    # Discovery
    mockfs = mock_fs(collections.OrderedDict({
        '20030415_Scan_POD_S501_m1&2_0hr': [
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr.log',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.log',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.lst',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.lst.hdr',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.scn',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.scn.hdr',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.img',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.img.gz',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.img.hdr',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.log',
            'acf.mhdr',
            'acf_00.a.hdr',
            'acf_00.atn',
            'acf_00.atn.hdr',
            'README',
        ],
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1__s4jc_1_sct_QC_f0': [
            'log_e7_sino_09.txt',
            'scatter_qc_01.ps',
        ],
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]': [
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.CTrecon.log',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.cat',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.cat.hdr',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.ct.img',
            '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.ct.img.hdr',
        ],
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/scan': [
            'another-scan.img',
            'another-scan.img.hdr',
        ],
        '20030415_Scan_POD_S502_m1&2_0hr': [
            'README'
        ]
    }))

    walker = PyFsWalker('mockfs://', src_fs=mockfs)
    importer.discover(walker)
    itr = iter(importer.container_factory.walk_containers())

    _, child = next(itr)
    assert child.container_type == 'group'
    assert child.id == 'unsorted'

    _, child = next(itr)
    assert child.container_type == 'project'
    assert child.label == 'POD'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == '20030415_Scan_POD_S501_m1'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'subject'
    assert child.label == '20030415_Scan_POD_S502_m1'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == '2_0hr'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'session'
    assert child.label == '2_0hr'
    assert len(child.files) == 0

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == '20030415_Scan_POD_SCC1483_S501_m1&2_0hr'
    assert child.files == ['20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr.log']

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1'
    assert child.files == [
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.log',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.lst',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.lst.hdr',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.scn',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1.scn.hdr',
    ]

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1__s4jc_1_sct_QC_f0'
    assert child.files == [
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1__s4jc_1_sct_QC_f0/log_e7_sino_09.txt',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_v1__s4jc_1_sct_QC_f0/scatter_qc_01.ps',
    ]

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == '20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor'
    assert child.files == [
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.img',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.img.gz',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.img.hdr',
        '20030415_Scan_POD_S501_m1&2_0hr/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_124I_80M_em_vOSEM2D_scatcor.pet.log',
    ]

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'CTscan_[2017-06-09-09h-18m-28s]'
    assert child.files == [
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.CTrecon.log',
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.cat',
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.cat.hdr',
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.ct.img',
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/20030415_Scan_POD_SCC1483_S501_m1&2_0hr_v1.ct.img.hdr',
    ]

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'CTscan_[2017-06-09-09h-18m-28s]_scan'
    assert child.files == [
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/scan/another-scan.img',
        '20030415_Scan_POD_S501_m1&2_0hr/CTscan_[2017-06-09-09h-18m-28s]/scan/another-scan.img.hdr',
    ]

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'README'
    assert child.files == ['20030415_Scan_POD_S501_m1&2_0hr/README']

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'acf'
    assert child.files == ['20030415_Scan_POD_S501_m1&2_0hr/acf.mhdr']

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'acf_00'
    assert child.files == [
        '20030415_Scan_POD_S501_m1&2_0hr/acf_00.a.hdr',
        '20030415_Scan_POD_S501_m1&2_0hr/acf_00.atn',
        '20030415_Scan_POD_S501_m1&2_0hr/acf_00.atn.hdr',
    ]

    _, child = next(itr)
    assert child.container_type == 'acquisition'
    assert child.label == 'README'
    assert child.files == ['20030415_Scan_POD_S502_m1&2_0hr/README']

    try:
        next(itr)
        pytest.fail('Unexpected container found')
    except StopIteration:
        pass
