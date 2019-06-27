#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP client
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

try:
    from xdg import BaseDirectory
    from os.path import expanduser, realpath
except ImportError:
    BaseDirectory = None
import sat


class Const(object):

    ## Application ##
    APP_NAME = u"Salut à Toi"
    APP_NAME_SHORT = u"SàT"
    APP_NAME_FILE = u"sat"
    APP_NAME_FULL = u"{name_short} ({name})".format(
        name_short=APP_NAME_SHORT, name=APP_NAME
    )
    APP_VERSION = (
        sat.__version__
    )  # Please add 'D' at the end of version in sat/VERSION for dev versions
    APP_RELEASE_NAME = u"La Commune"
    APP_URL = u"https://salut-a-toi.org"

    ## Runtime ##
    PLUGIN_EXT = "py"
    HISTORY_SKIP = u"skip"

    ## Main config ##
    DEFAULT_BRIDGE = "dbus"

    ## Protocol ##
    XMPP_C2S_PORT = 5222
    XMPP_MAX_RETRIES = None
    # default port used on Prosody, may differ on other servers
    XMPP_COMPONENT_PORT = 5347

    ## Parameters ##
    NO_SECURITY_LIMIT = -1  #  FIXME: to rename
    SECURITY_LIMIT_MAX = 0
    INDIVIDUAL = "individual"
    GENERAL = "general"
    # General parameters
    HISTORY_LIMIT = "History"
    SHOW_OFFLINE_CONTACTS = "Offline contacts"
    SHOW_EMPTY_GROUPS = "Empty groups"
    # Parameters related to connection
    FORCE_SERVER_PARAM = "Force server"
    FORCE_PORT_PARAM = "Force port"
    # Parameters related to encryption
    PROFILE_PASS_PATH = ("General", "Password")
    MEMORY_CRYPTO_NAMESPACE = "crypto"  # for the private persistent binary dict
    MEMORY_CRYPTO_KEY = "personal_key"
    # Parameters for static blog pages
    # FIXME: blog constants should not be in core constants
    STATIC_BLOG_KEY = "Blog page"
    STATIC_BLOG_PARAM_TITLE = "Title"
    STATIC_BLOG_PARAM_BANNER = "Banner"
    STATIC_BLOG_PARAM_KEYWORDS = "Keywords"
    STATIC_BLOG_PARAM_DESCRIPTION = "Description"

    ## Menus ##
    MENU_GLOBAL = "GLOBAL"
    MENU_ROOM = "ROOM"
    MENU_SINGLE = "SINGLE"
    MENU_JID_CONTEXT = "JID_CONTEXT"
    MENU_ROSTER_JID_CONTEXT = "ROSTER_JID_CONTEXT"
    MENU_ROSTER_GROUP_CONTEXT = "MENU_ROSTER_GROUP_CONTEXT"
    MENU_ROOM_OCCUPANT_CONTEXT = "MENU_ROOM_OCCUPANT_CONTEXT"

    ## Profile and entities ##
    PROF_KEY_NONE = "@NONE@"
    PROF_KEY_DEFAULT = "@DEFAULT@"
    PROF_KEY_ALL = "@ALL@"
    ENTITY_ALL = "@ALL@"
    ENTITY_ALL_RESOURCES = "@ALL_RESOURCES@"
    ENTITY_MAIN_RESOURCE = "@MAIN_RESOURCE@"
    ENTITY_CAP_HASH = "CAP_HASH"
    ENTITY_TYPE = "TYPE"

    ## Roster jids selection ##
    PUBLIC = "PUBLIC"
    ALL = (
        "ALL"
    )  # ALL means all known contacts, while PUBLIC means everybody, known or not
    GROUP = "GROUP"
    JID = "JID"

    ## Messages ##
    MESS_TYPE_INFO = "info"
    MESS_TYPE_CHAT = "chat"
    MESS_TYPE_ERROR = "error"
    MESS_TYPE_GROUPCHAT = "groupchat"
    MESS_TYPE_HEADLINE = "headline"
    MESS_TYPE_NORMAL = "normal"
    MESS_TYPE_AUTO = "auto"  # magic value to let the backend guess the type
    MESS_TYPE_STANDARD = (
        MESS_TYPE_CHAT,
        MESS_TYPE_ERROR,
        MESS_TYPE_GROUPCHAT,
        MESS_TYPE_HEADLINE,
        MESS_TYPE_NORMAL,
    )
    MESS_TYPE_ALL = MESS_TYPE_STANDARD + (MESS_TYPE_INFO, MESS_TYPE_AUTO)

    MESS_EXTRA_INFO = u"info_type"
    EXTRA_INFO_DECR_ERR = u"DECRYPTION_ERROR"
    EXTRA_INFO_ENCR_ERR = u"ENCRYPTION_ERROR"

    # encryption is a key for plugins
    MESS_KEY_ENCRYPTION = u"ENCRYPTION"
    # encrypted is a key for frontends
    MESS_KEY_ENCRYPTED = u"encrypted"
    MESS_KEY_TRUSTED = u"trusted"

    ## Chat ##
    CHAT_ONE2ONE = "one2one"
    CHAT_GROUP = "group"

    ## Presence ##
    PRESENCE_UNAVAILABLE = "unavailable"
    PRESENCE_SHOW_AWAY = "away"
    PRESENCE_SHOW_CHAT = "chat"
    PRESENCE_SHOW_DND = "dnd"
    PRESENCE_SHOW_XA = "xa"
    PRESENCE_SHOW = "show"
    PRESENCE_STATUSES = "statuses"
    PRESENCE_STATUSES_DEFAULT = "default"
    PRESENCE_PRIORITY = "priority"

    ## Common namespaces ##
    NS_XML = "http://www.w3.org/XML/1998/namespace"
    NS_CLIENT = "jabber:client"
    NS_FORWARD = "urn:xmpp:forward:0"
    NS_DELAY = "urn:xmpp:delay"
    NS_XHTML = "http://www.w3.org/1999/xhtml"

    ## Common XPath ##

    IQ_GET = '/iq[@type="get"]'
    IQ_SET = '/iq[@type="set"]'

    ## Directories ##

    # directory for components specific data
    COMPONENTS_DIR = u"components"
    CACHE_DIR = u"cache"
    # files in file dir are stored for long term
    # files dir is global, i.e. for all profiles
    FILES_DIR = u"files"
    # FILES_LINKS_DIR is a directory where files owned by a specific profile
    # are linked to the global files directory. This way the directory can be
    #  shared per profiles while keeping global directory where identical files
    # shared between different profiles are not duplicated.
    FILES_LINKS_DIR = u"files_links"
    # FILES_TMP_DIR is where profile's partially transfered files are put.
    # Once transfer is completed, they are moved to FILES_DIR
    FILES_TMP_DIR = u"files_tmp"

    ## Configuration ##
    if (
        BaseDirectory
    ):  # skipped when xdg module is not available (should not happen in backend)
        if "org.salutatoi.cagou" in BaseDirectory.__file__:
            # FIXME: hack to make config read from the right location on Android
            # TODO: fix it in a more proper way

            # we need to use Android API to get downloads directory
            import os.path
            from jnius import autoclass

            Environment = autoclass("android.os.Environment")

            BaseDirectory = None
            DEFAULT_CONFIG = {
                "local_dir": "/data/data/org.salutatoi.cagou/app",
                "media_dir": "/data/data/org.salutatoi.cagou/files/app/media",
                # FIXME: temporary location for downloads, need to call API properly
                "downloads_dir": os.path.join(
                    Environment.getExternalStoragePublicDirectory(
                        Environment.DIRECTORY_DOWNLOADS
                    ).getAbsolutePath(),
                    APP_NAME_FILE,
                ),
                "pid_dir": "%(local_dir)s",
                "log_dir": "%(local_dir)s",
            }
            CONFIG_FILES = [
                "/data/data/org.salutatoi.cagou/files/app/android/"
                + APP_NAME_FILE
                + ".conf"
            ]
        else:
            import os
            CONFIG_PATHS = (
                ["/etc/", "~/", "~/.", "", "."]
                + [
                    "%s/" % path
                    for path in list(BaseDirectory.load_config_paths(APP_NAME_FILE))
                ]
            )

            if os.getenv('FLATPAK_ID'):
                # for Flatpak, the conf can't be set in /etc or $HOME, so we have
                # to add /app
                CONFIG_PATHS.append('/app/')

            ## Configuration ##
            DEFAULT_CONFIG = {
                "media_dir": "/usr/share/" + APP_NAME_FILE + "/media",
                "local_dir": BaseDirectory.save_data_path(APP_NAME_FILE),
                "downloads_dir": "~/Downloads/" + APP_NAME_FILE,
                "pid_dir": "%(local_dir)s",
                "log_dir": "%(local_dir)s",
            }

            # List of the configuration filenames sorted by ascending priority
            CONFIG_FILES = [
                realpath(expanduser(path) + APP_NAME_FILE + ".conf")
                for path in CONFIG_PATHS
            ]

    ## Templates ##
    TEMPLATE_TPL_DIR = u"templates"
    TEMPLATE_THEME_DEFAULT = u"default"
    TEMPLATE_STATIC_DIR = u"static"
    KEY_LANG = u"lang"  # templates i18n

    ## Plugins ##

    # PLUGIN_INFO keys
    # XXX: we use PI instead of PLUG_INFO which would normally be used
    #      to make the header more readable
    PI_NAME = u"name"
    PI_IMPORT_NAME = u"import_name"
    PI_MAIN = u"main"
    PI_HANDLER = u"handler"
    PI_TYPE = (
        u"type"
    )  #  FIXME: should be types, and should handle single unicode type or tuple of types (e.g. "blog" and "import")
    PI_MODES = u"modes"
    PI_PROTOCOLS = u"protocols"
    PI_DEPENDENCIES = u"dependencies"
    PI_RECOMMENDATIONS = u"recommendations"
    PI_DESCRIPTION = u"description"
    PI_USAGE = u"usage"

    # Types
    PLUG_TYPE_XEP = "XEP"
    PLUG_TYPE_MISC = "MISC"
    PLUG_TYPE_EXP = "EXP"
    PLUG_TYPE_SEC = "SEC"
    PLUG_TYPE_SYNTAXE = "SYNTAXE"
    PLUG_TYPE_BLOG = "BLOG"
    PLUG_TYPE_IMPORT = "IMPORT"
    PLUG_TYPE_ENTRY_POINT = "ENTRY_POINT"

    # Modes
    PLUG_MODE_CLIENT = "client"
    PLUG_MODE_COMPONENT = "component"
    PLUG_MODE_DEFAULT = (PLUG_MODE_CLIENT,)
    PLUG_MODE_BOTH = (PLUG_MODE_CLIENT, PLUG_MODE_COMPONENT)

    # names of widely used plugins
    TEXT_CMDS = "TEXT-COMMANDS"

    # PubSub event categories
    PS_PEP = "PEP"
    PS_MICROBLOG = "MICROBLOG"

    # PubSub
    PS_PUBLISH = "publish"
    PS_RETRACT = "retract"  # used for items
    PS_DELETE = "delete"  # used for nodes
    PS_ITEM = "item"
    PS_ITEMS = "items"  # Can contain publish and retract items
    PS_EVENTS = (PS_ITEMS, PS_DELETE)

    ## MESSAGE/NOTIFICATION LEVELS ##

    LVL_INFO = "info"
    LVL_WARNING = "warning"
    LVL_ERROR = "error"

    ## XMLUI ##
    XMLUI_WINDOW = "window"
    XMLUI_POPUP = "popup"
    XMLUI_FORM = "form"
    XMLUI_PARAM = "param"
    XMLUI_DIALOG = "dialog"
    XMLUI_DIALOG_CONFIRM = "confirm"
    XMLUI_DIALOG_MESSAGE = "message"
    XMLUI_DIALOG_NOTE = "note"
    XMLUI_DIALOG_FILE = "file"
    XMLUI_DATA_ANSWER = "answer"
    XMLUI_DATA_CANCELLED = "cancelled"
    XMLUI_DATA_TYPE = "type"
    XMLUI_DATA_MESS = "message"
    XMLUI_DATA_LVL = "level"
    XMLUI_DATA_LVL_INFO = LVL_INFO
    XMLUI_DATA_LVL_WARNING = LVL_WARNING
    XMLUI_DATA_LVL_ERROR = LVL_ERROR
    XMLUI_DATA_LVL_DEFAULT = XMLUI_DATA_LVL_INFO
    XMLUI_DATA_LVLS = (XMLUI_DATA_LVL_INFO, XMLUI_DATA_LVL_WARNING, XMLUI_DATA_LVL_ERROR)
    XMLUI_DATA_BTNS_SET = "buttons_set"
    XMLUI_DATA_BTNS_SET_OKCANCEL = "ok/cancel"
    XMLUI_DATA_BTNS_SET_YESNO = "yes/no"
    XMLUI_DATA_BTNS_SET_DEFAULT = XMLUI_DATA_BTNS_SET_OKCANCEL
    XMLUI_DATA_FILETYPE = "filetype"
    XMLUI_DATA_FILETYPE_FILE = "file"
    XMLUI_DATA_FILETYPE_DIR = "dir"
    XMLUI_DATA_FILETYPE_DEFAULT = XMLUI_DATA_FILETYPE_FILE

    ## Logging ##
    LOG_LVL_DEBUG = "DEBUG"
    LOG_LVL_INFO = "INFO"
    LOG_LVL_WARNING = "WARNING"
    LOG_LVL_ERROR = "ERROR"
    LOG_LVL_CRITICAL = "CRITICAL"
    LOG_LEVELS = (
        LOG_LVL_DEBUG,
        LOG_LVL_INFO,
        LOG_LVL_WARNING,
        LOG_LVL_ERROR,
        LOG_LVL_CRITICAL,
    )
    LOG_BACKEND_STANDARD = "standard"
    LOG_BACKEND_TWISTED = "twisted"
    LOG_BACKEND_BASIC = "basic"
    LOG_BACKEND_CUSTOM = "custom"
    LOG_BASE_LOGGER = "root"
    LOG_TWISTED_LOGGER = "twisted"
    LOG_OPT_SECTION = "DEFAULT"  # section of sat.conf where log options should be
    LOG_OPT_PREFIX = "log_"
    # (option_name, default_value) tuples
    LOG_OPT_COLORS = (
        "colors",
        "true",
    )  # true for auto colors, force to have colors even if stdout is not a tty, false for no color
    LOG_OPT_TAINTS_DICT = (
        "levels_taints_dict",
        {
            LOG_LVL_DEBUG: ("cyan",),
            LOG_LVL_INFO: (),
            LOG_LVL_WARNING: ("yellow",),
            LOG_LVL_ERROR: ("red", "blink", r"/!\ ", "blink_off"),
            LOG_LVL_CRITICAL: ("bold", "red", "Guru Meditation ", "normal_weight"),
        },
    )
    LOG_OPT_LEVEL = ("level", "info")
    LOG_OPT_FORMAT = ("fmt", "%(message)s")  # similar to logging format.
    LOG_OPT_LOGGER = ("logger", "")  # regex to filter logger name
    LOG_OPT_OUTPUT_SEP = "//"
    LOG_OPT_OUTPUT_DEFAULT = "default"
    LOG_OPT_OUTPUT_MEMORY = "memory"
    LOG_OPT_OUTPUT_MEMORY_LIMIT = 50
    LOG_OPT_OUTPUT_FILE = "file"  # file is implicit if only output
    LOG_OPT_OUTPUT = (
        "output",
        LOG_OPT_OUTPUT_SEP + LOG_OPT_OUTPUT_DEFAULT,
    )  # //default = normal output (stderr or a file with twistd), path/to/file for a file (must be the first if used), //memory for memory (options can be put in parenthesis, e.g.: //memory(500) for a 500 lines memory)

    ## action constants ##
    META_TYPE_FILE = "file"
    META_TYPE_OVERWRITE = "overwrite"

    ## HARD-CODED ACTIONS IDS (generated with uuid.uuid4) ##
    AUTHENTICATE_PROFILE_ID = u"b03bbfa8-a4ae-4734-a248-06ce6c7cf562"
    CHANGE_XMPP_PASSWD_ID = u"878b9387-de2b-413b-950f-e424a147bcd0"

    ## Text values ##
    BOOL_TRUE = "true"
    BOOL_FALSE = "false"

    ## Special values used in bridge methods calls ##
    HISTORY_LIMIT_DEFAULT = -1
    HISTORY_LIMIT_NONE = -2

    ## Progress error special values ##
    PROGRESS_ERROR_DECLINED = u"declined"  #  session has been declined by peer user

    ## Files ##
    FILE_TYPE_DIRECTORY = "directory"
    FILE_TYPE_FILE = "file"

    ## Permissions management ##
    ACCESS_PERM_READ = u"read"
    ACCESS_PERM_WRITE = u"write"
    ACCESS_PERMS = {ACCESS_PERM_READ, ACCESS_PERM_WRITE}
    ACCESS_TYPE_PUBLIC = u"public"
    ACCESS_TYPE_WHITELIST = u"whitelist"
    ACCESS_TYPES = (ACCESS_TYPE_PUBLIC, ACCESS_TYPE_WHITELIST)

    ## Common data keys ##
    KEY_THUMBNAILS = u"thumbnails"
    KEY_PROGRESS_ID = u"progress_id"

    ## Common extra keys/values ##
    KEY_ORDER_BY = u"order_by"

    ORDER_BY_CREATION = u'creation'
    ORDER_BY_MODIFICATION = u'modification'

    # internationalisation
    DEFAULT_LOCALE = u"en_GB"

    ## Misc ##
    SAVEFILE_DATABASE = APP_NAME_FILE + ".db"
    IQ_SET = '/iq[@type="set"]'
    ENV_PREFIX = "SAT_"  # Prefix used for environment variables
    IGNORE = "ignore"
    NO_LIMIT = -1  # used in bridge when a integer value is expected
    DEFAULT_MAX_AGE = 1209600  # default max age of cached files, in seconds
    HASH_SHA1_EMPTY = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    STANZA_NAMES = (u"iq", u"message", u"presence")

    # Stream Hooks
    STREAM_HOOK_SEND = u"send"
    STREAM_HOOK_RECEIVE = u"receive"

    @classmethod
    def LOG_OPTIONS(cls):
        """Return options checked for logs"""
        # XXX: we use a classmethod so we can use Const inheritance to change default options
        return (
            cls.LOG_OPT_COLORS,
            cls.LOG_OPT_TAINTS_DICT,
            cls.LOG_OPT_LEVEL,
            cls.LOG_OPT_FORMAT,
            cls.LOG_OPT_LOGGER,
            cls.LOG_OPT_OUTPUT,
        )

    @classmethod
    def bool(cls, value):
        """@return (bool): bool value for associated constant"""
        assert isinstance(value, basestring)
        return value.lower() in (cls.BOOL_TRUE, "1", "yes", "on")

    @classmethod
    def boolConst(cls, value):
        """@return (str): constant associated to bool value"""
        assert isinstance(value, bool)
        return cls.BOOL_TRUE if value else cls.BOOL_FALSE
