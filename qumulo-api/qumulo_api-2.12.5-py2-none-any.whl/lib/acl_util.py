# Copyright (c) 2018 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from qumulo.lib.identity_util import Identity
from qumulo.lib.util import tabulate

ALLOWED_TYPE = "ALLOWED"
DENIED_TYPE = "DENIED"

class AceTranslator(object):
    '''
    Interface used by AclEditor to translate command-line arguments to access
    control entries expected by the target API (either an FS acl or a SMB
    share), and API reponses to text for display.
    '''

    def parse_trustee(self, trustee, ace):
        '''
        Translates a trustee specified on the command line (e.g. Everyone,
        sid:S-1-2-3-4, uid:1001, etc) into attributes on the given api ace.
        See @ref Identity for supported trustee formats.
        '''
        ace['trustee'] = Identity(trustee).dictionary()

    def pretty_trustee(self, ace):
        '''
        Formats the trustee attributes of the given ace into a human-readable
        string.
        '''
        trustee = Identity(ace['trustee'])
        # If the trustee has a name and a domain other than "world", we'll print
        # "domain:name" to avoid ambiguity when listing the share. We don't show
        # World because it only contains the already self-explanatory Everyone
        if trustee.has_name() and trustee.pretty_domain():
            return "{}:{}".format(trustee.pretty_domain(), str(trustee))
        return str(trustee)

    def ace_trustee_equal(self, ace, trustee):
        '''
        Determines whether a trustee specified on the command line (as for
        @ref parse_trustee) equals the trustee of the given ace.
        '''
        # When names are supported, may want to do a look-up to resolve
        # ambiguity.  Alternatively, could just require that the given name be
        # exactly the fully qualified name returned by the API.
        return Identity(ace['trustee']) == Identity(trustee)

    def parse_rights(self, rights, ace):
        '''
        Translates a list of rights (expected to be parsed and validated by
        an ArgumentParser) into attributes on the given api ace.
        It is an invariant that the given ACE will already have its type
        attribute set (see @ref FsAceTranslator for how and why this is used).
        '''
        raise NotImplementedError()

    def pretty_rights(self, ace):
        '''
        Formats the rights attribute of the given ace into a human-readable
        string.
        '''
        raise NotImplementedError()

    def ace_rights_equal(self, ace, rights):
        '''
        Determines whether rights specified on the command line equal the
        rights on the given ace.
        '''
        raise NotImplementedError()

    def parse_type_enum_value(self, ace_type):
        ace_type = ace_type.strip().upper()
        if ace_type not in {ALLOWED_TYPE, DENIED_TYPE}:
            raise ValueError('Type must be either "Allowed" or "Denied"')
        return ace_type

    def parse_type(self, ace_type, ace):
        '''
        Translates a type (expected to be parsed and validated by an
        ArgumentParser) into the attributes of the given api ace. This is
        currently common to all ace types, so it's implemented here.
        '''
        ace['type'] = self.parse_type_enum_value(ace_type)

    def pretty_type(self, ace):
        '''
        Formats the type attribute of the given ace into a human-readable
        string.
        '''
        return ace['type'].capitalize()

    def ace_type_equal(self, ace, ace_type):
        '''
        Determines whether the type specified on the command line equal the
        type of the given ace.
        '''
        return ace['type'] == self.parse_type_enum_value(ace_type)

    @property
    def has_flags(self):
        '''
        Indicates whether the ace type that this translator handles has flags.
        '''
        raise NotImplementedError()

    def parse_flags(self, flags, ace):
        '''
        Translates a list of flags (expected to be parsed and validated by an
        ArgumentParser) into an attribute on the given api ace.
        '''
        raise NotImplementedError()

    def pretty_flags(self, ace):
        '''
        Formats the flags attribute of the given ace into a human-readable
        string.
        '''
        raise NotImplementedError()

    def ace_flags_equal(self, ace, flags):
        '''
        Determines whether the flags specified on the command line equal the
        flags on the given ace.
        '''
        raise NotImplementedError()

    def find_grant_position(self, acl):
        '''
        Determine which position in a given acl is the correct position to
        insert new ACEs.  In the simple case this is usually the end, but
        e.g. FS ACLs with inherited ACEs have a different canonical position.
        '''
        return len(acl)

class AclEditor(object):
    '''
    Provides methods for manipulating an ACL.  Uses a given AceTranslator to
    handle different ACL structures (currently, fs acls and smb share acls).
    May start with a current ACL (for modify commands), or from an empty ACL
    (for add or reset).
    '''

    def __init__(self, translator, initial_acl=None):
        self.translator = translator
        self.acl = initial_acl if initial_acl else []

    def grant(self, trustees, rights, flags=None, position=None):
        '''
        Grants the given rights to the given trustees by appending
        ACEs to the ACL.  This would usually be used to build up a new ACL from
        nothing (but this usage is not strictly required).
        @p trustees A list of unparsed trustee strings
        @p rights A list of right options, e.g. ["Read", "Write"] ...
        @p flags Flags for the ACE.  Required if the ACL type has flags.
        @p position Override the position in the ACL where the new ACEs should
            be inserted.  By default, the AceTranslator controls insert position
        '''
        if position is None:
            position = self.translator.find_grant_position(self.acl)
        for trustee in trustees:
            new_ace = {}
            self.translator.parse_type(ALLOWED_TYPE, new_ace)
            self.translator.parse_trustee(trustee, new_ace)
            self.translator.parse_rights(rights, new_ace)
            if self.translator.has_flags:
                self.translator.parse_flags(flags, new_ace)
            self.acl.insert(position, new_ace)
            position += 1

    def deny(self, trustees, rights, flags=None, position=None):
        '''
        Denies the given rights to the given trustees by prepending ACEs
        to the ACL.  This would usually be used to build up a new ACL from
        nothing (but this usage is not strictly required).
        @p trustees A list of unparsed trustee strings
        @p rights A list of right options, e.g. ["Read", "Write"] ...
        @p position Override the position in the ACL where new ACEs should be
            inserted.  By default, they are inserted at the beginning.
        '''
        if position is None:
            position = 0
        for trustee in trustees:
            new_ace = {}
            self.translator.parse_type(DENIED_TYPE, new_ace)
            self.translator.parse_trustee(trustee, new_ace)
            self.translator.parse_rights(rights, new_ace)
            if self.translator.has_flags:
                self.translator.parse_flags(flags, new_ace)
            self.acl.insert(position, new_ace)
            position += 1

    def _find(self, position=None, trustee=None, ace_type=None, rights=None,
            flags=None, allow_multiple=False):
        '''
        Find the indices of ACEs matching the given description.
        See @ref remove and @ref modify for argument descriptions.
        @return a list of the indices of ACEs matching the arguments.
        '''
        if position is not None:
            if not all((trustee is None, ace_type is None, rights is None,
                    flags is None)):
                raise ValueError(
                    "Cannot specify entry by both position and attributes")
            # input is 1-indexed:
            if position < 1:
                raise ValueError("Position must be 1 or greater")
            if position > len(self.acl):
                raise ValueError("Position is past the end of the ACL")
            return [position - 1]

        res = []
        for index, ace in enumerate(self.acl):
            if trustee is not None and not self.translator.ace_trustee_equal(
                    ace, trustee):
                continue
            if ace_type is not None and not self.translator.ace_type_equal(
                    ace, ace_type):
                continue
            if rights is not None and not self.translator.ace_rights_equal(
                    ace, rights):
                continue
            if flags is not None and not self.translator.ace_flags_equal(
                    ace, flags):
                continue
            res.append(index)

        if not res:
            raise ValueError("No matching entries found")
        if len(res) > 1 and not allow_multiple:
            raise ValueError(
                "Expected to find exactly 1 entry, but found {}".format(
                    len(res)))

        return res

    def remove(self, position=None, trustee=None,
            ace_type=None, rights=None, flags=None, allow_multiple=False):
        '''
        Remove ACEs from the ACL, either by position, or by attribute.
        @p position Remove the ACE at the given 1-indexed position.  Mutually
            exclusive with all other arguments.
        @p trustee Remove ACE(s) with this trustee
        @p ace_type Remove ACE(s) with this ace_type (e.g. ALLOWED_TYPE, ...)
        @p rights Remove ACE(s) with these rights (e.g. READ_ACCESS, ...)
        @p allow_multiple If multiple ACEs match the given attributes, remove
            all of them.
        '''
        indices = self._find(
            position, trustee, ace_type, rights, flags, allow_multiple)

        # Remove in reverse-order, so indices are stable
        indices.reverse()
        for i in indices:
            del self.acl[i]

    def modify(self, position=None,
        old_trustee=None, old_type=None, old_rights=None, old_flags=None,
        new_trustee=None, new_type=None, new_rights=None, new_flags=None,
        allow_multiple=False):
        '''
        Modify a particular ACE in the ACL, either by position, or by matching
        attributes.
        @p position Modify the ACE at the given 1-indexed position.  Mutually
            exclusive with the old_<attr> arguments.
        @p old_trustee, old_type, old_rights Modify the ACE with these
            attributes.  Exactly one ACE must match the given attributes.
        @p new_trustee, new_type, new_rights If present, specify a new value
            for the given attribute.
        @p allow_multiple If multiple ACEs match the given attributes, modify
            all of them.
        '''
        indices = self._find(position,
            old_trustee, old_type, old_rights, old_flags, allow_multiple)

        for i in indices:
            if new_trustee is not None:
                self.translator.parse_trustee(new_trustee, self.acl[i])
            if new_type is not None:
                self.translator.parse_type(new_type, self.acl[i])
            if new_rights is not None:
                self.translator.parse_rights(new_rights, self.acl[i])
            if new_flags is not None:
                self.translator.parse_flags(new_flags, self.acl[i])

    def pretty_str(self):
        '''
        @return A nice tabular representation of the ACL.
        '''
        if self.translator.has_flags:
            headers = ["ID", "Trustee", "Type", "Flags", "Rights"]
        else:
            headers = ["ID", "Trustee", "Type", "Rights"]
        table = []
        for index, ace in enumerate(self.acl, start=1):
            row = [
                index,
                self.translator.pretty_trustee(ace),
                self.translator.pretty_type(ace)
            ]
            if self.translator.has_flags:
                row.append(self.translator.pretty_flags(ace))
            row.append(self.translator.pretty_rights(ace))

            table.append(row)
        return tabulate(table, headers=headers)
