import os

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['BASE_DIR'] = BASE_DIR
os.environ['APP'] = '{{PACKAGENAME}}'

from radiant.framework.brython.settings import *


ANDROID = {

    'APK': {
        'name': "{{APPNAME}}",
        'version': '1.0',
        # 'numericversion': '1',
        'package': 'com.radiant.{{PACKAGENAME}}',
        'icon': os.path.join(BASE_DIR, '{{PACKAGENAME}}', 'static', 'images', 'icon.png'),
        # 'statusbarcolor': '#00675b',
        # 'navigationbarcolor': '#00675b',
        'statusbarcolor': '#00675b',
        'navigationbarcolor': '#00675b',
        'orientation': 'portrait',
    },


    'BRYTHON': {
        'module': os.path.join(BASE_DIR, '{{PACKAGENAME}}', 'core'),
        'class': 'Brython',

    },

    'APP': {
        'multithread': False,
        # 'logs': '/storage/emulated/0',
    },


    'PORT': '1234',
    'IP': 'localhost',

    'PERMISSIONS': [],

    'BUILD': {
        'requirements': ['static'],
        'exclude_dirs': ['radiant', '.hg', 'brython_app'],
        'include_exts': ['py', 'png', 'sqlite3', 'html', 'css', 'js', 'svg', 'ttf', 'eot', 'woff', 'woff2', 'otf', 'xml'],
    },

    'ANDROID': {
        'ARCH': 'armeabi-v7a',
        'SDK': '/path/to/sdk-tools-linux',
        'API': '26',
        'CRYSTAX_NDK': '/path/to/crystax-ndk-10.3.2',
        'CRYSTAX_NDK_VERSION': '10.3.2',
        'BUILD_TOOL': 'ant',
    },

    'KEY': {
        'RELEASE_KEYSTORE': os.path.join(BASE_DIR, 'YeisonCardona.upload.jks'),
        'RELEASE_KEYALIAS': 'radiant',
        'RELEASE_KEYSTORE_PASSWD': 'radiant',  # use your own password
        'RELEASE_KEYALIAS_PASSWD': 'radiant',
    },

    'SPLASH': {
        'static_html': os.path.join(BASE_DIR, '{{PACKAGENAME}}', 'templates', 'splash.html'),
        'resources': [os.path.join(BASE_DIR, '{{PACKAGENAME}}', 'static', 'images', 'icon.png'),
                      os.path.join(BASE_DIR, '{{PACKAGENAME}}', 'static', 'images', 'splash.svg'),
                      ],
    },

    'THEME': {
        # https://material.io/tools/color/#!/?view.left=0&view.right=0&primary.color=4DB6AC&secondary.color=FFAB00&primary.text.color=ffffff&secondary.text.color=ffffff
        'colors': os.path.join(BASE_DIR, 'colors.xml'),
    },

}

TEMPLATE_DEBUG = True
os.environ['TEMPLATE_DEBUG'] = str(TEMPLATE_DEBUG)
