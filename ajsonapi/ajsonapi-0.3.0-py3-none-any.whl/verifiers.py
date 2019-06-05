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
"""Module jsonapi/checks deals with checking JSON API requests."""

from ajsonapi.conversions import id_name_to_number, uuid_name_to_number
from ajsonapi.errors import (
    DocumentDataInvalidAttributeError,
    DocumentDataInvalidIdError,
    DocumentDataInvalidRelationshipError,
    DocumentDataInvalidTypeError,
    DocumentDataMalformedError,
    DocumentDataMalformedIdError,
    DocumentDataMalformedRelationshipError,
    DocumentDataMalformedUuidError,
    DocumentDataMissingIdError,
    DocumentDataMissingTypeError,
)
from ajsonapi.exceptions import ErrorsException, TypeNameError
from ajsonapi.id import Id


def verify_data_resource_object(data, collection, id_name=None):
    """Verifies that the object's type, id and attributes are correct.

    Args:
        data: data containing the resource_object.
        collection: collection from which the resource_object should be.
        id_name (str): valid id name for the resource object.

    Returns:
        The id number and attributes found in the object.
    """

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements

    errors = []

    # Type
    try:
        data_type_name = data['type']
        if data_type_name != collection.name:
            errors.append(
                DocumentDataInvalidTypeError(f'/data/type/{data_type_name}'))
    except TypeError:
        raise ErrorsException([DocumentDataMalformedError()])
    except KeyError:
        errors.append(DocumentDataMissingTypeError('/data'))

    # Id
    if 'id' in data:
        data_id_name = data['id']
        try:
            if id_name:
                if data_id_name != id_name:
                    errors.append(
                        DocumentDataInvalidIdError('Invalid resource object.',
                                                   f'/data/id/{data_id_name}'))
                data_id_number = id_name_to_number(data_id_name)
            else:
                data_id_number = uuid_name_to_number(data_id_name)
        except ValueError:
            errors.append(
                DocumentDataMalformedUuidError(f'/data/id/{data_id_name}'))
    else:
        if id_name:
            errors.append(DocumentDataMissingIdError())
        data_id_number = None

    # Attributes
    data_attributes = data.get('attributes', {})
    invalid_data_attribute_names = (
        set(data_attributes.keys()) -
        {attr.name for attr in collection.table.attributes})
    if invalid_data_attribute_names:
        errors.extend([
            DocumentDataInvalidAttributeError(
                f'/data/attributes/{data_attribute_name}')
            for data_attribute_name in invalid_data_attribute_names
        ])

    # Relationships
    data_relationships = data.get('relationships', {})
    invalid_data_relationship_names = (
        set(data_relationships.keys()) -
        {rel.name for rel in collection.table.relationships})
    if invalid_data_relationship_names:
        errors.extend([
            DocumentDataInvalidRelationshipError(
                f'/data/relationships/{data_relationship_name}')
            for data_relationship_name in invalid_data_relationship_names
        ])
    result_relationships = {}
    for relationship_name, value in data_relationships.items():
        if relationship_name in invalid_data_relationship_names:
            continue
        relationship = getattr(collection.table, relationship_name)
        try:
            relationship_data = value['data']
        except TypeError:
            errors.append(
                DocumentDataMalformedRelationshipError(
                    f'/data/relationships/{relationship_name}'))
            continue
        data_rio_ids = relationship.verify_data_rios(relationship_name,
                                                     relationship_data, errors)
        result_relationships[relationship_name] = data_rio_ids

    if errors:
        raise ErrorsException(errors)
    return data_id_number, data_attributes, result_relationships


def verify_data_resource_identifier_object(obj, valid_type_name):
    """Verifies that the resource identifiers object type and id are valid.

    Args:
        obj: object that needs verifying.
        valid_type_name (str): The expected type_name.

    Returns:
        The resource identifier object's id number.

    Raises:
        ErrorsException containing all the errors found.
    """
    errors = []

    # Type
    try:
        obj_type_name = obj['type']
        if obj_type_name != valid_type_name:
            errors.append(
                DocumentDataInvalidTypeError(f'/data/type/{obj_type_name}'))
    except TypeError:
        raise ErrorsException([DocumentDataMalformedError()])
    except KeyError:
        errors.append(DocumentDataMissingTypeError('/data'))

    # Id
    try:
        obj_id_name = obj['id']
        try:
            obj_id = Id(obj_id_name)
        except ValueError:
            errors.append(
                DocumentDataMalformedIdError(
                    'Invalid resource identifier object.',
                    f'/data/id/{obj_id_name}'))
    except KeyError:
        errors.append(DocumentDataMissingIdError('/data'))

    if errors:
        raise ErrorsException(errors)
    return obj_id


def verify_data_resource_identifier_objects(data, valid_type_name):
    """Verifies that the resource identifiers object type and id are valid.

    Args:
        obj: object that needs verifying.
        valid_type_name (str): The expected type_name.

    Returns:
        The resource identifier object's id number.

    Raises:
        ErrorsException containing all the errors found.
    """

    if not isinstance(data, list):
        raise ErrorsException([DocumentDataMalformedError()])

    try:
        obj_type_names = {obj['type'] for obj in data}
        if not obj_type_names <= {valid_type_name}:
            raise TypeNameError()
        return [Id(obj['id']) for obj in data]
    except (KeyError, ValueError, TypeNameError):
        errors = []
        for index, obj in enumerate(data):
            # Type
            try:
                obj_type_name = obj['type']
                if obj_type_name != valid_type_name:
                    errors.append(
                        DocumentDataInvalidTypeError(
                            f'/data/{index}/type/{obj_type_name}'))
            except KeyError:
                errors.append(DocumentDataMissingTypeError(f'/data/{index}'))

            # Id
            try:
                id_name = obj['id']
                try:
                    id_name_to_number(id_name)
                except ValueError:
                    errors.append(
                        DocumentDataMalformedIdError(
                            'Invalid resource identifier object.',
                            f'/data/{index}/id/{id_name}'))
            except KeyError:
                errors.append(DocumentDataMissingIdError(f'/data/{index}'))
        raise ErrorsException(errors)
