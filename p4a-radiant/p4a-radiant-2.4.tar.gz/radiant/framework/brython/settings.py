"""
Brython Framework: Default settings
===================================

"""

import os


BASE_DIR = os.environ.get('BASE_DIR', '.')
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4dxpyfy=!&rp6jif-(75@uy6n-_wemlfyhogxerq9o8^vh3i@g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'static_precompiler',

    'radiant.builder',
    'radiant.framework',  # optional, for urls support

    # 'android',
    os.environ['APP'],
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#ROOT_URLCONF = 'brythonapp.urls'
ROOT_URLCONF = 'radiant.framework.brython.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],

            'libraries':{
                'try_to_include': 'radiant.framework.templatetags.custom_include',
                'compile_static': 'static_precompiler.templatetags.compile_static',
            },

        },
    },
]

#WSGI_APPLICATION = 'brythonapp.wsgi.application'
WSGI_APPLICATION = 'radiant.framework.brython.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'


STATIC_ROOT = os.path.join(BASE_DIR, 'resources')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, os.environ['APP'], 'views'),
]

APPEND_SLASH = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'static_precompiler.finders.StaticPrecompilerFinder',
)

# if HOST == 'arch':
STATIC_PRECOMPILER_COMPILERS = (
    'static_precompiler.compilers.CoffeeScript',
    # 'static_precompiler.compilers.Babel',
    # 'static_precompiler.compilers.Handlebars',
    'static_precompiler.compilers.SASS',
    'static_precompiler.compilers.SCSS',
    # 'static_precompiler.compilers.LESS',
    # 'static_precompiler.compilers.Stylus',
)


# STATIC_PRECOMPILER_COMPILERS = (
    #('static_precompiler.compilers.CoffeeScript', {"executable": "/usr/bin/coffee"}),
    #('static_precompiler.compilers.SCSS', {"executable": os.path.expanduser("~/.gem/ruby/2.4.0/bin/sass")}),
# )

#STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True
