"""An interface for creating and retrieving PII records in Matchlight."""
from __future__ import absolute_import

import io
import json

import six

import matchlight.error
import matchlight.utils

from pylibfp import (
    fingerprint,
    fingerprints_pii_address_variants,
    fingerprints_pii_city_state_zip_variants,
    fingerprints_pii_credit_card,
    fingerprints_pii_email_address,
    fingerprints_pii_iban,
    fingerprints_pii_name_variants,
    fingerprints_pii_phone_number,
    fingerprints_pii_ssn,
    MODE_CODE,
    OPTIONS_TILED,
)


__all__ = (
    'Record',
    'RecordMethods',
)


MAX_DOCUMENT_FINGERPRINTS = 840


class Record(object):
    """Represents a personal information record."""

    def __init__(self, id, name, description, ctime=None, mtime=None,
                 metadata=None):
        """Initializes a new personal information record.

        Args:
            id (:obj:`str`): A 128-bit UUID.
            name (:obj:`str`): The name of the record.
            description (:obj:`str`): The description of the record.
            ctime (:obj:`int`, optional): A Unix timestamp of the
                record creation timestamp.
            mtime (:obj:`int`, optional): A Unix timestamp of the
                record last modification date timestamp.

        """
        if metadata is None:
            metadata = {}
        self.id = id
        self.name = name
        self.description = description
        self.ctime = ctime
        self.mtime = mtime
        self.metadata = metadata

    @classmethod
    def from_mapping(cls, mapping):
        """Creates a new project instance from the given mapping."""
        return cls(
            id=mapping['id'],
            name=mapping['name'],
            description=mapping['description'],
            ctime=mapping['ctime'],
            mtime=mapping['mtime'],
            metadata=mapping['metadata'],
        )

    @property
    def user_provided_id(self):
        """:obj:`int`: The user provided record identifier."""
        return self.metadata.get('user_record_id', None)

    @property
    def details(self):
        """:obj:`dict`: Returns the feed details as a mapping."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ctime': self.ctime,
            'mtime': self.mtime,
            'metadata': self.metadata,
        }

    def __repr__(self):  # pragma: no cover
        return '<Record(name="{}", id="{}")>'.format(self.name, self.id)


class RecordMethods(object):
    """Provides methods for interfacing with the records API.

    Examples:
        Get record by record id::
            >>> record = ml.records.get("0760570a2c4a4ea68d526f58bab46cbd")
            >>> record
            <Record(name="pce****@terbiumlabs.com",
            id="0760570a2c4a4ea68d526f58bab46cbd")>

        Add PII records to a project::
            >>> pii_project = ml.projects.add(
            ...     name="Employee Database May 2016",
            ...     project_type="pii")
            >>> record_data = {
            ...     "first_name": "Bird",
            ...     "last_name": "Feather",
            ...     "email": "familybird@teribumlabs.com",
            ... }
            >>> new_record = ml.records.add_pii(
            ...      pii_project,
            ...      "uploaded on 20160519",
            ...      **record_data)

        Delete a record::
            >>> record
            <Record(name="fam****@terbiumlabs.com",
            id="655a732ad0f243beab1801651c2088a3")>
            >>> ml.record.delete(record)

    """

    def __init__(self, ml_connection):  # noqa: D205,D400
        """Initializes a records interface with the given Matchlight
        connection.

        Args:
            ml_connection (:class:`~.Connection`): A Matchlight
                connection instance.

        """
        self.conn = ml_connection

    def all(self):
        """Returns all records associated with the account."""
        return self.filter()

    def add_document(self, project, name, description, content,
                     user_record_id='-', min_score=None, offline=False):
        """Creates a new document record in the given project.

        Args:
            project (:class:`~.Project`): Project object to associate
                with record.
            name (:obj:`str`): The name of the document (not
                fingerprinted).
            description (:obj:`str`): A description of the record (not
                fingerprinted).
            content (:obj:`str`): The text of the document to be
                fingerprinted. Must be 840 characters or less.
            user_record_id (:obj:`str`, optional): An optional, user
                provided custom record identifier. Defaults to
                :obj:`NoneType`.
            offline (:obj:`bool`, optional): Run in "offline mode". No
                data is sent to the Matchlight server. Returns a
                dictionary of values instead of a :class:`~.Report`
                instance.

        Returns:
            :class:`~.Record`: Created record with metadata.

        """
        if len(content) > MAX_DOCUMENT_FINGERPRINTS:
            raise matchlight.error.SDKError(
                'Fingerprinter Failed: the maximum length of a Document record'
                ' is 840 characters.'
            )

        result_json = fingerprint(content, flags=OPTIONS_TILED)
        result = json.loads(result_json)
        fingerprints = result['data']['fingerprints']

        data = {
            'name': name,
            'desc': description,
            'user_record_id': user_record_id,
            'fingerprints': fingerprints,
            'metadata': {
                'fingerprinting_tool_name': 'Python SDK',
                'fingerprinting_tool_version': matchlight.__version__
            }
        }
        if min_score is not None:
            data['metadata']['min_score'] = str(min_score)
        if offline:
            return data
        else:
            return self.add_document_from_fingerprints(project, data)

    def add_document_from_fingerprints(self, project, fingerprint_data):
        """Add a document record from fingerprints.

        Add a document record from fingerprinted data generated by the
        :class:`~/.Record.add_pii` in offline mode.

        Args:
            project (:class:`~.Project`): Project object to associate
                with record.
            fingerprint_data (:obj:`dict`): The output of
                :class:`~/.Record.add_document(offline=True)`
        """
        response = self.conn.request(
            '/records/upload/document/{upload_token}'.format(
                upload_token=project.upload_token
            ),
            data=json.dumps(fingerprint_data)
        )
        return Record.from_mapping(response.json())

    def add_pii(self, project, description, email, first_name=None,
                middle_name=None, last_name=None, ssn=None, address=None,
                city=None, state=None, zipcode=None, phone=None,
                credit_card=None, iban=None, user_record_id='-',
                offline=False):
        """Creates a new PII record in the given project.

        Args:
            project (:class:`~.Project`): Project object to associate
                with record.
            description (:obj:`str`): A description of the record (not
                fingerprinted).
            email (:obj:`str`, optional): An email address.
            first_name (:obj:`str`, optional): Defaults to
                :obj:`NoneType`.
            middle_name (:obj:`str`, optional): Defaults to
                :obj:`NoneType`.
            last_name (:obj:`str`, optional): Defaults to
                :obj:`NoneType`.
            ssn (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            address (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            city (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            state (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            zipcode (int, optional): Defaults to :obj:`NoneType`.
            phone (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            credit_card (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            iban (:obj:`str`, optional): Defaults to :obj:`NoneType`.
            user_record_id (:obj:`str`, optional): An optional, user
                provided custom record identifier. Defaults to
                :obj:`NoneType`.
            offline (:obj:`bool`, optional): Run in "offline mode". No
                data is sent to the Matchlight server. Returns a
                dictionary of values instead of a :class:`~.Report`
                instance.

        Returns:
            :class:`~.Record`: Created record with metadata.

        """
        if first_name is not None and last_name is None:
            raise matchlight.error.SDKError(
                'Fingerprinter Failed: the last_name argument is required '
                'along with the first_name argument.'
            )

        if first_name is None and last_name is not None:
            raise matchlight.error.SDKError(
                'Fingerprinter Failed: the first_name argument is required '
                'along with the last_name argument.'
            )

        data = {
            'desc': description,
            'user_record_id': user_record_id,
            'blinded_first': matchlight.utils.blind_name(first_name),
            'blinded_last': matchlight.utils.blind_name(last_name),
            'blinded_email': matchlight.utils.blind_email(email),
            'metadata': {
                'fingerprinting_tool_name': 'Python SDK',
                'fingerprinting_tool_version': matchlight.__version__
            }
        }

        if any((first_name, middle_name, last_name)):
            name_fingerprints = fingerprints_pii_name_variants(
                first_name or '', middle_name or None, last_name or '')
            data['name_fingerprints'] = name_fingerprints

        if email:
            email_fingerprints = fingerprints_pii_email_address(email)
            data['email_fingerprints'] = email_fingerprints
        data['blinded_email'] = matchlight.utils.blind_email(email)
        data['name'] = matchlight.utils.blind_email(email)

        if ssn:
            ssn_fingerprints = [fingerprints_pii_ssn(ssn)]
            data['ssn_fingerprints'] = ssn_fingerprints

        if address:
            address_fingerprints = fingerprints_pii_address_variants(
                address)
            data['street_address_fingerprints'] = address_fingerprints

        if any((city, state, zipcode)):
            csz_fingerprints = fingerprints_pii_city_state_zip_variants(
                *[six.text_type(text) if text is not None else ''
                  for text in (city, state, zipcode)])
            data['city_state_zip_fingerprints'] = csz_fingerprints

        if phone:
            phone_fingerprints = fingerprints_pii_phone_number(phone)
            data['phone_fingerprints'] = [phone_fingerprints]

        if credit_card:
            cc_fingerprints = fingerprints_pii_credit_card(credit_card)
            data['credit_card_fingerprints'] = [cc_fingerprints]

        if iban:
            iban_fingerprints = fingerprints_pii_iban(iban)
            data['iban_fingerprints'] = iban_fingerprints

        if offline:
            return data
        else:
            return self.add_pii_from_fingerprints(project, data)

    def add_pii_from_fingerprints(self, project, fingerprint_data):
        """Add a PII record from fingerprints.

        Add a PII record from fingerprinted data generated by the
        :class:`~/.Record.add_pii` in offline mode.

        Args:
            project (:class:`~.Project`): Project object to associate
                with record.
            fingerprint_data (:obj:`dict`): The output of
                :class:`~/.Record.add_pii(offline=True)`
        """
        response = self.conn.request(
            '/records/upload/pii/{}'.format(
                project.upload_token
            ),
            data=json.dumps(fingerprint_data)
        )
        return Record.from_mapping(response.json())

    def add_source_code(self, project, name, description, code_path,
                        min_score=None, offline=False):
        """Creates a new source code record in the given project.

        Args:
            project (:class:`~.Project`): Project object to associate
                with record.
            name (:obj:`str`): The name of the file (not
                fingerprinted).
            description (:obj:`str`): A description of the code (not
                fingerprinted).
            code_path (:obj:`str`): The location of the source code.
                Code must be 840 characters or less.
            user_record_id (:obj:`str`, optional): An optional, user
                provided custom record identifier. Defaults to
                :obj:`NoneType`.
            offline (:obj:`bool`, optional): Run in "offline mode". No
                data is sent to the Matchlight server. Returns a
                dictionary of values instead of a :class:`~.Report`
                instance.

        Returns:
            :class:`~.Record`: Created record with metadata.

        """
        with io.open(code_path, 'r', encoding='utf-8') as document:
            content = document.read()

        if len(content) > MAX_DOCUMENT_FINGERPRINTS:
            raise matchlight.error.SDKError(
                'Fingerprinter Failed: the maximum length of a Source Code '
                'record is 840 characters.'
            )

        result_json = fingerprint(content, flags=OPTIONS_TILED, mode=MODE_CODE)
        result = json.loads(result_json)
        fingerprints = result['data']['fingerprints']

        data = {
            'name': name,
            'desc': description,
            'fingerprints': fingerprints,
            'metadata': {
                'fingerprinting_tool_name': 'Python SDK',
                'fingerprinting_tool_version': matchlight.__version__
            }
        }

        if min_score is not None:
            data['metadata']['min_score'] = str(min_score)
        if offline:
            return data
        else:
            return self.add_source_code_from_fingerprints(project, data)

    def add_source_code_from_fingerprints(self, project, fingerprint_data):
        """Add a source code record from fingerprints.

        Add a souce code record from fingerprinted data generated by the
        :class:`~/.Record.add_source_code` in offline mode.

        Args:
            project (:class:`~.Project`): Project object to associate
                with record.
            fingerprint_data (:obj:`dict`): The output of
                :class:`~/.Record.add_source_code(offline=True)`
        """
        response = self.conn.request(
            '/records/upload/source_code/{}'.format(
                upload_token=project.upload_token
            ),
            data=json.dumps(fingerprint_data)
        )
        return Record.from_mapping(response.json())

    def delete(self, record_or_id):
        """Delete a fingerprinted record.

        Args:
            record_or_id (:class:`~.Record` or :obj:`str`): The record
                object or identifier to be deleted.

        Returns:
            :obj:`NoneType`

        """
        if isinstance(record_or_id, Record):
            record_upload_token = record_or_id.id
        else:
            record_upload_token = record_or_id
        self.conn.request('/record/{}/delete'.format(record_upload_token),
                          data=json.dumps({}))

    def filter(self, project=None):
        """Returns a list of records.

        Providing an optional **project** keyword argument will only
        return records that are associated with a specific project.

        Example:
            Request all records::

                >>> my_project
                <Project(name="Super Secret Algorithm", type="source_code")>
                >>> ml.records.filter(project=my_project)
                [<Record(name="fam****@fakeemail.com",
                id="625a732ad0f247beab18595z951c2088a3")>,
                Record(name="pce****@fakeemail.com",
                id="f9427dd5a24d4a98b2069004g04c2977")]

        Args:
            project (:class:`~.Project`, optional): a project object.
                Defaults to all projects if not specified.

        Returns:
            :obj:`list` of :class:`~.Record`: List of records that
                are associated with a project.

        """
        if project is not None:
            upload_token = project.upload_token
        else:
            upload_token = None
        response = self.conn.request('/records', params={
            'upload_token': upload_token})
        records = []
        for payload in response.json().get('data', []):
            records.append(Record(
                id=payload['id'],
                name=payload['name'],
                description=payload['description'],
                ctime=int(payload['ctime']),
                mtime=int(payload['mtime']),
            ))
        return records

    def get(self, record_id):
        """Returns a record by the given record ID.

        Args:
            record_id (:obj:`str`): The record identifier.

        Returns:
           :class:`~.Record`: A record instance.

        """
        return next((record for record in self.filter()
                     if record.id == record_id), None)

    def __iter__(self):
        return iter(self.filter())
