#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
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

from sat.core.i18n import _

### logging ###
import logging as log
log.basicConfig(level=log.DEBUG,
                format='%(message)s')
###

import sys
import locale
import os.path
import argparse
from glob import iglob
from importlib import import_module
from sat_frontends.tools.jid import JID
from sat.tools import config
from sat.tools.common import dynamic_import
from sat.tools.common import uri
from sat.tools.common import date_utils
from sat.core import exceptions
import sat_frontends.jp
from sat_frontends.jp.constants import Const as C
from sat_frontends.tools import misc
import xml.etree.ElementTree as ET  # FIXME: used temporarily to manage XMLUI
import shlex
from collections import OrderedDict

## bridge handling
# we get bridge name from conf and initialise the right class accordingly
main_config = config.parseMainConf()
bridge_name = config.getConfig(main_config, '', 'bridge', 'dbus')


# TODO: move loops handling in a separated module
if 'dbus' in bridge_name:
    from gi.repository import GLib


    class JPLoop(object):

        def __init__(self):
            self.loop = GLib.MainLoop()

        def run(self):
            self.loop.run()

        def quit(self):
            self.loop.quit()

        def call_later(self, delay, callback, *args):
            """call a callback repeatedly

            @param delay(int): delay between calls in ms
            @param callback(callable): method to call
                if the callback return True, the call will continue
                else the calls will stop
            @param *args: args of the callbac
            """
            GLib.timeout_add(delay, callback, *args)

else:
    print u"can't start jp: only D-Bus bridge is currently handled"
    sys.exit(C.EXIT_ERROR)
    # FIXME: twisted loop can be used when jp can handle fully async bridges
    # from twisted.internet import reactor

    # class JPLoop(object):

    #     def run(self):
    #         reactor.run()

    #     def quit(self):
    #         reactor.stop()

    #     def _timeout_cb(self, args, callback, delay):
    #         ret = callback(*args)
    #         if ret:
    #             reactor.callLater(delay, self._timeout_cb, args, callback, delay)

    #     def call_later(self, delay, callback, *args):
    #         delay = float(delay) / 1000
    #         reactor.callLater(delay, self._timeout_cb, args, callback, delay)

if bridge_name == "embedded":
    from sat.core import sat_main
    sat = sat_main.SAT()

if sys.version_info < (2, 7, 3):
    # XXX: shlex.split only handle unicode since python 2.7.3
    # this is a workaround for older versions
    old_split = shlex.split
    new_split = (lambda s, *a, **kw: [t.decode('utf-8') for t in old_split(s.encode('utf-8'), *a, **kw)]
        if isinstance(s, unicode) else old_split(s, *a, **kw))
    shlex.split = new_split

try:
    import progressbar
except ImportError:
    msg = (_(u'ProgressBar not available, please download it at http://pypi.python.org/pypi/progressbar\n') +
           _(u'Progress bar deactivated\n--\n'))
    print >>sys.stderr,msg.encode('utf-8')
    progressbar=None

#consts
PROG_NAME = u"jp"
DESCRIPTION = """This software is a command line tool for XMPP.
Get the latest version at """ + C.APP_URL

COPYLEFT = u"""Copyright (C) 2009-2019 Jérôme Poisson, Adrien Cossa
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it under certain conditions.
"""

PROGRESS_DELAY = 10 # the progression will be checked every PROGRESS_DELAY ms


def unicode_decoder(arg):
    # Needed to have unicode strings from arguments
    return arg.decode(locale.getpreferredencoding())


def date_decoder(arg):
    return date_utils.date_parse_ext(arg, default_tz=date_utils.TZ_LOCAL)


class Jp(object):
    """
    This class can be use to establish a connection with the
    bridge. Moreover, it should manage a main loop.

    To use it, you mainly have to redefine the method run to perform
    specify what kind of operation you want to perform.

    """
    def __init__(self):
        """

        @attribute quit_on_progress_end (bool): set to False if you manage yourself exiting,
            or if you want the user to stop by himself
        @attribute progress_success(callable): method to call when progress just started
            by default display a message
        @attribute progress_success(callable): method to call when progress is successfully finished
            by default display a message
        @attribute progress_failure(callable): method to call when progress failed
            by default display a message
        """
        # FIXME: need_loop should be removed, everything must be async in bridge so
        #        loop will always be needed
        bridge_module = dynamic_import.bridge(bridge_name, 'sat_frontends.bridge')
        if bridge_module is None:
            log.error(u"Can't import {} bridge".format(bridge_name))
            sys.exit(1)

        self.bridge = bridge_module.Bridge()
        self.bridge.bridgeConnect(callback=self._bridgeCb, errback=self._bridgeEb)

    def _bridgeCb(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description=DESCRIPTION)
        self._make_parents()
        self.add_parser_options()
        self.subparsers = self.parser.add_subparsers(title=_(u'Available commands'), dest='subparser_name')
        self._auto_loop = False # when loop is used for internal reasons
        self._need_loop = False

        # progress attributes
        self._progress_id = None # TODO: manage several progress ids
        self.quit_on_progress_end = True

        # outputs
        self._outputs = {}
        for type_ in C.OUTPUT_TYPES:
            self._outputs[type_] = OrderedDict()
        self.default_output = {}

        self.own_jid = None  # must be filled at runtime if needed

    def _bridgeEb(self, failure):
        if isinstance(failure, exceptions.BridgeExceptionNoService):
            print(_(u"Can't connect to SàT backend, are you sure it's launched ?"))
        elif isinstance(failure, exceptions.BridgeInitError):
            print(_(u"Can't init bridge"))
        else:
            print(_(u"Error while initialising bridge: {}".format(failure)))
        sys.exit(C.EXIT_BRIDGE_ERROR)

    @property
    def version(self):
        return self.bridge.getVersion()

    @property
    def progress_id(self):
        return self._progress_id

    @progress_id.setter
    def progress_id(self, value):
        self._progress_id = value
        self.replayCache('progress_ids_cache')

    @property
    def watch_progress(self):
        try:
            self.pbar
        except AttributeError:
            return False
        else:
            return True

    @watch_progress.setter
    def watch_progress(self, watch_progress):
        if watch_progress:
            self.pbar = None

    @property
    def verbosity(self):
        try:
            return self.args.verbose
        except AttributeError:
            return 0

    def replayCache(self, cache_attribute):
        """Replay cached signals

        @param cache_attribute(str): name of the attribute containing the cache
            if the attribute doesn't exist, there is no cache and the call is ignored
            else the cache must be a list of tuples containing the replay callback as first item,
            then the arguments to use
        """
        try:
            cache = getattr(self, cache_attribute)
        except AttributeError:
            pass
        else:
            for cache_data in cache:
                cache_data[0](*cache_data[1:])

    def disp(self, msg, verbosity=0, error=False, no_lf=False):
        """Print a message to user

        @param msg(unicode): message to print
        @param verbosity(int): minimal verbosity to display the message
        @param error(bool): if True, print to stderr instead of stdout
        @param no_lf(bool): if True, do not emit line feed at the end of line
        """
        if self.verbosity >= verbosity:
            if error:
                if no_lf:
                    print >>sys.stderr,msg.encode('utf-8'),
                else:
                    print >>sys.stderr,msg.encode('utf-8')
            else:
                if no_lf:
                    print msg.encode('utf-8'),
                else:
                    print msg.encode('utf-8')

    def output(self, type_, name, extra_outputs, data):
        if name in extra_outputs:
            extra_outputs[name](data)
        else:
            self._outputs[type_][name]['callback'](data)

    def addOnQuitCallback(self, callback, *args, **kwargs):
        """Add a callback which will be called on quit command

        @param callback(callback): method to call
        """
        try:
            callbacks_list = self._onQuitCallbacks
        except AttributeError:
            callbacks_list = self._onQuitCallbacks = []
        finally:
            callbacks_list.append((callback, args, kwargs))

    def getOutputChoices(self, output_type):
        """Return valid output filters for output_type

        @param output_type: True for default,
            else can be any registered type
        """
        return self._outputs[output_type].keys()

    def _make_parents(self):
        self.parents = {}

        # we have a special case here as the start-session option is present only if connection is not needed,
        # so we create two similar parents, one with the option, the other one without it
        for parent_name in ('profile', 'profile_session'):
            parent = self.parents[parent_name] = argparse.ArgumentParser(add_help=False)
            parent.add_argument("-p", "--profile", action="store", type=str, default='@DEFAULT@', help=_("Use PROFILE profile key (default: %(default)s)"))
            parent.add_argument("--pwd", action="store", type=unicode_decoder, default='', metavar='PASSWORD', help=_("Password used to connect profile, if necessary"))

        profile_parent, profile_session_parent = self.parents['profile'], self.parents['profile_session']

        connect_short, connect_long, connect_action, connect_help = "-c", "--connect", "store_true", _(u"Connect the profile before doing anything else")
        profile_parent.add_argument(connect_short, connect_long, action=connect_action, help=connect_help)

        profile_session_connect_group = profile_session_parent.add_mutually_exclusive_group()
        profile_session_connect_group.add_argument(connect_short, connect_long, action=connect_action, help=connect_help)
        profile_session_connect_group.add_argument("--start-session", action="store_true", help=_("Start a profile session without connecting"))

        progress_parent = self.parents['progress'] = argparse.ArgumentParser(add_help=False)
        if progressbar:
            progress_parent.add_argument("-P", "--progress", action="store_true", help=_("Show progress bar"))

        verbose_parent = self.parents['verbose'] = argparse.ArgumentParser(add_help=False)
        verbose_parent.add_argument('--verbose', '-v', action='count', default=0, help=_(u"Add a verbosity level (can be used multiple times)"))

        draft_parent = self.parents['draft'] = argparse.ArgumentParser(add_help=False)
        draft_group = draft_parent.add_argument_group(_('draft handling'))
        draft_group.add_argument("-D", "--current", action="store_true", help=_(u"load current draft"))
        draft_group.add_argument("-F", "--draft-path", type=unicode_decoder, help=_(u"path to a draft file to retrieve"))


    def make_pubsub_group(self, flags, defaults):
        """generate pubsub options according to flags

        @param flags(iterable[unicode]): see [CommandBase.__init__]
        @param defaults(dict[unicode, unicode]): help text for default value
            key can be "service" or "node"
            value will be set in " (DEFAULT: {value})", or can be None to remove DEFAULT
        @return (ArgumentParser): parser to add
        """
        flags = misc.FlagsHandler(flags)
        parent = argparse.ArgumentParser(add_help=False)
        pubsub_group = parent.add_argument_group('pubsub')
        pubsub_group.add_argument("-u", "--pubsub-url", type=unicode_decoder,
                                  help=_(u"Pubsub URL (xmpp or http)"))

        service_help = _(u"JID of the PubSub service")
        if not flags.service:
            default = defaults.pop(u'service', _(u'PEP service'))
            if default is not None:
                service_help += _(u" (DEFAULT: {default})".format(default=default))
        pubsub_group.add_argument("-s", "--service", type=unicode_decoder, default=u'',
                                  help=service_help)

        node_help = _(u"node to request")
        if not flags.node:
            default = defaults.pop(u'node', _(u'standard node'))
            if default is not None:
                node_help += _(u" (DEFAULT: {default})".format(default=default))
        pubsub_group.add_argument("-n", "--node", type=unicode_decoder, default=u'', help=node_help)

        if flags.single_item:
            item_help = (u"item to retrieve")
            if not flags.item:
                default = defaults.pop(u'item', _(u'last item'))
                if default is not None:
                    item_help += _(u" (DEFAULT: {default})".format(default=default))
            pubsub_group.add_argument("-i", "--item", type=unicode_decoder, default=u'',
                                      help=item_help)
            pubsub_group.add_argument("-L", "--last-item", action='store_true', help=_(u'retrieve last item'))
        elif flags.multi_items:
            # mutiple items, this activate several features: max-items, RSM, MAM
            # and Orbder-by
            pubsub_group.add_argument("-i", "--item", type=unicode_decoder, action='append', dest='items', default=[], help=_(u"items to retrieve (DEFAULT: all)"))
            if not flags.no_max:
                max_group = pubsub_group.add_mutually_exclusive_group()
                # XXX: defaut value for --max-items or --max is set in parse_pubsub_args
                max_group.add_argument(
                    "-M", "--max-items", dest="max", type=int,
                    help=_(u"maximum number of items to get ({no_limit} to get all items)"
                           .format(no_limit=C.NO_LIMIT)))
                # FIXME: it could be possible to no duplicate max (between pubsub
                #        max-items and RSM max)should not be duplicated, RSM could be
                #        used when available and pubsub max otherwise
                max_group.add_argument(
                    "-m", "--max", dest="rsm_max", type=int,
                    help=_(u"maximum number of items to get per page (DEFAULT: 10)"))

            # RSM

            rsm_page_group = pubsub_group.add_mutually_exclusive_group()
            rsm_page_group.add_argument(
                "-a", "--after", dest="rsm_after", type=unicode_decoder,
                help=_(u"find page after this item"), metavar='ITEM_ID')
            rsm_page_group.add_argument(
                "-b", "--before", dest="rsm_before", type=unicode_decoder,
                help=_(u"find page before this item"), metavar='ITEM_ID')
            rsm_page_group.add_argument(
                "--index", dest="rsm_index", type=int,
                help=_(u"index of the page to retrieve"))


            # MAM

            pubsub_group.add_argument(
                "-f", "--filter", dest='mam_filters', type=unicode_decoder, nargs=2,
                action='append', default=[], help=_(u"MAM filters to use"),
                metavar=(u"FILTER_NAME", u"VALUE")
            )

            # Order-By

            # TODO: order-by should be a list to handle several levels of ordering
            #       but this is not yet done in SàT (and not really useful with
            #       current specifications, as only "creation" and "modification" are
            #       available)
            pubsub_group.add_argument(
                "-o", "--order-by", choices=[C.ORDER_BY_CREATION,
                                             C.ORDER_BY_MODIFICATION],
                help=_(u"how items should be ordered"))

        if not flags.all_used:
            raise exceptions.InternalError('unknown flags: {flags}'.format(flags=u', '.join(flags.unused)))
        if defaults:
            raise exceptions.InternalError('unused defaults: {defaults}'.format(defaults=defaults))

        return parent

    def add_parser_options(self):
        self.parser.add_argument('--version', action='version', version=("%(name)s %(version)s %(copyleft)s" % {'name': PROG_NAME, 'version': self.version, 'copyleft': COPYLEFT}))

    def register_output(self, type_, name, callback, description="", default=False):
        if type_ not in C.OUTPUT_TYPES:
            log.error(u"Invalid output type {}".format(type_))
            return
        self._outputs[type_][name] = {'callback': callback,
                                      'description': description
                                     }
        if default:
            if type_ in self.default_output:
                self.disp(_(u'there is already a default output for {}, ignoring new one').format(type_))
            else:
                self.default_output[type_] = name


    def parse_output_options(self):
        options = self.command.args.output_opts
        options_dict = {}
        for option in options:
            try:
                key, value = option.split(u'=', 1)
            except ValueError:
                key, value = option, None
            options_dict[key.strip()] = value.strip() if value is not None else None
        return options_dict

    def check_output_options(self, accepted_set, options):
        if not accepted_set.issuperset(options):
            self.disp(u"The following output options are invalid: {invalid_options}".format(
                invalid_options = u', '.join(set(options).difference(accepted_set))),
                error=True)
            self.quit(C.EXIT_BAD_ARG)

    def import_plugins(self):
        """Automaticaly import commands and outputs in jp

        looks from modules names cmd_*.py in jp path and import them
        """
        path = os.path.dirname(sat_frontends.jp.__file__)
        # XXX: outputs must be imported before commands as they are used for arguments
        for type_, pattern in ((C.PLUGIN_OUTPUT, 'output_*.py'), (C.PLUGIN_CMD, 'cmd_*.py')):
            modules = (os.path.splitext(module)[0] for module in map(os.path.basename, iglob(os.path.join(path, pattern))))
            for module_name in modules:
                module_path = "sat_frontends.jp." + module_name
                try:
                    module = import_module(module_path)
                    self.import_plugin_module(module, type_)
                except ImportError as e:
                    self.disp(_(u"Can't import {module_path} plugin, ignoring it: {msg}".format(
                    module_path = module_path,
                    msg = e)), error=True)
                except exceptions.CancelError:
                    continue
                except exceptions.MissingModule as e:
                    self.disp(_(u"Missing module for plugin {name}: {missing}".format(
                        name = module_path,
                        missing = e)), error=True)


    def import_plugin_module(self, module, type_):
        """add commands or outpus from a module to jp

        @param module: module containing commands or outputs
        @param type_(str): one of C_PLUGIN_*
        """
        try:
            class_names =  getattr(module, '__{}__'.format(type_))
        except AttributeError:
            log.disp(_(u"Invalid plugin module [{type}] {module}").format(type=type_, module=module), error=True)
            raise ImportError
        else:
            for class_name in class_names:
                cls = getattr(module, class_name)
                cls(self)

    def get_xmpp_uri_from_http(self, http_url):
        """parse HTML page at http(s) URL, and looks for xmpp: uri"""
        if http_url.startswith('https'):
            scheme = u'https'
        elif http_url.startswith('http'):
            scheme = u'http'
        else:
            raise exceptions.InternalError(u'An HTTP scheme is expected in this method')
        self.disp(u"{scheme} URL found, trying to find associated xmpp: URI".format(scheme=scheme.upper()),1)
        # HTTP URL, we try to find xmpp: links
        try:
            from lxml import etree
        except ImportError:
            self.disp(u"lxml module must be installed to use http(s) scheme, please install it with \"pip install lxml\"", error=True)
            self.quit(1)
        import urllib2
        parser = etree.HTMLParser()
        try:
            root = etree.parse(urllib2.urlopen(http_url), parser)
        except etree.XMLSyntaxError as e:
            self.disp(_(u"Can't parse HTML page : {msg}").format(msg=e))
            links = []
        else:
            links = root.xpath("//link[@rel='alternate' and starts-with(@href, 'xmpp:')]")
        if not links:
            self.disp(u'Could not find alternate "xmpp:" URI, can\'t find associated XMPP PubSub node/item', error=True)
            self.quit(1)
        xmpp_uri = links[0].get('href')
        return xmpp_uri

    def parse_pubsub_args(self):
        if self.args.pubsub_url is not None:
            url = self.args.pubsub_url

            if url.startswith('http'):
                # http(s) URL, we try to retrieve xmpp one from there
                url = self.get_xmpp_uri_from_http(url)

            try:
                uri_data = uri.parseXMPPUri(url)
            except ValueError:
                self.parser.error(_(u'invalid XMPP URL: {url}').format(url=url))
            else:
                if uri_data[u'type'] == 'pubsub':
                    # URL is alright, we only set data not already set by other options
                    if not self.args.service:
                        self.args.service = uri_data[u'path']
                    if not self.args.node:
                        self.args.node = uri_data[u'node']
                    uri_item = uri_data.get(u'item')
                    if uri_item:
                        # there is an item in URI
                        # we use it only if item is not already set
                        # and item_last is not used either
                        try:
                            item = self.args.item
                        except AttributeError:
                            try:
                                items = self.args.items
                            except AttributeError:
                                self.disp(_(u"item specified in URL but not needed in command, ignoring it"), error=True)
                            else:
                                if not items:
                                    self.args.items = [uri_item]
                        else:
                            if not item:
                                try:
                                    item_last = self.args.item_last
                                except AttributeError:
                                    item_last = False
                                if not item_last:
                                    self.args.item = uri_item
                else:
                    self.parser.error(_(u'XMPP URL is not a pubsub one: {url}').format(url=url))
        flags = self.args._cmd._pubsub_flags
        # we check required arguments here instead of using add_arguments' required option
        # because the required argument can be set in URL
        if C.SERVICE in flags and not self.args.service:
            self.parser.error(_(u"argument -s/--service is required"))
        if C.NODE in flags and not self.args.node:
            self.parser.error(_(u"argument -n/--node is required"))
        if C.ITEM in flags and not self.args.item:
            self.parser.error(_(u"argument -i/--item is required"))

        # FIXME: mutually groups can't be nested in a group and don't support title
        #        so we check conflict here. This may be fixed in Python 3, to be checked
        try:
            if self.args.item and self.args.item_last:
                self.parser.error(_(u"--item and --item-last can't be used at the same time"))
        except AttributeError:
            pass

        try:
            max_items = self.args.max
            rsm_max = self.args.rsm_max
        except AttributeError:
            pass
        else:
            # we need to set a default value for max, but we need to know if we want
            # to use pubsub's max or RSM's max. The later is used if any RSM or MAM
            # argument is set
            if max_items is None and rsm_max is None:
                to_check = ('mam_filters', 'rsm_max', 'rsm_after', 'rsm_before',
                            'rsm_index')
                if any((getattr(self.args, name) for name in to_check)):
                    # we use RSM
                    self.args.rsm_max = 10
                else:
                    # we use pubsub without RSM
                    self.args.max = 10
            if self.args.max is None:
                self.args.max = C.NO_LIMIT

    def run(self, args=None, namespace=None):
        self.args = self.parser.parse_args(args, namespace=None)
        if self.args._cmd._use_pubsub:
            self.parse_pubsub_args()
        try:
            self.args._cmd.run()
            if self._need_loop or self._auto_loop:
                self._start_loop()
        except KeyboardInterrupt:
            self.disp(_("User interruption: good bye"))

    def _start_loop(self):
        self.loop = JPLoop()
        self.loop.run()

    def stop_loop(self):
        try:
            self.loop.quit()
        except AttributeError:
            pass

    def confirmOrQuit(self, message, cancel_message=_(u"action cancelled by user")):
        """Request user to confirm action, and quit if he doesn't"""

        res = raw_input("{} (y/N)? ".format(message))
        if res not in ("y", "Y"):
            self.disp(cancel_message)
            self.quit(C.EXIT_USER_CANCELLED)

    def quitFromSignal(self, errcode=0):
        """Same as self.quit, but from a signal handler

        /!\: return must be used after calling this method !
        """
        assert self._need_loop
        # XXX: python-dbus will show a traceback if we exit in a signal handler
        # so we use this little timeout trick to avoid it
        self.loop.call_later(0, self.quit, errcode)

    def quit(self, errcode=0):
        # first the onQuitCallbacks
        try:
            callbacks_list = self._onQuitCallbacks
        except AttributeError:
            pass
        else:
            for callback, args, kwargs in callbacks_list:
                callback(*args, **kwargs)

        self.stop_loop()
        sys.exit(errcode)

    def check_jids(self, jids):
        """Check jids validity, transform roster name to corresponding jids

        @param profile: profile name
        @param jids: list of jids
        @return: List of jids

        """
        names2jid = {}
        nodes2jid = {}

        for contact in self.bridge.getContacts(self.profile):
            jid_s, attr, groups = contact
            _jid = JID(jid_s)
            try:
                names2jid[attr["name"].lower()] = jid_s
            except KeyError:
                pass

            if _jid.node:
                nodes2jid[_jid.node.lower()] = jid_s

        def expand_jid(jid):
            _jid = jid.lower()
            if _jid in names2jid:
                expanded = names2jid[_jid]
            elif _jid in nodes2jid:
                expanded = nodes2jid[_jid]
            else:
                expanded = jid
            return expanded

        def check(jid):
            if not jid.is_valid:
                log.error (_("%s is not a valid JID !"), jid)
                self.quit(1)

        dest_jids=[]
        try:
            for i in range(len(jids)):
                dest_jids.append(expand_jid(jids[i]))
                check(dest_jids[i])
        except AttributeError:
            pass

        return dest_jids

    def connect_profile(self, callback):
        """ Check if the profile is connected and do it if requested

        @param callback: method to call when profile is connected
        @exit: - 1 when profile is not connected and --connect is not set
               - 1 when the profile doesn't exists
               - 1 when there is a connection error
        """
        # FIXME: need better exit codes

        def cant_connect(failure):
            log.error(_(u"Can't connect profile: {reason}").format(reason=failure))
            self.quit(1)

        def cant_start_session(failure):
            log.error(_(u"Can't start {profile}'s session: {reason}").format(profile=self.profile, reason=failure))
            self.quit(1)

        self.profile = self.bridge.profileNameGet(self.args.profile)

        if not self.profile:
            log.error(_("The profile [{profile}] doesn't exist").format(profile=self.args.profile))
            self.quit(1)

        try:
            start_session = self.args.start_session
        except AttributeError:
            pass
        else:
            if start_session:
                self.bridge.profileStartSession(self.args.pwd, self.profile, lambda __: callback(), cant_start_session)
                self._auto_loop = True
                return
            elif not self.bridge.profileIsSessionStarted(self.profile):
                if not self.args.connect:
                    log.error(_(u"Session for [{profile}] is not started, please start it before using jp, or use either --start-session or --connect option").format(profile=self.profile))
                    self.quit(1)
            elif not getattr(self.args, "connect", False):
                callback()
                return


        if not hasattr(self.args, 'connect'):
            # a profile can be present without connect option (e.g. on profile creation/deletion)
            return
        elif self.args.connect is True:  # if connection is asked, we connect the profile
            self.bridge.connect(self.profile, self.args.pwd, {}, lambda __: callback(), cant_connect)
            self._auto_loop = True
            return
        else:
            if not self.bridge.isConnected(self.profile):
                log.error(_(u"Profile [{profile}] is not connected, please connect it before using jp, or use --connect option").format(profile=self.profile))
                self.quit(1)

        callback()

    def get_full_jid(self, param_jid):
        """Return the full jid if possible (add main resource when find a bare jid)"""
        _jid = JID(param_jid)
        if not _jid.resource:
            #if the resource is not given, we try to add the main resource
            main_resource = self.bridge.getMainResource(param_jid, self.profile)
            if main_resource:
                return "%s/%s" % (_jid.bare, main_resource)
        return param_jid


class CommandBase(object):

    def __init__(self, host, name, use_profile=True, use_output=False, extra_outputs=None,
                       need_connect=None, help=None, **kwargs):
        """Initialise CommandBase

        @param host: Jp instance
        @param name(unicode): name of the new command
        @param use_profile(bool): if True, add profile selection/connection commands
        @param use_output(bool, unicode): if not False, add --output option
        @param extra_outputs(dict): list of command specific outputs:
            key is output name ("default" to use as main output)
            value is a callable which will format the output (data will be used as only argument)
            if a key already exists with normal outputs, the extra one will be used
        @param need_connect(bool, None): True if profile connection is needed
            False else (profile session must still be started)
            None to set auto value (i.e. True if use_profile is set)
            Can't be set if use_profile is False
        @param help(unicode): help message to display
        @param **kwargs: args passed to ArgumentParser
            use_* are handled directly, they can be:
            - use_progress(bool): if True, add progress bar activation option
                progress* signals will be handled
            - use_verbose(bool): if True, add verbosity option
            - use_pubsub(bool): if True, add pubsub options
                mandatory arguments are controlled by pubsub_req
            - use_draft(bool): if True, add draft handling options
            ** other arguments **
            - pubsub_flags(iterable[unicode]): tuple of flags to set pubsub options, can be:
                C.SERVICE: service is required
                C.NODE: node is required
                C.ITEM: item is required
                C.SINGLE_ITEM: only one item is allowed
        @attribute need_loop(bool): to set by commands when loop is needed
        """
        self.need_loop = False # to be set by commands when loop is needed
        try: # If we have subcommands, host is a CommandBase and we need to use host.host
            self.host = host.host
        except AttributeError:
            self.host = host

        # --profile option
        parents = kwargs.setdefault('parents', set())
        if use_profile:
            #self.host.parents['profile'] is an ArgumentParser with profile connection arguments
            if need_connect is None:
                need_connect = True
            parents.add(self.host.parents['profile' if need_connect else 'profile_session'])
        else:
            assert need_connect is None
        self.need_connect = need_connect
        # from this point, self.need_connect is None if connection is not needed at all
        # False if session starting is needed, and True if full connection is needed

        # --output option
        if use_output:
            if extra_outputs is None:
                extra_outputs = {}
            self.extra_outputs = extra_outputs
            if use_output == True:
                use_output = C.OUTPUT_TEXT
            assert use_output in C.OUTPUT_TYPES
            self._output_type = use_output
            output_parent = argparse.ArgumentParser(add_help=False)
            choices = set(self.host.getOutputChoices(use_output))
            choices.update(extra_outputs)
            if not choices:
                raise exceptions.InternalError("No choice found for {} output type".format(use_output))
            try:
                default = self.host.default_output[use_output]
            except KeyError:
                if u'default' in choices:
                    default = u'default'
                elif u'simple' in choices:
                    default = u'simple'
                else:
                    default = list(choices)[0]
            output_parent.add_argument('--output', '-O', choices=sorted(choices), default=default, help=_(u"select output format (default: {})".format(default)))
            output_parent.add_argument('--output-option', '--oo', type=unicode_decoder, action="append", dest='output_opts', default=[], help=_(u"output specific option"))
            parents.add(output_parent)
        else:
            assert extra_outputs is None

        self._use_pubsub = kwargs.pop('use_pubsub', False)
        if self._use_pubsub:
            flags = kwargs.pop('pubsub_flags', [])
            defaults = kwargs.pop('pubsub_defaults', {})
            parents.add(self.host.make_pubsub_group(flags, defaults))
            self._pubsub_flags = flags

        # other common options
        use_opts = {k:v for k,v in kwargs.iteritems() if k.startswith('use_')}
        for param, do_use in use_opts.iteritems():
            opt=param[4:] # if param is use_verbose, opt is verbose
            if opt not in self.host.parents:
                raise exceptions.InternalError(u"Unknown parent option {}".format(opt))
            del kwargs[param]
            if do_use:
                parents.add(self.host.parents[opt])

        self.parser = host.subparsers.add_parser(name, help=help, **kwargs)
        if hasattr(self, "subcommands"):
            self.subparsers = self.parser.add_subparsers()
        else:
            self.parser.set_defaults(_cmd=self)
        self.add_parser_options()

    @property
    def args(self):
        return self.host.args

    @property
    def profile(self):
        return self.host.profile

    @property
    def verbosity(self):
        return self.host.verbosity

    @property
    def progress_id(self):
        return self.host.progress_id

    @progress_id.setter
    def progress_id(self, value):
        self.host.progress_id = value

    def progressStartedHandler(self, uid, metadata, profile):
        if profile != self.profile:
            return
        if self.progress_id is None:
            # the progress started message can be received before the id
            # so we keep progressStarted signals in cache to replay they
            # when the progress_id is received
            cache_data = (self.progressStartedHandler, uid, metadata, profile)
            try:
                self.host.progress_ids_cache.append(cache_data)
            except AttributeError:
                self.host.progress_ids_cache = [cache_data]
        else:
            if self.host.watch_progress and uid == self.progress_id:
                self.onProgressStarted(metadata)
                self.host.loop.call_later(PROGRESS_DELAY, self.progressUpdate)

    def progressFinishedHandler(self, uid, metadata, profile):
        if profile != self.profile:
            return
        if uid == self.progress_id:
            try:
                self.host.pbar.finish()
            except AttributeError:
                pass
            self.onProgressFinished(metadata)
            if self.host.quit_on_progress_end:
                self.host.quitFromSignal()

    def progressErrorHandler(self, uid, message, profile):
        if profile != self.profile:
            return
        if uid == self.progress_id:
            if self.args.progress:
                self.disp('') # progress is not finished, so we skip a line
            if self.host.quit_on_progress_end:
                self.onProgressError(message)
                self.host.quitFromSignal(1)

    def progressUpdate(self):
        """This method is continualy called to update the progress bar"""
        data = self.host.bridge.progressGet(self.progress_id, self.profile)
        if data:
            try:
                size = data['size']
            except KeyError:
                self.disp(_(u"file size is not known, we can't show a progress bar"), 1, error=True)
                return False
            if self.host.pbar is None:
                #first answer, we must construct the bar
                self.host.pbar = progressbar.ProgressBar(max_value=int(size),
                                                         widgets=[_(u"Progress: "),progressbar.Percentage(),
                                                         " ",
                                                         progressbar.Bar(),
                                                         " ",
                                                         progressbar.FileTransferSpeed(),
                                                         " ",
                                                         progressbar.ETA()])
                self.host.pbar.start()

            self.host.pbar.update(int(data['position']))

        elif self.host.pbar is not None:
            return False

        self.onProgressUpdate(data)

        return True

    def onProgressStarted(self, metadata):
        """Called when progress has just started

        can be overidden by a command
        @param metadata(dict): metadata as sent by bridge.progressStarted
        """
        self.disp(_(u"Operation started"), 2)

    def onProgressUpdate(self, metadata):
        """Method called on each progress updata

        can be overidden by a command to handle progress metadata
        @para metadata(dict): metadata as returned by bridge.progressGet
        """
        pass

    def onProgressFinished(self, metadata):
        """Called when progress has just finished

        can be overidden by a command
        @param metadata(dict): metadata as sent by bridge.progressFinished
        """
        self.disp(_(u"Operation successfully finished"), 2)

    def onProgressError(self, error_msg):
        """Called when a progress failed

        @param error_msg(unicode): error message as sent by bridge.progressError
        """
        self.disp(_(u"Error while doing operation: {}").format(error_msg), error=True)

    def disp(self, msg, verbosity=0, error=False, no_lf=False):
        return self.host.disp(msg, verbosity, error, no_lf)

    def output(self, data):
        try:
            output_type = self._output_type
        except AttributeError:
            raise exceptions.InternalError(_(u'trying to use output when use_output has not been set'))
        return self.host.output(output_type, self.args.output, self.extra_outputs, data)

    def exitCb(self, msg=None):
        """generic callback for success

        optionally print a message, and quit
        msg(None, unicode): if not None, print this message
        """
        if msg is not None:
            self.disp(msg)
        self.host.quit(C.EXIT_OK)

    def errback(self, failure_, msg=None, exit_code=C.EXIT_ERROR):
        """generic callback for errbacks

        display failure_ then quit with generic error
        @param failure_: arguments returned by errback
        @param msg(unicode, None): message template
            use {} if you want to display failure message
        @param exit_code(int): shell exit code
        """
        if msg is None:
            msg = _(u"error: {}")
        self.disp(msg.format(failure_), error=True)
        self.host.quit(exit_code)

    def getPubsubExtra(self, extra=None):
        """Helper method to compute extra data from pubsub arguments

        @param extra(None, dict): base extra dict, or None to generate a new one
        @return (dict): dict which can be used directly in the bridge for pubsub
        """
        if extra is None:
            extra = {}
        else:
            intersection = {C.KEY_ORDER_BY}.intersection(extra.keys())
            if intersection:
                raise exceptions.ConflictError(
                    u"given extra dict has conflicting keys with pubsub keys "
                    u"{intersection}".format(intersection=intersection))

        # RSM

        for attribute in (u'max', u'after', u'before', 'index'):
            key = u'rsm_' + attribute
            if key in extra:
                raise exceptions.ConflictError(
                    u"This key already exists in extra: u{key}".format(key=key))
            value = getattr(self.args, key, None)
            if value is not None:
                extra[key] = unicode(value)

        # MAM

        if hasattr(self.args, u'mam_filters'):
            for key, value in self.args.mam_filters:
                key = u'filter_' + key
                if key in extra:
                    raise exceptions.ConflictError(
                        u"This key already exists in extra: u{key}".format(key=key))
                extra[key] = value

        # Order-By

        try:
            order_by = self.args.order_by
        except AttributeError:
            pass
        else:
            if order_by is not None:
                extra[C.KEY_ORDER_BY] = self.args.order_by
        return extra

    def add_parser_options(self):
        try:
            subcommands = self.subcommands
        except AttributeError:
            # We don't have subcommands, the class need to implements add_parser_options
            raise NotImplementedError

        # now we add subcommands to ourself
        for cls in subcommands:
            cls(self)

    def run(self):
        """this method is called when a command is actually run

        It set stuff like progression callbacks and profile connection
        You should not overide this method: you should call self.start instead
        """
        # we keep a reference to run command, it may be useful e.g. for outputs
        self.host.command = self
        # host._need_loop is set here from our current value and not before
        # as the need_loop decision must be taken only by then running command
        self.host._need_loop = self.need_loop

        try:
            show_progress = self.args.progress
        except AttributeError:
            # the command doesn't use progress bar
            pass
        else:
            if show_progress:
                self.host.watch_progress = True
            # we need to register the following signal even if we don't display the progress bar
            self.host.bridge.register_signal("progressStarted", self.progressStartedHandler)
            self.host.bridge.register_signal("progressFinished", self.progressFinishedHandler)
            self.host.bridge.register_signal("progressError", self.progressErrorHandler)

        if self.need_connect is not None:
             self.host.connect_profile(self.connected)
        else:
            self.start()

    def connected(self):
        """this method is called when profile is connected (or session is started)

        this method is only called when use_profile is True
        most of time you should override self.start instead of this method, but if loop
        if not always needed depending on your arguments, you may override this method,
        but don't forget to call the parent one (i.e. this one) after self.need_loop is set
        """
        if not self.need_loop:
            self.host.stop_loop()
        self.start()

    def start(self):
        """This is the starting point of the command, this method should be overriden

        at this point, profile are connected if needed
        """
        pass


class CommandAnswering(CommandBase):
    """Specialised commands which answer to specific actions

    to manage action_types answer,
    """
    action_callbacks = {} # XXX: set managed action types in a dict here:
                          # key is the action_type, value is the callable
                          # which will manage the answer. profile filtering is
                          # already managed when callback is called

    def __init__(self, *args, **kwargs):
        super(CommandAnswering, self).__init__(*args, **kwargs)
        self.need_loop = True

    def onActionNew(self, action_data, action_id, security_limit, profile):
        if profile != self.profile:
            return
        try:
            action_type = action_data['meta_type']
        except KeyError:
            try:
                xml_ui = action_data["xmlui"]
            except KeyError:
                pass
            else:
                self.onXMLUI(xml_ui)
        else:
            try:
                callback = self.action_callbacks[action_type]
            except KeyError:
                pass
            else:
                callback(action_data, action_id, security_limit, profile)

    def onXMLUI(self, xml_ui):
        """Display a dialog received from the backend.

        @param xml_ui (unicode): dialog XML representation
        """
        # FIXME: we temporarily use ElementTree, but a real XMLUI managing module
        #        should be available in the future
        # TODO: XMLUI module
        ui = ET.fromstring(xml_ui.encode('utf-8'))
        dialog = ui.find("dialog")
        if dialog is not None:
            self.disp(dialog.findtext("message"), error=dialog.get("level") == "error")

    def connected(self):
        """Auto reply to confirmations requests"""
        self.need_loop = True
        super(CommandAnswering, self).connected()
        self.host.bridge.register_signal("actionNew", self.onActionNew)
        actions = self.host.bridge.actionsGet(self.profile)
        for action_data, action_id, security_limit in actions:
            self.onActionNew(action_data, action_id, security_limit, self.profile)
