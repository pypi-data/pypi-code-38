import os

ANDROID = {
    'APK': {
        'name': "appname",
        'version': '0.1', #https://developer.android.com/studio/publish/versioning.html
        # 'numericversion': '1',
        'package': 'com.radiant.appname',
        'icon': '/static/images/icon.png',
        'statusbarcolor': '#000000',
        'navigationbarcolor': '#000000',
        'orientation': 'portrait', #other options: 'sensor' and 'landscape'
        'intent_filters': None,
    },

    'APP': {
        'multithread': False,
        'logs': 'logs',  #directory for save logs, by default is in the app folder
    },

    'BRYTHON': False,

    'MAIN_SRC': '',

    'ANDROID': {
        'ARCH': 'armeabi-v7a',
        'SDK': '/absolute/path/to/android-sdk-linux', #https://developer.android.com/studio/index.html
        'API': '26',
        'CRYSTAX_NDK': '/absolute/path/to/crystax-ndk-10.3.2', #https://www.crystax.net/en/download
        'CRYSTAX_NDK_API': '19', #https://www.crystax.net/en/download
        #'CRYSTAX_NDK_VERSION': '10.3.2',
        'BUILD_TOOL': 'ant',  #ant, gradle
    },

    #for sign and release packages
    'KEY': {
        'RELEASE_KEYSTORE': 'radiant.keystore',
        'RELEASE_KEYALIAS': 'radiant',
        'RELEASE_KEYSTORE_PASSWD': 'radiant', #use your own password
        'RELEASE_KEYALIAS_PASSWD': 'radiant',
    },

    #splash screen for your app, this is static html, NOT a Django view
    'SPLASH': {
        'static_html': False, #path to .html, resources must be added with just file name, i.e background-image: url("splash.png");
        'resources': [], #list of files used in the static html, i.e ['static/images/splash.png']
    },

    #for localserver
    'PORT': '8888',
    'IP': '127.0.0.1',

    #extra permissions for app https://developer.android.com/reference/android/Manifest.permission.html
    'PERMISSIONS': [], #list of permissions, i.e ['BLUETOOTH', 'BLUETOOTH_ADMIN', 'CAMERA']
    '__PERMISSIONS': ['INTERNET', 'WRITE_EXTERNAL_STORAGE', 'READ_EXTERNAL_STORAGE'],

    'ADD_JARS': [],
    'ADD_AARS': [],

    #sandbox for python-for-andoid operations
    'BUILD': {
        'build': os.path.expanduser('~/.radiant'), #where the magic happens
        'recipes': None, #path for user recipes parent directory, check http://python-for-android.readthedocs.io/en/latest/recipes/
        'whitelist': None, #for python-for-android users
        'requirements': [], #extra python packages to install, differents to ['python3crystax', 'pyjnius', 'django', 'sqlite3', 'djangoforandroid']
        '__requirements': ['python3', 'libffi', 'django', 'sqlite3', 'radiant', 'pytz', 'pyjnius', 'djangostaticprecompiler'],
        '__requirements_brython': ['python3', 'openssl', 'libffi', 'radiant', 'pyjnius', 'static', 'pystache'],
        'exclude_dirs': [], #list of RELATIVE paths, this directories will not be included in the final .apk
        'include_exts': [], #list of extensions to include in final .apk, i.e ['py', 'png', 'sqlite3', 'html', 'css', 'js'], if empty then add all files
        'exclude_files': [], #list of RELATIVE paths, this files will not be included in the final .apk
    },

    'THEME': {
        'colors': False,
    },
}
