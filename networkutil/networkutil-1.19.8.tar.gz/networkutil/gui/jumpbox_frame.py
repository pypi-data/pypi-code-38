# encoding: utf-8

import getpass
from uiutil.tk_names import W, NORMAL, showerror
from paramiko import AuthenticationException

import logging_helper
from .._metadata import __version__, __authorshort__, __module_name__
from ..jumpbox import JumpBox
from ..resources import templates, schema
from uiutil.frame.frame import BaseFrame
from uiutil.window.root import RootWindow
from uiutil.widget.button import Button
from uiutil.widget.entry import TextEntry
from uiutil.widget.combobox import Combobox
from configurationutil import Configuration, cfg_params

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
JUMPBOX_CFG = u'jumpbox_hosts'
TEMPLATE = templates.jumpbox

# Constants for accessing config items
JB_ADDRESS = u'host'
JB_PORT = u'port'
JB_ELEV_USER = u'elevated_user'

# TODO: Add UI to configure the jump hosts (perhaps this could come from a base device frame?)


class JumpboxException(Exception):
    pass


class JumpboxFrame(BaseFrame):

    BUTTON_WIDTH = 20
    TEXT_FIELD_WIDTH = 22
    LABEL_WIDTH = 20
    COMBO_WIDTH = 21

    def __init__(self,
                 jb_class=JumpBox,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.jb = None
        self.jb_class = jb_class

        self.jumpbox_config = Configuration()

        # Register configuration
        self.jumpbox_config.register(config=JUMPBOX_CFG,
                                     config_type=cfg_params.CONST.json,
                                     template=TEMPLATE,
                                     schema=schema.jumpbox)

        self.build_jumpbox_frame()

    def build_jumpbox_frame(self):

        self.label(text=u'Username:',
                   width=self.LABEL_WIDTH,
                   sticky=W)

        self.label(text=u'Password:',
                   width=self.LABEL_WIDTH,
                   column=self.column.next(),
                   sticky=W)

        self.label(text=u'Jumpbox:',
                   width=self.LABEL_WIDTH,
                   column=self.column.next(),
                   sticky=W)

        self.username = TextEntry(value=getpass.getuser(),
                                  width=self.TEXT_FIELD_WIDTH,
                                  row=self.row.next(),
                                  column=self.column.start())

        self.password = TextEntry(width=self.TEXT_FIELD_WIDTH,
                                  show=u'*',
                                  column=self.column.next())

        self.jumpbox = Combobox(width=self.COMBO_WIDTH,
                                postcommand=self.populate_jumpbox_list,
                                column=self.column.next(),
                                tooltip=u'Select the jumpbox to connect to...')

        self.populate_jumpbox_list()

        self.connect_button = Button(state=NORMAL,
                                     value=u'Connect',
                                     width=self.BUTTON_WIDTH,
                                     command=self.connect,
                                     row=self.row.next(),
                                     tooltip=u'Connect to Jumpbox')
        self.nice_grid()

    def populate_jumpbox_list(self):

        jumpbox_list = []

        for row in self.jumpbox_config[JUMPBOX_CFG]:
            jumpbox_list.append(row)

        logging.debug(jumpbox_list)

        self.jumpbox.values = jumpbox_list

        if jumpbox_list:
            self.jumpbox.value = jumpbox_list[0]

    def connect(self):

        jb_name = self.jumpbox.value

        key = u'{c}.{name}'.format(c=JUMPBOX_CFG,
                                   name=jb_name)

        try:
            jb_config = self.jumpbox_config[key]

        except LookupError:
            raise JumpboxException(u'Could not find jumpbox in config!')

        try:
            self.jb = self.jb_class(host=jb_config[JB_ADDRESS],
                                    username=self.username.value,
                                    password=self.password.value,
                                    elevated_username=jb_config[JB_ELEV_USER],
                                    port=int(jb_config[JB_PORT]))

            self.connect_button.value = u'Disconnect'
            self.connect_button.config(command=self.disconnect)

            self.jb.register_observer(self)

            self.notify_observers(jumpbox=self.jb)

        except AuthenticationException as err:
            logging.warning(err)
            showerror(title=u'Authentication Error',
                      message=err,
                      parent=self)

        except Exception as err:
            logging.exception(err)

    def disconnect(self):

        if self.jb:
            try:
                self.jb.disconnect()
                self.jb = None
                self.connect_button.value = u'Connect'
                self.connect_button.config(command=self.connect)

                self.notify_observers(jumpbox=self.jb)

            except Exception as err:
                logging.exception(err)

    def notification(self,
                     notifier,
                     **params):

        jumpbox = params.get(u'jumpbox')

        if jumpbox is not None:

            # Check for disconnection!
            if not jumpbox.jumpbox_connected:
                self.jb = None
                self.connect_button.value = u'Connect'
                self.connect_button.config(command=self.connect)

                self.notify_observers(jumpbox=self.jb)


class ExampleJumpboxFrame(RootWindow):

    def __init__(self, *args, **kwargs):
        super(ExampleJumpboxFrame, self).__init__(*args, **kwargs)

    def _draw_widgets(self):

        self.title(u"Example Jumpbox Frame")

        self.drm = JumpboxFrame(parent=self._main_frame)
