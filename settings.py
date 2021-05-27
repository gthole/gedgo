import os

# Django settings for gedgo project.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/data/db.sqllite',
    }
}

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = '/app/.files/default/'
MEDIA_URL = '/gedgo/media/default/'

STATIC_ROOT = '/static/'
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
            '/app/gedgo/templates',
            '/app/gedgo/templates/default',
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
                'django.template.context_processors.request',
            ],
        },
    },
]


MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'
ASGI_APPLICATION = 'asgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_simple_task',
    'gedgo',
)


CACHES = {
    'research_preview': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/app/.files/research_preview',
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    }
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# BROKER_URL = 'django://'
# CELERY_RESULT_BACKEND = 'djcelery.backends.database'
# CELERY_ACCEPT_CONTENT = ["json"]

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
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


#
# Environment-variable overrides
#

TIME_ZONE = os.environ.get('TIME_ZONE', 'America/New_York')
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')
DEBUG = (os.environ.get('DEBUG') == 'True')
SECRET_KEY = os.environ.get('SECRET_KEY', 'foo')
if os.environ.get('ADMINS'):
    ADMINS = [a.split(':') for a in os.environ['ADMINS'].split(',')]
else:
    ADMINS = []
MANAGERS = ADMINS

#
# Gedgo-specific settings
#

DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN', None)
GEDGO_ALLOW_FILE_UPLOADS = os.environ.get('GEDGO_ALLOW_FILE_UPLOADS', 'False') == 'True'
GEDGO_SENDFILE_HEADER = os.environ.get('GEDGO_SENDIFLE_HEADER', 'X-Accel-Redirect')
GEDGO_SENDFILE_PREFIX = os.environ.get('GEDOG_SENDFILE_PREFIX', '/protected/')
GEDGO_SITE_TITLE = os.environ.get('GEDGO_SITE_TITLE', 'My Genealogy Site')
GEDGO_RESEARCH_FILE_STORAGE = os.environ.get('GEDGO_RESEARCH_FILE_STORAGE', 'gedgo.storages.FileSystemSearchableStorage')
GEDGO_RESEARCH_FILE_ROOT = os.environ.get('GEDGO_RESEARCH_FILE_ROOT', '/app/.files/gedcom/')
GEDGO_DOCUMENTARY_STORAGE = os.environ.get('GEDGO_DOCUMENTARY_STORAGE', 'gedgo.storages.FileSystemSearchableStorage')
GEDGO_DOCUMENTARY_ROOT = os.environ.get('GEDGO_DOCUMENTARY_ROOT', '/app/.files/documentaries/')
GEDGO_GEDCOM_FILE_STORAGE = os.environ.get('GEDGO_GEDCOM_FILE_STORAGE', 'gedgo.storages.FileSystemSearchableStorage')
GEDGO_GEDCOM_FILE_ROOT = os.environ.get('GEDGO_GEDCOM_FILE_ROOT', '/app/.files/research/')
GEDGO_SHOW_RESEARCH_FILES = os.environ.get('GEDGO_SHOW_RESEARCH_FILES', 'True') == 'True'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SERVER_EMAIL = ['noreply@example.com']
if os.environ.get('EMAIL_HOST') and not DEBUG:
    EMAIL_BACKEND = os.environ.get(
        'EMAIL_BACKEND',
        'django.core.mail.backends.smtp.EmailBackend'
    )
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', EMAIL_HOST_USER)
