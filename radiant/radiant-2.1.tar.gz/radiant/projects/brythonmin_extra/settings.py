import os
from android import APPNAME, PACKAGENAME


#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['BASE_DIR'] = BASE_DIR

from radiant.framework.brython.settings import *


ANDROID = {

    'APK': {
        'name': APPNAME,
        'version': '1.0',
        # 'numericversion': '1',
        # 'package': 'com.radiant.{}'.format(PACKAGENAME),
        'package': 'com.radiant.autobuild',
        'icon': os.path.join(BASE_DIR, 'android', 'static', 'images', 'icon.png'),
        'statusbarcolor': '#00675b',
        'navigationbarcolor': '#00675b',
        'orientation': 'portrait',
    },


    'BRYTHON': {
        'module': os.path.join(BASE_DIR, 'android', 'core'),
        'class': 'Brython',

    },

    'APP': {
        'multithread': False,
        #'logs': '/storage/emulated/0',
    },


    'PORT': '1234',
    'IP': 'localhost',

    'PERMISSIONS': [],

    'BUILD': {
        'requirements': ['static'],
        'exclude_dirs': ['radiant', '.hg', 'brython_app', 'docs'],
        'include_exts': ['py', 'png', 'sqlite3', 'html', 'css', 'js', 'svg', 'ttf', 'eot', 'woff', 'woff2', 'otf', 'xml'],
        },

    'ANDROID': {
        'ARCH': 'armeabi-v7a',
        'SDK': '/home/yeison/Development/android/sdk-tools-linux',
        'API': '26',
        'CRYSTAX_NDK': '/home/yeison/Development/android/crystax-ndk-10.3.2',
        'CRYSTAX_NDK_VERSION': '10.3.2',
        'BUILD_TOOL': 'ant',
    },

    'SPLASH': {
        'static_html': os.path.join(BASE_DIR, 'android', 'templates', 'splash.html'),
        'resources': [os.path.join(BASE_DIR, 'android', 'static', 'images', 'icon.png'),
                      os.path.join(BASE_DIR, 'android', 'static', 'images', 'splash.svg'),
                     ],
    },

    'THEME': {
        #https://material.io/tools/color/#!/?view.left=0&view.right=0&primary.color=4DB6AC&secondary.color=FFAB00&primary.text.color=ffffff&secondary.text.color=ffffff
        'colors': os.path.join(BASE_DIR, 'android', 'colors.xml'),
    },

}

TEMPLATE_DEBUG = True
os.environ['TEMPLATE_DEBUG'] = str(TEMPLATE_DEBUG)