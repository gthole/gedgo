import os
import sys
project_root = os.path.dirname(__file__)
# Django settings for gedgo project.

DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gedgo',
        'USER': 'gedgo',
        'PASSWORD': 'gedgo',
        'HOST': 'db',
        'PORT': '',
    }
}

ALLOWED_HOSTS = []
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = '/app/files/default/'
MEDIA_URL = '/gedgo/media/'

STATIC_ROOT = ''
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'not_a_secret'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(project_root, 'gedgo/templates'),
            os.path.join(project_root, 'gedgo/templates/default'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'
# WSGI_APPLICATION = 'wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'gedgo'
)

CACHES = {
    'research_preview': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/app/files/research_preview',
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    }
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Just send emails to the console.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SERVER_EMAIL = ['noreply@example.com']

GEDGO_ALLOW_FILE_UPLOADS = True
GEDGO_SENDFILE_HEADER = 'X-Accel-Redirect'
GEDGO_SENDFILE_PREFIX = '/protected/'
GEDGO_SITE_TITLE = 'My Genealogy Site'
GEDGO_REDIS_SERVER = 'redis'
GEDGO_RESEARCH_FILE_STORAGE = 'gedgo.storages.FileSystemSearchableStorage'
GEDGO_RESEARCH_FILE_ROOT = '/app/files/gedcom/'
GEDGO_GEDCOM_FILE_STORAGE = 'gedgo.storages.FileSystemSearchableStorage'
GEDGO_GEDCOM_FILE_ROOT = '/app/files/research/'
GEDGO_SHOW_RESEARCH_FILES = True

BROKER_BACKEND = 'redis'
BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ["json"]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if 'test' in sys.argv:
    DATABASES['default']['USER'] = 'root'
    DATABASES['default']['PASSWORD'] = 'docker'
else:
    try:
        from settings_local import *  # noqa
    except ImportError:
        pass
