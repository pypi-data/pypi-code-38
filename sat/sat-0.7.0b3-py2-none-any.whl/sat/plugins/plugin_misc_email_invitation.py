#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for file tansfer
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import shortuuid
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools import utils
from sat.tools.common import data_format
from sat.memory import persistent
from sat.tools import email as sat_email

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Invitations",
    C.PI_IMPORT_NAME: "EMAIL_INVITATION",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_DEPENDENCIES: ['XEP-0077'],
    C.PI_RECOMMENDATIONS: ["IDENTITY"],
    C.PI_MAIN: "InvitationsPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""invitation of people without XMPP account""")
}


SUFFIX_MAX = 5
INVITEE_PROFILE_TPL = u"guest@@{uuid}"
KEY_ID = u'id'
KEY_JID = u'jid'
KEY_CREATED = u'created'
KEY_LAST_CONNECTION = u'last_connection'
KEY_GUEST_PROFILE = u'guest_profile'
KEY_PASSWORD = u'password'
KEY_EMAILS_EXTRA = u'emails_extra'
EXTRA_RESERVED = {KEY_ID, KEY_JID, KEY_CREATED, u'jid_', u'jid', KEY_LAST_CONNECTION,
                  KEY_GUEST_PROFILE, KEY_PASSWORD, KEY_EMAILS_EXTRA}
DEFAULT_SUBJECT = D_(u"You have been invited by {host_name} to {app_name}")
DEFAULT_BODY = D_(u"""Hello {name}!

You have received an invitation from {host_name} to participate to "{app_name}".
To join, you just have to click on the following URL:
{url}

Please note that this URL should not be shared with anybody!
If you want more details on {app_name}, you can check {app_url}.

Welcome!
""")


class InvitationsPlugin(object):

    def __init__(self, host):
        log.info(_(u"plugin Invitations initialization"))
        self.host = host
        self.invitations = persistent.LazyPersistentBinaryDict(u'invitations')
        host.bridge.addMethod("invitationCreate", ".plugin", in_sign='sasssssssssa{ss}s',
                              out_sign='a{ss}',
                              method=self._create,
                              async=True)
        host.bridge.addMethod("invitationGet", ".plugin", in_sign='s', out_sign='a{ss}',
                              method=self.get,
                              async=True)
        host.bridge.addMethod("invitationModify", ".plugin", in_sign='sa{ss}b',
                              out_sign='',
                              method=self._modify,
                              async=True)
        host.bridge.addMethod("invitationList", ".plugin", in_sign='s',
                              out_sign='a{sa{ss}}',
                              method=self._list,
                              async=True)

    def checkExtra(self, extra):
        if EXTRA_RESERVED.intersection(extra):
            raise ValueError(
                _(u"You can't use following key(s) in extra, they are reserved: {}")
                .format(u', '.join(EXTRA_RESERVED.intersection(extra))))

    def _create(self, email=u'', emails_extra=None, jid_=u'', password=u'', name=u'',
                host_name=u'', language=u'', url_template=u'', message_subject=u'',
                message_body=u'', extra=None, profile=u''):
        # XXX: we don't use **kwargs here to keep arguments name for introspection with
        #      D-Bus bridge
        if emails_extra is None:
            emails_extra = []

        if extra is None:
            extra = {}
        else:
            extra = {unicode(k): unicode(v) for k,v in extra.iteritems()}

        kwargs = {"extra": extra,
                  KEY_EMAILS_EXTRA: [unicode(e) for e in emails_extra]
                  }

        # we need to be sure that values are unicode, else they won't be pickled correctly
        # with D-Bus
        for key in ("jid_", "password", "name", "host_name", "email", "language",
                    "url_template", "message_subject", "message_body", "profile"):
            value = locals()[key]
            if value:
                kwargs[key] = unicode(value)
        d = self.create(**kwargs)
        def serialize(data):
            data[KEY_JID] = data[KEY_JID].full()
            return data
        d.addCallback(serialize)
        return d

    @defer.inlineCallbacks
    def create(self, **kwargs):
        ur"""Create an invitation

        This will create an XMPP account and a profile, and use a UUID to retrieve them.
        The profile is automatically generated in the form guest@@[UUID], this way they
            can be retrieved easily
        **kwargs: keywords arguments which can have the following keys, unset values are
                  equivalent to None:
            jid_(jid.JID, None): jid to use for invitation, the jid will be created using
                                 XEP-0077
                if the jid has no user part, an anonymous account will be used (no XMPP
                    account created in this case)
                if None, automatically generate an account name (in the form
                    "invitation-[random UUID]@domain.tld") (note that this UUID is not the
                    same as the invitation one, as jid can be used publicly (leaking the
                    UUID), and invitation UUID give access to account.
                in case of conflict, a suffix number is added to the account until a free
                    one if found (with a failure if SUFFIX_MAX is reached)
            password(unicode, None): password to use (will be used for XMPP account and
                                     profile)
                None to automatically generate one
            name(unicode, None): name of the invitee
                will be set as profile identity if present
            host_name(unicode, None): name of the host
            email(unicode, None): email to send the invitation to
                if None, no invitation email is sent, you can still associate email using
                    extra
                if email is used, extra can't have "email" key
            language(unicode): language of the invitee (used notabily to translate the
                               invitation)
                TODO: not used yet
            url_template(unicode, None): template to use to construct the invitation URL
                use {uuid} as a placeholder for identifier
                use None if you don't want to include URL (or if it is already specified
                    in custom message)
                /!\ you must put full URL, don't forget https://
                /!\ the URL will give access to the invitee account, you should warn in
                    message to not publish it publicly
            message_subject(unicode, None): customised message body for the invitation
                                            email
                None to use default subject
                uses the same substitution as for message_body
            message_body(unicode, None): customised message body for the invitation email
                None to use default body
                use {name} as a place holder for invitee name
                use {url} as a placeholder for the invitation url
                use {uuid} as a placeholder for the identifier
                use {app_name} as a placeholder for this software name
                use {app_url} as a placeholder for this software official website
                use {profile} as a placeholder for host's profile
                use {host_name} as a placeholder for host's name
            extra(dict, None): extra data to associate with the invitee
                some keys are reserved:
                    - created (creation date)
                if email argument is used, "email" key can't be used
            profile(unicode, None): profile of the host (person who is inviting)
        @return (dict[unicode, unicode]): dictionary with:
            - UUID associated with the invitee (key: id)
            - filled extra dictionary, as saved in the databae
        """
        ## initial checks
        extra = kwargs.pop('extra', {})
        if set(kwargs).intersection(extra):
            raise ValueError(
                _(u"You can't use following key(s) in both args and extra: {}").format(
                u', '.join(set(kwargs).intersection(extra))))

        self.checkExtra(extra)

        email = kwargs.pop(u'email', None)
        emails_extra = kwargs.pop(u'emails_extra', [])
        if not email and emails_extra:
            raise ValueError(
                _(u'You need to provide a main email address before using emails_extra'))

        if (email is not None
            and not 'url_template' in kwargs
            and not 'message_body' in kwargs):
            raise ValueError(
                _(u"You need to provide url_template if you use default message body"))

        ## uuid
        log.info(_(u"creating an invitation"))
        id_ = unicode(shortuuid.uuid())

        ## XMPP account creation
        password = kwargs.pop(u'password', None)
        if password is None:
           password = utils.generatePassword()
        assert password
        # XXX: password is here saved in clear in database
        #      it is needed for invitation as the same password is used for profile
        #      and SàT need to be able to automatically open the profile with the uuid
        # FIXME: we could add an extra encryption key which would be used with the uuid
        #        when the invitee is connecting (e.g. with URL). This key would not be
        #        saved and could be used to encrypt profile password.
        extra[KEY_PASSWORD] = password

        jid_ = kwargs.pop(u'jid_', None)
        if not jid_:
            domain = self.host.memory.getConfig(None, 'xmpp_domain')
            if not domain:
                # TODO: fallback to profile's domain
                raise ValueError(_(u"You need to specify xmpp_domain in sat.conf"))
            jid_ = u"invitation-{uuid}@{domain}".format(uuid=shortuuid.uuid(),
                                                        domain=domain)
        jid_ = jid.JID(jid_)
        if jid_.user:
            # we don't register account if there is no user as anonymous login is then
            # used
            try:
                yield self.host.plugins['XEP-0077'].registerNewAccount(jid_, password)
            except error.StanzaError as e:
                prefix = jid_.user
                idx = 0
                while e.condition == u'conflict':
                    if idx >= SUFFIX_MAX:
                        raise exceptions.ConflictError(_(u"Can't create XMPP account"))
                    jid_.user = prefix + '_' + unicode(idx)
                    log.info(_(u"requested jid already exists, trying with {}".format(
                        jid_.full())))
                    try:
                        yield self.host.plugins['XEP-0077'].registerNewAccount(jid_,
                                                                               password)
                    except error.StanzaError as e:
                        idx += 1
                    else:
                        break
                if e.condition != u'conflict':
                    raise e

            log.info(_(u"account {jid_} created").format(jid_=jid_.full()))

        ## profile creation

        extra[KEY_GUEST_PROFILE] = guest_profile = INVITEE_PROFILE_TPL.format(uuid=id_)
        # profile creation should not fail as we generate unique name ourselves
        yield self.host.memory.createProfile(guest_profile, password)
        yield self.host.memory.startSession(password, guest_profile)
        yield self.host.memory.setParam("JabberID", jid_.full(), "Connection",
                                        profile_key=guest_profile)
        yield self.host.memory.setParam("Password", password, "Connection",
                                        profile_key=guest_profile)
        name = kwargs.pop(u'name', None)
        if name is not None:
            extra[u'name'] = name
            try:
                id_plugin = self.host.plugins[u'IDENTITY']
            except KeyError:
                pass
            else:
                yield self.host.connect(guest_profile, password)
                guest_client = self.host.getClient(guest_profile)
                yield id_plugin.setIdentity(guest_client, {u'nick': name})
                yield self.host.disconnect(guest_profile)

        ## email
        language = kwargs.pop(u'language', None)
        if language is not None:
            extra[u'language'] = language.strip()

        if email is not None:
            extra[u'email'] = email
            data_format.iter2dict(KEY_EMAILS_EXTRA, extra)
            url_template = kwargs.pop(u'url_template', '')
            format_args = {
                u'uuid': id_,
                u'app_name': C.APP_NAME,
                u'app_url': C.APP_URL}

            if name is None:
                format_args[u'name'] = email
            else:
                format_args[u'name'] = name

            profile = kwargs.pop(u'profile', None)
            if profile is None:
                format_args[u'profile'] = u''
            else:
                format_args[u'profile'] = extra[u'profile'] = profile

            host_name = kwargs.pop(u'host_name', None)
            if host_name is None:
                format_args[u'host_name'] = profile or _(u"somebody")
            else:
                format_args[u'host_name'] = extra[u'host_name'] = host_name

            invite_url = url_template.format(**format_args)
            format_args[u'url'] = invite_url

            yield sat_email.sendEmail(
                self.host,
                [email] + emails_extra,
                (kwargs.pop(u'message_subject', None) or DEFAULT_SUBJECT).format(
                    **format_args),
                (kwargs.pop(u'message_body', None) or DEFAULT_BODY).format(**format_args),
            )

        ## extra data saving
        self.invitations[id_] = extra

        if kwargs:
            log.warning(_(u"Not all arguments have been consumed: {}").format(kwargs))

        extra[KEY_ID] = id_
        extra[KEY_JID] = jid_
        defer.returnValue(extra)

    def get(self, id_):
        """Retrieve invitation linked to uuid if it exists

        @param id_(unicode): UUID linked to an invitation
        @return (dict[unicode, unicode]): data associated to the invitation
        @raise KeyError: there is not invitation with this id_
        """
        return self.invitations[id_]

    def _modify(self, id_, new_extra, replace):
        return self.modify(id_, {unicode(k): unicode(v) for k,v in new_extra.iteritems()},
                           replace)

    def modify(self, id_, new_extra, replace=False):
        """Modify invitation data

        @param id_(unicode): UUID linked to an invitation
        @param new_extra(dict[unicode, unicode]): data to update
            empty values will be deleted if replace is True
        @param replace(bool): if True replace the data
            else update them
        @raise KeyError: there is not invitation with this id_
        """
        self.checkExtra(new_extra)
        def gotCurrentData(current_data):
            if replace:
                new_data = new_extra
                for k in EXTRA_RESERVED:
                    try:
                        new_data[k] = current_data[k]
                    except KeyError:
                        continue
            else:
                new_data = current_data
                for k,v in new_extra.iteritems():
                    if k in EXTRA_RESERVED:
                        log.warning(_(u"Skipping reserved key {key}".format(k)))
                        continue
                    if v:
                        new_data[k] = v
                    else:
                        try:
                            del new_data[k]
                        except KeyError:
                            pass

            self.invitations[id_] = new_data

        d = self.invitations[id_]
        d.addCallback(gotCurrentData)
        return d

    def _list(self, profile=C.PROF_KEY_NONE):
        return self.list(profile)

    @defer.inlineCallbacks
    def list(self, profile=C.PROF_KEY_NONE):
        """List invitations

        @param profile(unicode): return invitation linked to this profile only
            C.PROF_KEY_NONE: don't filter invitations
        @return list(unicode): invitations uids
        """
        invitations = yield self.invitations.items()
        if profile != C.PROF_KEY_NONE:
            invitations = {id_:data for id_, data in invitations.iteritems()
                           if data.get(u'profile') == profile}

        defer.returnValue(invitations)
