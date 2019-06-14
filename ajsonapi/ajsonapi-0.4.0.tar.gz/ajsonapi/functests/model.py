# Copyright © 2018-2019 Roel van der Goot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Module model specifies the object model used in the functional tests."""

from ajsonapi import (
    JSON_API,
    Attribute,
    Int64,
    ManyToManyRelationship,
    ManyToOneRelationship,
    OneToManyRelationship,
    OneToOneLocalRelationship,
    OneToOneRemoteRelationship,
    String,
)


class Centers(JSON_API):
    """Class under test."""
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_local = OneToOneLocalRelationship('OneOneLocals',
                                              lfkey='one_one_local_id')
    one_one_remote = OneToOneRemoteRelationship('OneOneRemotes',
                                                rfkey='center_id')
    one_manys = OneToManyRelationship('OneManys', rfkey='center_id')
    many_one = ManyToOneRelationship('ManyOnes', lfkey='many_one_id')
    many_manys = ManyToManyRelationship('ManyManys',
                                        'CentersManyManys',
                                        lafkey='center_id',
                                        rafkey='many_many_id')


class OneOneLocals(JSON_API):
    """Resource objects that are associated from class Center through a
    one-to-one relationship with a local foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    center = OneToOneRemoteRelationship('Centers', rfkey='one_one_local_id')
    ool_one_one_local = OneToOneLocalRelationship('OOLOneOneLocals',
                                                  lfkey='ool_one_one_local_id')
    ool_one_one_remote = OneToOneRemoteRelationship('OOLOneOneRemotes',
                                                    rfkey='one_one_local_id')
    ool_many_one = ManyToOneRelationship('OOLManyOnes', lfkey='ool_many_one_id')
    ool_one_manys = OneToManyRelationship('OOLOneManys',
                                          rfkey='one_one_local_id')
    ool_many_manys = ManyToManyRelationship('OOLManyManys',
                                            'OneOneLocalsOOLManyManys',
                                            lafkey='one_one_local_id',
                                            rafkey='ool_many_many_id')


class OneOneRemotes(JSON_API):
    """Resource objects that are associated from class Center through a
    one-to-one relationship with a remote foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    center = OneToOneLocalRelationship('Centers', lfkey='center_id')
    oor_one_one_local = OneToOneLocalRelationship('OOROneOneLocals',
                                                  lfkey='oor_one_one_local_id')
    oor_one_one_remote = OneToOneRemoteRelationship('OOROneOneRemotes',
                                                    rfkey='one_one_remote_id')
    oor_many_one = ManyToOneRelationship('OORManyOnes', lfkey='oor_many_one_id')
    oor_one_manys = OneToManyRelationship('OOROneManys',
                                          rfkey='one_one_remote_id')
    oor_many_manys = ManyToManyRelationship('OORManyManys',
                                            'OneOneRemotesOORManyManys',
                                            lafkey='one_one_remote_id',
                                            rafkey='oor_many_many_id')


class OneManys(JSON_API):
    """Resource objects that are associated from class Center through a
    one-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    center = ManyToOneRelationship('Centers', lfkey='center_id')
    om_one_one_local = OneToOneLocalRelationship('OMOneOneLocals',
                                                 lfkey='om_one_one_local_id')
    om_one_one_remote = OneToOneRemoteRelationship('OMOneOneRemotes',
                                                   rfkey='one_many_id')
    om_many_one = ManyToOneRelationship('OMManyOnes', lfkey='om_many_one_id')
    om_one_manys = OneToManyRelationship('OMOneManys', rfkey='one_many_id')
    om_many_manys = ManyToManyRelationship('OMManyManys',
                                           'OneManysOMManyManys',
                                           lafkey='one_many_id',
                                           rafkey='om_many_many_id')


class ManyOnes(JSON_API):
    """Resource objects that are associated from class Center through a
    many-to-one relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    centers = OneToManyRelationship('Centers', rfkey='many_one_id')
    mo_one_one_local = OneToOneLocalRelationship('MOOneOneLocals',
                                                 lfkey='mo_one_one_local_id')
    mo_one_one_remote = OneToOneRemoteRelationship('MOOneOneRemotes',
                                                   rfkey='many_one_id')
    mo_many_one = ManyToOneRelationship('MOManyOnes', lfkey='mo_many_one_id')
    mo_one_manys = OneToManyRelationship('MOOneManys', rfkey='many_one_id')
    mo_many_manys = ManyToManyRelationship('MOManyManys',
                                           'ManyOnesMOManyManys',
                                           lafkey='many_one_id',
                                           rafkey='mo_many_many_id')


class ManyManys(JSON_API):
    """Resource objects that are associated from class Center through a
    many-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    centers = ManyToManyRelationship('Centers',
                                     'CentersManyManys',
                                     lafkey='many_many_id',
                                     rafkey='center_id')
    mm_one_one_local = OneToOneLocalRelationship('MMOneOneLocals',
                                                 lfkey='mm_one_one_local_id')
    mm_one_one_remote = OneToOneRemoteRelationship('MMOneOneRemotes',
                                                   rfkey='many_many_id')
    mm_many_one = ManyToOneRelationship('MMManyOnes', lfkey='mm_many_one_id')
    mm_one_manys = OneToManyRelationship('MMOneManys', rfkey='many_many_id')
    mm_many_manys = ManyToManyRelationship('MMManyManys',
                                           'ManyManysMMManyManys',
                                           lafkey='many_many_id',
                                           rafkey='mm_many_many_id')


class OOLOneOneLocals(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    one-to-one relationship with a local foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_local = OneToOneRemoteRelationship('OneOneLocals',
                                               rfkey='ool_one_one_local_id')


class OOLOneOneRemotes(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    one-to-one relationship with a remote foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_local = OneToOneLocalRelationship('OneOneLocals',
                                              lfkey='one_one_local_id')


class OOLManyOnes(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    many-to-one relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_locals = OneToManyRelationship('OneOneLocals',
                                           rfkey='ool_many_one_id')


class OOLOneManys(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    one-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_local = ManyToOneRelationship('OneOneLocals',
                                          lfkey='one_one_local_id')


class OOLManyManys(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    many-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_locals = ManyToManyRelationship('OneOneLocals',
                                            'OneOneLocalsOOLManyManys',
                                            lafkey='ool_many_many_id',
                                            rafkey='one_one_local_id')


class OOROneOneLocals(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-one relationship with a local foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_remote = OneToOneRemoteRelationship('OneOneRemotes',
                                                rfkey='oor_one_one_local_id')


class OOROneOneRemotes(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-one relationship with a remote foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_remote = OneToOneLocalRelationship('OneOneRemotes',
                                               lfkey='one_one_remote_id')


class OORManyOnes(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    many-to-one relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_remotes = OneToManyRelationship('OneOneRemotes',
                                            rfkey='oor_many_one_id')


class OOROneManys(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_remote = ManyToOneRelationship('OneOneRemotes',
                                           lfkey='one_one_remote_id')


class OORManyManys(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    many-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_one_remotes = ManyToManyRelationship('OneOneRemotes',
                                             'OneOneRemotesOORManyManys',
                                             lafkey='oor_many_many_id',
                                             rafkey='one_one_remote_id')


class OMOneOneLocals(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-one relationship with a local foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_many = OneToOneRemoteRelationship('OneManys',
                                          rfkey='om_one_one_local_id')


class OMOneOneRemotes(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-one relationship with a remote foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_many = OneToOneLocalRelationship('OneManys', lfkey='one_many_id')


class OMManyOnes(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    many-to-one relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_manys = OneToManyRelationship('OneManys', rfkey='om_many_one_id')


class OMOneManys(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_many = ManyToOneRelationship('OneManys', lfkey='one_many_id')


class OMManyManys(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    many-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    one_manys = ManyToManyRelationship('OneManys',
                                       'OneManysOMManyManys',
                                       lafkey='om_many_many_id',
                                       rafkey='one_many_id')


class MOOneOneLocals(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    one-to-one relationship with a local foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_one = OneToOneRemoteRelationship('ManyOnes',
                                          rfkey='mo_one_one_local_id')


class MOOneOneRemotes(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    one-to-one relationship with a remote foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_one = OneToOneLocalRelationship('ManyOnes', lfkey='many_one_id')


class MOManyOnes(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    many-to-one relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_ones = OneToManyRelationship('ManyOnes', rfkey='mo_many_one_id')


class MOOneManys(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    one-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_one = ManyToOneRelationship('ManyOnes', lfkey='many_one_id')


class MOManyManys(JSON_API):
    """Resource objects that are associated from class OneOneLocals through a
    many-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_ones = ManyToManyRelationship('ManyOnes',
                                       'ManyOnesMOManyManys',
                                       lafkey='mo_many_many_id',
                                       rafkey='many_one_id')


class MMOneOneLocals(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-one relationship with a local foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_many = OneToOneRemoteRelationship('ManyManys',
                                           rfkey='mm_one_one_local_id')


class MMOneOneRemotes(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-one relationship with a remote foreign key.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_many = OneToOneLocalRelationship('ManyManys', lfkey='many_many_id')


class MMManyOnes(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    many-to-one relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_manys = OneToManyRelationship('ManyManys', rfkey='mm_many_one_id')


class MMOneManys(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    one-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_many = ManyToOneRelationship('ManyManys', lfkey='many_many_id')


class MMManyManys(JSON_API):
    """Resource objects that are associated from class OneOneRemotes through a
    many-to-many relationship.
    """
    # pylint: disable=too-few-public-methods

    attr_int = Attribute(Int64)
    attr_str = Attribute(String)

    many_manys = ManyToManyRelationship('ManyManys',
                                        'ManyManysMMManyManys',
                                        lafkey='mm_many_many_id',
                                        rafkey='many_many_id')


class Circulars(JSON_API):
    """Resource objects that refer to themselves."""
    # pylint: disable=too-few-public-methods

    one_one_local = OneToOneLocalRelationship('Circulars', lfkey='one_one_id')
    one_one_remote = OneToOneRemoteRelationship('Circulars', rfkey='one_one_id')
    one_manys = OneToManyRelationship('Circulars', rfkey='one_many_id')
    many_one = ManyToOneRelationship('Circulars', lfkey='one_many_id')
    many_manys_1 = ManyToManyRelationship('Circulars',
                                          'CircularsCirculars',
                                          lafkey='many_many_1_id',
                                          rafkey='many_many_2_id')
    many_manys_2 = ManyToManyRelationship('Circulars',
                                          'CircularsCirculars',
                                          lafkey='many_many_2_id',
                                          rafkey='many_many_1_id')
