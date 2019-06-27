#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import Console
import logging
from . import config
import shutil
import re

class Module():
    """
    Module class
    """

    DESC_SKEL = """{
    "icon": "help-circle-outline",
    "global": {
        "js": ["%(MODULE_NAME)s.service.js"],
        "html": [],
        "css": []
    },
    "config": {
        "js": ["%(MODULE_NAME)s.config.js"],
        "html": ["%(MODULE_NAME)s.config.html"]
    }
}
    """
    ANGULAR_SERVICE_SKEL = """/**
 * %(MODULE_NAME_CAPITALIZED)s service
 * Handle %(MODULE_NAME)s application requests
 */
var %(MODULE_NAME)sService = function(\$q, \$rootScope, rpcService) {
    var self = this;

    /**
     * Catch x.x.x events
     */
    \$rootScope.\$on('x.x.x', function(event, uuid, params) {
    });
}
    
var RaspIot = angular.module('RaspIot');
RaspIot.service('%(MODULE_NAME)sService', ['\$q', '\$rootScope', 'rpcService', %(MODULE_NAME)sService]);
    """
    ANGULAR_CONTROLLER_SKEL = """/**
 * %(MODULE_NAME_CAPITALIZED)s config directive
 * Handle %(MODULE_NAME)s application configuration
 */
var %(MODULE_NAME)sConfigDirective = function(\$rootScope, %(MODULE_NAME)sService, raspiotService) {

    var %(MODULE_NAME)sConfigController = function() {
        var self = this;

        /**
         * Init controller
         */
        self.init = function() {
            // TODO
        };
    };

    var %(MODULE_NAME)sConfigLink = function(scope, element, attrs, controller) {
        controller.init();
    };

    return {
        templateUrl: '%(MODULE_NAME)s.config.html',
        replace: true,
        scope: true,
        controller: %(MODULE_NAME)sConfigController,
        controllerAs: '%(MODULE_NAME)sCtl',
        link: %(MODULE_NAME)sConfigLink
    };
};

var RaspIot = angular.module('RaspIot');
RaspIot.directive('%(MODULE_NAME)sConfigDirective', ['\$rootScope', '%(MODULE_NAME)sService', 'raspiotService', %(MODULE_NAME)sConfigDirective]);
    """
    ANGULAR_CONTROLLER_TEMPLATE_SKEL = """<div layout="column" layout-padding ng-cloak>

    <md-list>
    </md-list>

</div>
    """
    PYTHON_MODULE_SKEL = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.utils import MissingParameter, InvalidParameter, CommandError
from raspiot.raspiot import RaspIotModule

class %(MODULE_NAME_CAPITALIZED)s(RaspIotModule):
    \\"\\"\\"
    %(MODULE_NAME_CAPITALIZED)s application
    \\"\\"\\"
    MODULE_AUTHOR = u'TODO'
    MODULE_VERSION = u'0.0.0'
    MODULE_DEPS = []
    MODULE_DESCRIPTION = u'TODO'
    MODULE_LONGDESCRIPTION = u'TODO'
    MODULE_TAGS = []
    MODULE_CATEGORY = u'TODO'
    MODULE_COUNTRY = None
    MODULE_URLINFO = None
    MODULE_URLHELP = None
    MODULE_URLSITE = None
    MODULE_URLBUGS = None

    MODULE_CONFIG_FILE = u'%(MODULE_NAME)s.conf'
    DEFAULT_CONFIG = {}

    def __init__(self, bootstrap, debug_enabled):
        \\"\\"\\"
        Constructor

        Params:
            bootstrap (dict): bootstrap objects
            debug_enabled: debug status
        \\"\\"\\"
        RaspIotModule.__init__(self, bootstrap, debug_enabled)

    def _configure(self):
        \\"\\"\\"
        Configure module
        \\"\\"\\"
        # launch here custom thread or action that takes time to process
        pass

    def _stop(self):
        \\"\\"\\"
        Stop module
        \\"\\"\\"
        # stop here your custom threads or close external connections
        pass

    def event_received(self, event):
        \\"\\"\\"
        Event received

        Params:
            event (MessageRequest): event data
        \\"\\"\\"
        # execute here actions when you receive an event:
        #  - on time event => cron task
        #  - on alert event => send email or push message
        #  - ...
        pass
    """
    TEST_DEFAULT = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
import sys
sys.path.append('../')
from backend.%(MODULE_NAME)s import %(MODULE_NAME_CAPITALIZED)s
from raspiot.utils import InvalidParameter, MissingParameter, CommandError, Unauthorized
from raspiot.libs.tests import session

class Test%(MODULE_NAME_CAPITALIZED)s(unittest.TestCase):

    def setUp(self):
        self.session = session.Session(logging.CRITICAL)
        #next line instanciates your module, overwriting all useful stuff to isolate your module for tests
        self.module = self.session.setup(%(MODULE_NAME_CAPITALIZED)s)

    def tearDown(self):
        #clean session
        self.session.clean()

    #write your tests here defining functions starting with \"test_\"
    #see official documentation https://docs.python.org/2.7/library/unittest.html
    #def test_my_test(self):
    #   ...

#do not remove code below, otherwise test won't run
if __name__ == '__main__':
    unittest.main()
    """
    DOCS_CONF_PY = """# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.abspath('../'))

project = u''
copyright = u''
author = u''
version = u''
release = u''
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
]
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = [u'_build', 'Thumbs.db', '.DS_Store']
pygments_style = None
html_theme = 'sphinx_rtd_theme'
todo_include_todos = True
autodoc_default_options = { 
    'undoc-members': True,
    'private-members': False,
}
def setup(app):
    app.add_css_file('cleep.css')
    """
    #'exclude-members': '__init__,_stop,_configure'
    DOCS_INDEX_RST = """Welcome to %(MODULE_NAME_CAPITALIZED)s's documentation!
=================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   source/modules

Indices and tables
==================

* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`
    """
    DOCS_CLEEP_CSS = """.wy-nav-side {
    background: #90a4ae !important;
}
.wy-side-nav-search {
    background: #607d8b !important;
}
.rst-content dl:not(.docutils) dt {
    color: #d32f2f !important;
    background: #ffcdd2 !important;
    border-top: solid 3px #b71c1c !important;
 }
.rst-content dl:not(.docutils) dl dt {
    border: none !important;
    border-left: solid 3px #d32f2f !important;
    background: #eceff1 !important;
    color: #607d8b !important;
}
a:visited, a:hover {
    color: #d32f2f;
}
a {
    color: #000000;
}
a:visited.icon.icon-home, a.icon.icon-home {
    color: #FFFFFF !important;
}
a:hover.icon.icon-home {
    color: #d32f2f;
}
.wy-menu-vertical header,.wy-menu-vertical p.caption {
    color: #000000;
}
    """

    def __init__(self):
        """
        Constructor
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, module_name):
        """
        Create module skeleton

        Args:
            module_name (string): module name
        """
        module_name = re.sub('[^0-9a-zA-Z]+', '', module_name).lstrip('0123456789').lower()
        self.logger.debug('Module name to create: %s' % module_name)
        path = os.path.join(config.MODULES_SRC, module_name)
        self.logger.info('Creating module "%s" in "%s"' % (module_name, path))
        
        if os.path.exists(path):
            self.logger.error('Module "%s" already exists in "%s"' % (module_name, path))
            return False

        templates = {
            'ANGULAR_SERVICE': self.ANGULAR_SERVICE_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'ANGULAR_CONTROLLER': self.ANGULAR_CONTROLLER_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'ANGULAR_CONTROLLER_TEMPLATE': self.ANGULAR_CONTROLLER_TEMPLATE_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DESC': self.DESC_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'PYTHON_MODULE': self.PYTHON_MODULE_SKEL % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'TEST_DEFAULT': self.TEST_DEFAULT % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DOCS_CONF_PY': self.DOCS_CONF_PY % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DOCS_INDEX_RST': self.DOCS_INDEX_RST % {'MODULE_NAME': module_name, 'MODULE_NAME_CAPITALIZED': module_name.capitalize()},
            'DOCS_CLEEP_CSS': self.DOCS_CLEEP_CSS,
        }

        c = Console()
        resp = c.command("""
/bin/mkdir -p "%(MODULE_DIR)s/backend"
/usr/bin/touch "%(MODULE_DIR)s/backend/__init__.py"
/bin/echo "%(PYTHON_MODULE)s" > %(MODULE_DIR)s/backend/%(MODULE_NAME)s.py
/bin/mkdir -p "%(MODULE_DIR)s/frontend"
/bin/echo "%(DESC)s" > %(MODULE_DIR)s/frontend/desc.json
/bin/echo "%(ANGULAR_SERVICE)s" > %(MODULE_DIR)s/frontend/%(MODULE_NAME)s.service.js
/bin/echo "%(ANGULAR_CONTROLLER)s" > %(MODULE_DIR)s/frontend/%(MODULE_NAME)s.config.js
/bin/echo "%(ANGULAR_CONTROLLER_TEMPLATE)s" > %(MODULE_DIR)s/frontend/%(MODULE_NAME)s.config.html
/bin/mkdir -p "%(MODULE_DIR)s/tests"
/usr/bin/touch "%(MODULE_DIR)s/tests/__init__.py"
/bin/echo "%(TEST_DEFAULT)s" > %(MODULE_DIR)s/tests/test_%(MODULE_NAME)s.py
/bin/mkdir -p "%(MODULE_DIR)s/docs"
/bin/echo "%(DOCS_CONF_PY)s" > %(MODULE_DIR)s/docs/conf.py
/bin/echo "%(DOCS_INDEX_RST)s" > %(MODULE_DIR)s/docs/index.rst
/bin/mkdir -p "%(MODULE_DIR)s/docs/_static"
/bin/echo "%(DOCS_CLEEP_CSS)s" > %(MODULE_DIR)s/docs/_static/cleep.css
        """ % {
            'MODULE_DIR': path,
            'MODULE_NAME': module_name,
            'DESC': templates['DESC'],
            'ANGULAR_SERVICE': templates['ANGULAR_SERVICE'],
            'ANGULAR_CONTROLLER': templates['ANGULAR_CONTROLLER'],
            'ANGULAR_CONTROLLER_TEMPLATE': templates['ANGULAR_CONTROLLER_TEMPLATE'],
            'PYTHON_MODULE': templates['PYTHON_MODULE'],
            'TEST_DEFAULT': templates['TEST_DEFAULT'],
            'DOCS_CONF_PY': templates['DOCS_CONF_PY'],
            'DOCS_INDEX_RST': templates['DOCS_INDEX_RST'],
            'DOCS_CLEEP_CSS': templates['DOCS_CLEEP_CSS'],
        }, 10)
        if resp['error'] or resp['killed']:
            self.logger.error('Error occured while pulling repository: %s' % ('killed' if resp['killed'] else resp['stderr']))
            shutil.rmtree(path)
            return False
        
        self.logger.info('Done')
        return True

