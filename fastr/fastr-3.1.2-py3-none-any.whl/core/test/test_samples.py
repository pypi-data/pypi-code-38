# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pickle
from collections import OrderedDict, namedtuple

import pytest

import fastr
from fastr.core.samples import SampleId, SampleIndex, SampleItem
from fastr import exceptions

String = fastr.types['String']


@pytest.fixture(scope="module")
def sample_data():
    data_container = namedtuple('DataContainer', [
        'sample_id_0',
        'sample_id_1',
        'sample_id_2',
        'sampleindex_0',
        'sampleindex_1',
        'sampleindex_2',
        'sampleindex_3',
        'sampleindex_4',
        'sampleindex_5',
        'sampleindex_6',
        'sampleindex_7',
        'sampleindex_8',
        'sample_item_0',
        'sample_item_1',
        'sample_item_2',
    ])

    sample_id_0 = SampleId('single')
    sample_id_1 = SampleId('test', '123', 'test')
    sampleindex_0 = SampleIndex(0)
    sampleindex_1 = SampleIndex(42, 4, 2)

    return data_container(
        sample_id_0,
        sample_id_1,
        SampleId(['built', 'from', 'list']),
        sampleindex_0,
        sampleindex_1,
        SampleIndex([5, 3, 8]),
        SampleIndex(range(3)),  # Create index from iterator
        SampleIndex(0, slice(3, 5)),
        SampleIndex(slice(1, 6, 2), 3),
        SampleIndex(slice(None, None, 2)),
        SampleIndex(slice(None, 9, 3)),
        SampleIndex(slice(None, 5, 2), slice(1, 4)),
        SampleItem(sampleindex_0, sample_id_0, OrderedDict(), None),
        SampleItem(sampleindex_1, sample_id_1, OrderedDict({0: (String('val1'), String('val2'))}), set()),
        SampleItem((0, 1), ('a', 'b'), OrderedDict({0: (String('val1'), String('val2'))}), set()),
    )


def test_failed_sample_default(sample_data):
    assert sample_data.sample_item_0.failed_annotations == set()


def test_failed_sample_add_failure(sample_data):
    sample_item = SampleItem(sample_data.sampleindex_0, sample_data.sample_id_0, OrderedDict(), None, set())
    sample_item.failed_annotations.add(('job_0', "because of what?"))
    assert sample_item.failed_annotations == {('job_0', "because of what?")}


def test_failed_sample_add_multiple_failures(sample_data):
    sample_item = SampleItem(sample_data.sampleindex_0, sample_data.sample_id_0, OrderedDict(), None, set())
    sample_item.failed_annotations.add(('job_0', "because of what?"))
    sample_item.failed_annotations.add(('job_1', "because of that"))
    assert sample_item.failed_annotations == {('job_0', "because of what?"), ('job_1', "because of that")}


def test_failed_sample_add_wrong_type():
    with pytest.raises(exceptions.FastrTypeError):
        sample_item = SampleItem((0, 1), ('a', 'b'), OrderedDict({0: (String('val1'), String('val2'))}), set(), "blaat")


def test_sample_id_str(sample_data):
    assert str(sample_data.sample_id_0) == 'single'
    assert str(sample_data.sample_id_1) == 'test__123__test'
    assert str(sample_data.sample_id_2) == 'built__from__list'


def test_sampleid_noniter():
    with pytest.raises(exceptions.FastrTypeError):
        SampleId(None)


def test_sampleindex_empty():
    with pytest.raises(exceptions.FastrValueError):
        SampleIndex()


def test_sampleindex_emptylist():
    with pytest.raises(exceptions.FastrValueError):
        SampleIndex([])


def test_sampleindex_noniter():
    with pytest.raises(exceptions.FastrTypeError):
        SampleIndex(None)


def test_sampleindex_wrongtype1():
    with pytest.raises(exceptions.FastrTypeError):
        SampleIndex('test')


def test_sampleindex_wrongtype2():
    with pytest.raises(exceptions.FastrTypeError):
        SampleIndex(['test', 1, 2, 3])


def test_sampleindex_wrongtype3():
    with pytest.raises(exceptions.FastrTypeError):
        SampleIndex(1.0, 2.0)


def test_sampleindex_str(sample_data):
    assert str(sample_data.sampleindex_0) == '(0)'
    assert str(sample_data.sampleindex_1) == '(42, 4, 2)'
    assert str(sample_data.sampleindex_2) == '(5, 3, 8)'
    assert str(sample_data.sampleindex_3) == '(0, 1, 2)'
    assert str(sample_data.sampleindex_4) == '(0, 3:5)'
    assert str(sample_data.sampleindex_5) == '(1:6:2, 3)'
    assert str(sample_data.sampleindex_6) == '(::2)'
    assert str(sample_data.sampleindex_7) == '(:9:3)'
    assert str(sample_data.sampleindex_8) == '(:5:2, 1:4)'


def test_sampleindex_repr(sample_data):
    assert repr(sample_data.sampleindex_0) == '<SampleIndex (0)>'
    assert repr(sample_data.sampleindex_1) == '<SampleIndex (42, 4, 2)>'
    assert repr(sample_data.sampleindex_2) == '<SampleIndex (5, 3, 8)>'
    assert repr(sample_data.sampleindex_3) == '<SampleIndex (0, 1, 2)>'
    assert repr(sample_data.sampleindex_4) == '<SampleIndex (0, 3:5)>'
    assert repr(sample_data.sampleindex_5) == '<SampleIndex (1:6:2, 3)>'
    assert repr(sample_data.sampleindex_6) == '<SampleIndex (::2)>'
    assert repr(sample_data.sampleindex_7) == '<SampleIndex (:9:3)>'
    assert repr(sample_data.sampleindex_8) == '<SampleIndex (:5:2, 1:4)>'


def test_sampleindex_isslice(sample_data):
    assert not sample_data.sampleindex_0.isslice
    assert not sample_data.sampleindex_1.isslice
    assert not sample_data.sampleindex_2.isslice
    assert not sample_data.sampleindex_3.isslice
    assert sample_data.sampleindex_4.isslice
    assert sample_data.sampleindex_5.isslice
    assert sample_data.sampleindex_6.isslice
    assert sample_data.sampleindex_7.isslice
    assert sample_data.sampleindex_8.isslice


def test_sampleindex_expand_wrong_dim(sample_data):
    with pytest.raises(exceptions.FastrValueError):
        sample_data.sampleindex_8.expand((10, 8, 9))


def test_sampleindex_expand(sample_data):
    # No expand used
    assert sample_data.sampleindex_0.expand((10,)) == SampleIndex(0)

    # Check various expands
    assert sample_data.sampleindex_4.expand((6, 8,)) == (SampleIndex(0, 3),
                                                         SampleIndex(0, 4))
    assert sample_data.sampleindex_5.expand((8, 5)) == (SampleIndex(1, 3),
                                                        SampleIndex(3, 3),
                                                        SampleIndex(5, 3))
    assert sample_data.sampleindex_6.expand((5,)) == (SampleIndex(0),
                                                      SampleIndex(2),
                                                      SampleIndex(4))
    assert sample_data.sampleindex_6.expand((6,)) == (SampleIndex(0),
                                                      SampleIndex(2),
                                                      SampleIndex(4))
    assert sample_data.sampleindex_6.expand((7,)) == (SampleIndex(0),
                                                      SampleIndex(2),
                                                      SampleIndex(4),
                                                      SampleIndex(6))
    assert sample_data.sampleindex_8.expand((7, 6)) == (SampleIndex(0, 1),
                                                        SampleIndex(0, 2),
                                                        SampleIndex(0, 3),
                                                        SampleIndex(2, 1),
                                                        SampleIndex(2, 2),
                                                        SampleIndex(2, 3),
                                                        SampleIndex(4, 1),
                                                        SampleIndex(4, 2),
                                                        SampleIndex(4, 3))


def test_sampleindex_add(sample_data):
    # Add sample index
    assert sample_data.sampleindex_0 + sample_data.sampleindex_1 == SampleIndex(0, 42, 4, 2)
    assert sample_data.sampleindex_2 + sample_data.sampleindex_6 == SampleIndex(5, 3, 8, slice(None, None, 2))

    # Add element
    assert sample_data.sampleindex_0 + 5 == SampleIndex(0, 5)
    assert sample_data.sampleindex_0 + slice(1, 4) == SampleIndex(0, slice(1, 4))

    # Add tuple
    assert sample_data.sampleindex_0 + (4, 5) == SampleIndex(0, 4, 5)


def test_sampleindex_add_wrong_type(sample_data):
    with pytest.raises(TypeError):
        sample_data.sampleindex_0 + 1.0


def test_sampleindex_add_wrong_type2(sample_data):
    with pytest.raises(exceptions.FastrTypeError):
        sample_data.sampleindex_0 + (1.0, 2.0)


def test_sampleindex_radd(sample_data):
    # Radd element
    assert 4 + sample_data.sampleindex_0 == SampleIndex(4, 0)
    assert slice(4, 8) + sample_data.sampleindex_1 == SampleIndex(slice(4, 8), 42, 4, 2)

    # Add tuple
    assert (1, 2) + sample_data.sampleindex_0 == SampleIndex(1, 2, 0)
    assert (slice(None, 3), 1) + sample_data.sampleindex_2 == SampleIndex(slice(None, 3), 1, 5, 3, 8)


def test_sampleindex_radd_wrong_type(sample_data):
    with pytest.raises(TypeError):
        1.0 + sample_data.sampleindex_0


def test_sampleindex_radd_wrong_type2(sample_data):
    with pytest.raises(exceptions.FastrTypeError):
        (1.0, 2.0) + sample_data.sampleindex_0


def test_sampleitem_wrong_jobs_type():
    with pytest.raises(exceptions.FastrTypeError):
        SampleItem((0, 1), ('a', 'b'), {0: ('val1', 'val2')}, dict())


def test_sampleitem_repr(sample_data):
    assert repr(sample_data.sample_item_0) == '<SampleItem index=(0), id=single>'
    assert repr(sample_data.sample_item_1) == '<SampleItem index=(42, 4, 2), id=test__123__test>'


def test_sampleitem_pickle(sample_data):
    assert sample_data.sample_item_0 == pickle.loads(pickle.dumps(sample_data.sample_item_0))
    assert sample_data.sample_item_1 == pickle.loads(pickle.dumps(sample_data.sample_item_1))
    assert sample_data.sample_item_2 == pickle.loads(pickle.dumps(sample_data.sample_item_2))
    assert sample_data.sample_item_0 != pickle.loads(pickle.dumps(sample_data.sample_item_1))
    assert sample_data.sample_item_0 != pickle.loads(pickle.dumps(sample_data.sample_item_2))
    assert sample_data.sample_item_1 != pickle.loads(pickle.dumps(sample_data.sample_item_2))


def test_sampleitem_newargs(sample_data):
    assert sample_data.sample_item_0.__getnewargs__() == (sample_data.sampleindex_0, sample_data.sample_id_0, OrderedDict(), set(), set())
    assert sample_data.sample_item_1.__getnewargs__() == (sample_data.sampleindex_1, sample_data.sample_id_1, OrderedDict({0: (String('val1'), String('val2'))}), set(), set())
    assert sample_data.sample_item_2.__getnewargs__() == (SampleIndex(0, 1), SampleId('a', 'b'), OrderedDict({0: (String('val1'), String('val2'))}), set(), set())


def test_sampleitem_data(sample_data):
    assert sample_data.sample_item_0.data == OrderedDict()
    assert sample_data.sample_item_1.data == OrderedDict({0: (String('val1'), String('val2'))})
    assert sample_data.sample_item_2.data == OrderedDict({0: (String('val1'), String('val2'))})
